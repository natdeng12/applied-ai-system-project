import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .validation import validate_song_rows
from .evaluation import validate_recommendations
import logging
from .logging_config import setup_logging
logger = setup_logging()


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    Object-oriented interface to the recommendation engine.
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Rank songs using the same scoring rules as recommend_songs().
        """

        if k < 1:
            raise ValueError("k must be at least 1.")

        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }

        song_dicts = [
            {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "tempo_bpm": song.tempo_bpm,
                "valence": song.valence,
                "danceability": song.danceability,
                "acousticness": song.acousticness,
                "popularity": 0,
                "release_decade": "",
                "mood_tags": [],
                "lyrical_theme": "",
                "instrumentation": [],
            }
            for song in self.songs
        ]

        ranked = recommend_songs(user_prefs, song_dicts, k)

        return [
            self.songs[index]
            for index, (song, score, explanation) in enumerate(ranked)
            for index in [
                next(
                    i for i, original in enumerate(self.songs)
                    if original.id == song["id"]
                )
            ]
        ]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """
        Explain why a song was recommended.
        """

        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }

        song_data = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "popularity": 0,
            "release_decade": "",
            "mood_tags": [],
            "lyrical_theme": "",
            "instrumentation": [],
        }

        score, reasons = score_song(user_prefs, song_data)

        return f"{song.title} scored {score:.2f}. " + "; ".join(reasons)


def load_songs_with_report(csv_path: str):
    """
    Load raw CSV records, validate them, and return:
    - valid songs
    - validation issues
    """

    print(f"Loading songs from {csv_path}...")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required_columns = {
            "id", "title", "artist", "genre", "mood",
            "energy", "tempo_bpm", "valence", "danceability",
            "acousticness", "popularity", "release_decade",
            "mood_tags", "lyrical_theme", "instrumentation"
        }

        if reader.fieldnames is None:
            raise ValueError("The CSV file is empty or has no header.")

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"CSV is missing required columns: {', '.join(sorted(missing_columns))}"
            )

        raw_rows = list(reader)

    # Validate records before converting their values.
    valid_rows, issues = validate_song_rows(raw_rows)

    # Convert validated values into the formats used by the recommender.
    songs = []

    for row in valid_rows:
        song = dict(row)
        song["id"] = int(song["id"])
        song["tempo_bpm"] = int(song["tempo_bpm"])
        song["popularity"] = int(song["popularity"])
        songs.append(song)

    return songs, issues


def load_songs(csv_path: str) -> List[Dict]:
    """
    Load and validate songs.
    Keeps the original interface used by src/main.py.
    """

    songs, issues = load_songs_with_report(csv_path)

    if issues:
        print(f"Validation excluded {len(issues)} song(s):")

        for issue in issues:
            print(
                f"Row {issue['row']} | "
                f"ID: {issue['id']} | "
                f"Title: {issue['title']} | "
                f"Reasons: {', '.join(issue['reasons'])}"
            )

    if not songs:
        raise ValueError(
            "No valid songs remain in the dataset. "
            "Please check the CSV file and its validation errors."
        )

    print(f"Successfully loaded {len(songs)} valid songs.")

    return songs


def _clean_list(value) -> List[str]:
    """Turn a list (or a semicolon-separated string) into lowercase, trimmed items, skipping blanks."""
    if not value:
        return []
    if isinstance(value, str):
        value = value.split(";")
    return [item.strip().lower() for item in value if item.strip()]

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    """Calculate a song's score based on the user's genre, mood, and energy preferences."""
    
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, reasons)
    score = 0.0
    reasons = []

    # Rule 1: Genre match
    if song["genre"].strip().lower() == user_prefs["genre"].strip().lower():
        score += 1.0
        reasons.append("Genre matches (+1.0)")
    # Rule 2: Mood match
    if song["mood"].strip().lower() == user_prefs["mood"].strip().lower():
        score += 1.0
        reasons.append("Mood matches (+1.0)")
    # Rule 3: Energy similarity
    energy_score = 2.0 * (1 - abs(song["energy"] - user_prefs["energy"]))
    score += energy_score
    reasons.append(f"Energy similarity (+{energy_score:.2f})")

    # Advanced rules below only run when the user supplies that preference.

    # Rule 4: Popularity
    min_popularity = user_prefs.get("min_popularity")
    target_popularity = user_prefs.get("target_popularity")
    if target_popularity is not None:
        popularity_score = 1 - abs(song["popularity"] - target_popularity) / 100
        score += popularity_score
        reasons.append(f"Popularity {song['popularity']} close to target {target_popularity} (+{popularity_score:.2f})")
    elif min_popularity is not None:
        if song["popularity"] >= min_popularity:
            popularity_score = song["popularity"] / 100
            score += popularity_score
            reasons.append(f"Popularity {song['popularity']} meets minimum {min_popularity} (+{popularity_score:.2f})")
        else:
            reasons.append(f"Popularity {song['popularity']} below minimum {min_popularity} (+0.00)")

    # Rule 5: Release decade
    preferred_decade = user_prefs.get("preferred_decade")
    if preferred_decade and song["release_decade"].lower() == preferred_decade.strip().lower():
        score += 1.0
        reasons.append(f"Release decade {song['release_decade']} matches (+1.0)")

    # Rule 6: Mood tags (+1 per matching tag, max +2)
    song_tags = _clean_list(song["mood_tags"])
    matched_tags = [tag for tag in _clean_list(user_prefs.get("preferred_mood_tags")) if tag in song_tags]
    if matched_tags:
        tag_score = min(len(matched_tags), 2)
        score += tag_score
        reasons.append(f"Mood tags match: {', '.join(matched_tags)} (+{tag_score:.1f})")

    # Rule 7: Lyrical theme
    preferred_theme = user_prefs.get("preferred_lyrical_theme")
    if preferred_theme and song["lyrical_theme"].lower() == preferred_theme.strip().lower():
        score += 1.0
        reasons.append(f"Lyrical theme '{song['lyrical_theme']}' matches (+1.0)")

    # Rule 8: Instrumentation (+1 per matching instrument, max +2)
    song_instruments = _clean_list(song["instrumentation"])
    matched_instruments = [item for item in _clean_list(user_prefs.get("preferred_instruments")) if item in song_instruments]
    if matched_instruments:
        instrument_score = min(len(matched_instruments), 2)
        score += instrument_score
        reasons.append(f"Instruments match: {', '.join(matched_instruments)} (+{instrument_score:.1f})")

    return score, reasons



def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Rank songs, validate the results, and return safe recommendations.
    """

    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k must be a positive integer.")

    if not songs:
        raise ValueError("Cannot recommend songs from an empty dataset.")

    scored_songs = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored_songs.append((song, score, "; ".join(reasons)))

    ranked_songs = sorted(
        scored_songs,
        key=lambda item: item[1],
        reverse=True
    )

    recommendations = ranked_songs[:k]

    # Reliability check: inspect results before returning them.
    is_valid, issues = validate_recommendations(
        recommendations,
        songs,
        k
    )

    if not is_valid:
        logger.error(
            "Recommendation reliability check failed: %s",
            "; ".join(issues),
        )

        raise ValueError(
            "Recommendation reliability check failed: "
            + "; ".join(issues)
        )

    logger.info(
        "Generated %s recommendations from %s valid songs.",
        len(recommendations),
        len(songs),
    )

    return recommendations

