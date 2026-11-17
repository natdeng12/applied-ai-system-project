import json

from src.evaluation_runner import (
    ALL_TEST_CASES,
    TEST_CASES,
    run_case,
    run_evaluation,
    save_report,
    summarize,
)
from src.recommender import load_songs_with_report


DATASET = "data/songs.csv"


def load_dataset():
    songs, _issues = load_songs_with_report(DATASET)
    return songs


def simple_case(**overrides):
    case = {
        "name": "Test Case",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.9},
        "k": 3,
        "expect": {},
    }
    case.update(overrides)
    return case


def failed_check_names(result):
    return {check["check"] for check in result["checks"] if not check["passed"]}


def test_harness_defines_at_least_five_profiles():
    assert len(TEST_CASES) >= 5


def test_all_predefined_profiles_pass_on_real_dataset():
    report = run_evaluation(DATASET)

    assert report["summary"]["overall_passed"] is True, report["summary"]["failed_case_names"]
    assert report["summary"]["case_success_rate"] == 1.0


def test_real_engine_case_passes_core_checks():
    result = run_case(simple_case(expect={"top_genre": "pop"}), load_dataset())

    assert result["passed"] is True
    assert len(result["recommendations"]) == 3


def test_duplicate_recommendations_are_caught():
    songs = load_dataset()

    def duplicate_fn(case, songs, k):
        return [(songs[0], 3.0, "dup")] * k

    result = run_case(simple_case(), songs, recommend_fn=duplicate_fn)

    assert result["passed"] is False
    assert "no_duplicates" in failed_check_names(result)


def test_invalid_scores_are_caught():
    songs = load_dataset()

    def nan_fn(case, songs, k):
        return [(songs[i], float("nan"), "bad score") for i in range(k)]

    result = run_case(simple_case(), songs, recommend_fn=nan_fn)

    assert result["passed"] is False
    assert "scores_finite" in failed_check_names(result)


def test_songs_outside_dataset_are_caught():
    songs = load_dataset()
    fake_song = {"id": 999, "title": "Not A Real Song", "genre": "pop", "mood": "happy", "energy": 0.9}

    def fake_fn(case, songs, k):
        return [(fake_song, 3.0, "made up")]

    result = run_case(simple_case(k=1), songs, recommend_fn=fake_fn)

    assert result["passed"] is False
    assert "songs_in_dataset" in failed_check_names(result)


def test_wrong_count_and_missing_explanations_are_caught():
    songs = load_dataset()

    def short_fn(case, songs, k):
        return [(songs[0], 3.0, "  ")]  # only 1 song, blank explanation

    result = run_case(simple_case(k=3), songs, recommend_fn=short_fn)

    failed = failed_check_names(result)
    assert result["passed"] is False
    assert "returned_requested_count" in failed
    assert "explanations_present" in failed


def test_unsorted_results_are_caught():
    songs = load_dataset()

    def unsorted_fn(case, songs, k):
        return [(songs[0], 1.0, "low"), (songs[1], 3.0, "high")]

    result = run_case(simple_case(k=2), songs, recommend_fn=unsorted_fn)

    assert result["passed"] is False
    assert "sorted_by_score" in failed_check_names(result)


def test_engine_crash_is_reported_as_failure():
    def crashing_fn(case, songs, k):
        raise ValueError("engine exploded")

    result = run_case(simple_case(), load_dataset(), recommend_fn=crashing_fn)

    assert result["passed"] is False
    assert "engine exploded" in result["error"]
    assert "engine_ran_without_error" in failed_check_names(result)


def test_unmet_expectation_fails_the_case():
    # A pop/happy/0.9 user should NOT get a classical song at the top.
    case = simple_case(expect={"top_genre": "classical"})

    result = run_case(case, load_dataset())

    assert result["passed"] is False
    assert "top_genre_matches" in failed_check_names(result)


def test_summary_counts_failures():
    case_results = [
        {"name": "A", "passed": True, "checks": [{"check": "x", "passed": True, "detail": ""}]},
        {"name": "B", "passed": False, "checks": [{"check": "x", "passed": False, "detail": ""}]},
    ]

    summary = summarize(case_results)

    assert summary["passed_cases"] == 1
    assert summary["case_success_rate"] == 0.5
    assert summary["per_check"]["x"] == {"passed": 1, "total": 2}
    assert summary["failed_case_names"] == ["B"]
    assert summary["overall_passed"] is False


def test_empty_run_does_not_count_as_pass():
    assert summarize([])["overall_passed"] is False


def test_cli_exits_with_error_when_profiles_fail(tmp_path):
    # A tiny dataset with only two classical songs cannot satisfy the pop,
    # rock, or lofi expectations, so the harness must report failure.
    import csv

    from src.evaluation_runner import main

    fields = ["id", "title", "artist", "genre", "mood", "energy", "tempo_bpm", "valence",
              "danceability", "acousticness", "popularity", "release_decade", "mood_tags",
              "lyrical_theme", "instrumentation"]
    rows = [
        ["1", "Calm A", "X", "classical", "peaceful", "0.2", "70", "0.3", "0.2", "0.9", "30", "1990s", "calm", "rest", "piano"],
        ["2", "Calm B", "Y", "classical", "peaceful", "0.1", "60", "0.4", "0.1", "0.95", "20", "1990s", "calm", "rest", "strings"],
    ]
    dataset = tmp_path / "tiny.csv"
    with open(dataset, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(rows)

    output = tmp_path / "report.json"
    exit_code = main(["--dataset", str(dataset), "--output", str(output)])

    report = json.loads(output.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert report["summary"]["overall_passed"] is False
    assert report["summary"]["failed_cases"] > 0


def test_saved_report_is_reproducible(tmp_path):
    first = save_report(run_evaluation(DATASET), tmp_path / "first.json")
    second = save_report(run_evaluation(DATASET), tmp_path / "second.json")

    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")
    assert json.loads(first.read_text(encoding="utf-8"))["summary"]["total_cases"] == len(ALL_TEST_CASES)
