
from src.evaluation import validate_recommendations


def make_song(song_id):
    return {
        "id": str(song_id),
        "title": f"Song {song_id}",
    }


def test_valid_recommendations_pass():
    songs = [make_song(1), make_song(2)]

    recommendations = [
        (songs[0], 3.5, "Good genre and mood match"),
        (songs[1], 2.5, "Similar energy"),
    ]

    is_valid, issues = validate_recommendations(
        recommendations, songs, 2
    )

    assert is_valid is True
    assert issues == []


def test_too_many_recommendations_are_rejected():
    songs = [make_song(1), make_song(2), make_song(3)]

    recommendations = [
        (song, 3.0, "Test explanation") for song in songs
    ]

    is_valid, issues = validate_recommendations(
        recommendations, songs, 2
    )

    assert is_valid is False
    assert any("More recommendations" in issue for issue in issues)


def test_duplicate_recommendations_are_rejected():
    song = make_song(1)
    songs = [song]

    recommendations = [
        (song, 3.0, "First recommendation"),
        (song, 3.0, "Duplicate recommendation"),
    ]

    is_valid, issues = validate_recommendations(
        recommendations, songs, 2
    )

    assert is_valid is False
    assert any("Duplicate" in issue for issue in issues)


def test_invalid_scores_are_rejected():
    song = make_song(1)
    songs = [song]

    recommendations = [
        (song, float("nan"), "Test explanation")
    ]

    is_valid, issues = validate_recommendations(
        recommendations, songs, 1
    )

    assert is_valid is False
    assert any("invalid score" in issue for issue in issues)


def test_songs_outside_validated_dataset_are_rejected():
    valid_songs = [make_song(1)]
    invalid_song = make_song(99)

    recommendations = [
        (invalid_song, 3.0, "Test explanation")
    ]

    is_valid, issues = validate_recommendations(
        recommendations, valid_songs, 1
    )

    assert is_valid is False
    assert any("not in the validated dataset" in issue for issue in issues)


def test_missing_explanations_are_rejected():
    song = make_song(1)
    songs = [song]

    recommendations = [
        (song, 3.0, "")
    ]

    is_valid, issues = validate_recommendations(
        recommendations, songs, 1
    )

    assert is_valid is False
    assert any("no explanation" in issue for issue in issues)
