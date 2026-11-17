
from src.validation import validate_song_rows
from src.recommender import load_songs_with_report
import csv


def make_song(**overrides):
    """Create a valid sample song for testing."""

    song = {
        "id": "1",
        "title": "Test Song",
        "artist": "Test Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": "0.8",
        "tempo_bpm": "120",
        "valence": "0.7",
        "danceability": "0.6",
        "acousticness": "0.2",
        "popularity": "80",
        "release_decade": "2020s",
        "mood_tags": "happy; energetic",
        "lyrical_theme": "freedom",
        "instrumentation": "piano; drums",
    }

    song.update(overrides)
    return song


def test_valid_song_is_accepted():
    valid, issues = validate_song_rows([make_song()])

    assert len(valid) == 1
    assert len(issues) == 0


def test_invalid_energy_is_excluded():
    valid, issues = validate_song_rows([
        make_song(energy="1.5")
    ])

    assert len(valid) == 0
    assert len(issues) == 1
    assert any("energy" in reason for reason in issues[0]["reasons"])


def test_missing_title_is_excluded():
    valid, issues = validate_song_rows([
        make_song(title="")
    ])

    assert len(valid) == 0
    assert len(issues) == 1
    assert any("title" in reason.lower() for reason in issues[0]["reasons"])


def test_all_records_with_duplicate_ids_are_excluded():
    songs = [
        make_song(id="99", title="First Song"),
        make_song(id="99", title="Second Song"),
    ]

    valid, issues = validate_song_rows(songs)

    assert len(valid) == 0
    assert len(issues) == 2
    assert all(
        any("duplicate" in reason.lower() for reason in issue["reasons"])
        for issue in issues
    )


def test_valid_songs_are_kept_when_another_song_is_invalid():
    songs = [
        make_song(id="1", title="Good Song"),
        make_song(id="2", title="Bad Song", energy="1.5"),
    ]

    valid, issues = validate_song_rows(songs)

    assert len(valid) == 1
    assert valid[0]["title"] == "Good Song"
    assert len(issues) == 1

def test_csv_loader_excludes_invalid_song(tmp_path):
    """The CSV loader should exclude invalid records and report why."""

    csv_path = tmp_path / "songs_test.csv"

    songs = [
        make_song(id="1", title="Good Song"),
        make_song(id="2", title="Bad Song", energy="1.5"),
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=songs[0].keys())
        writer.writeheader()
        writer.writerows(songs)

    valid, issues = load_songs_with_report(str(csv_path))

    assert len(valid) == 1
    assert valid[0]["title"] == "Good Song"
    assert len(issues) == 1
    assert any("energy" in reason for reason in issues[0]["reasons"])