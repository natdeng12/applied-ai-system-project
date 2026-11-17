import pytest

from src.evaluation_runner import SPECIALIZED_TEST_CASES, compare_modes
from src.recommender import load_songs_with_report, recommend_songs, score_song
from src.specialization import (
    SPECIALIZED_PROFILES,
    build_prototype,
    context_bonus,
    recommend_songs_specialized,
)


DATASET = "data/songs.csv"
PREFS = {"genre": "pop", "mood": "happy", "energy": 0.75}


def load_dataset():
    songs, _issues = load_songs_with_report(DATASET)
    return songs


def test_five_profiles_each_have_few_shot_examples():
    assert len(SPECIALIZED_PROFILES) >= 5
    for profile in SPECIALIZED_PROFILES.values():
        assert len(profile["examples"]) >= 2
        assert profile["label"] and profile["description"]


def test_example_songs_are_not_copied_from_the_dataset():
    # The examples are meant to be fictional templates, not catalog songs.
    catalog_titles = {song["title"] for song in load_dataset()}
    for profile in SPECIALIZED_PROFILES.values():
        for example in profile["examples"]:
            assert example["title"] not in catalog_titles


def test_prototype_is_the_average_of_the_examples():
    examples = SPECIALIZED_PROFILES["workout"]["examples"]
    expected_energy = sum(example["energy"] for example in examples) / len(examples)

    prototype = build_prototype("workout")

    assert prototype["averages"]["energy"] == pytest.approx(expected_energy)
    assert "energetic" in prototype["tags"]


def test_unknown_profile_is_rejected():
    with pytest.raises(ValueError):
        recommend_songs_specialized(PREFS, load_dataset(), "not_a_profile", k=5)


def test_invalid_k_is_rejected():
    with pytest.raises(ValueError):
        recommend_songs_specialized(PREFS, load_dataset(), "workout", k=0)


def test_specialized_results_are_valid_and_explained():
    songs = load_dataset()
    results = recommend_songs_specialized(PREFS, songs, "workout", k=5)

    assert len(results) == 5
    ids = [song["id"] for song, _score, _explanation in results]
    assert len(ids) == len(set(ids))
    for _song, _score, explanation in results:
        assert explanation.startswith("[Workout / High Energy mode]")
        assert "Closest example song" in explanation


def test_specialized_score_is_baseline_plus_context_bonus():
    song = load_dataset()[0]
    base_score, _ = score_song(PREFS, song)
    bonus, _ = context_bonus(song, "workout")

    results = recommend_songs_specialized(PREFS, [song], "workout", k=1)

    assert results[0][1] == pytest.approx(base_score + bonus)


def test_context_bonus_rewards_matching_songs():
    songs = {song["title"]: song for song in load_dataset()}

    gym_bonus, _ = context_bonus(songs["Gym Hero"], "workout")
    calm_bonus, _ = context_bonus(songs["Quiet Memories"], "workout")

    assert gym_bonus > calm_bonus


def test_baseline_mode_is_unchanged():
    # Same expectations the baseline had before specialization was added.
    songs = load_dataset()
    rock = recommend_songs({"genre": "rock", "mood": "intense", "energy": 0.88}, songs, k=5)

    assert rock[0][0]["title"] == "Storm Runner"
    assert "mode]" not in rock[0][2]  # baseline explanations have no mode label


def test_specialized_mode_differs_from_baseline_on_at_least_three_profiles():
    comparison = compare_modes(load_dataset())

    assert comparison["profiles_with_different_results"] >= 3
    assert comparison["passed"] is True


def test_specialized_mode_is_deterministic():
    songs = load_dataset()
    case = SPECIALIZED_TEST_CASES[0]

    first = recommend_songs_specialized(case["prefs"], songs, case["profile"], k=5)
    second = recommend_songs_specialized(case["prefs"], songs, case["profile"], k=5)

    assert first == second
