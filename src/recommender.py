import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    
    """Load song data from a CSV file and return it as a list of dictionaries."""
    
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": int(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "popularity": int(row["popularity"]),
                "release_decade": row["release_decade"].strip(),
                "mood_tags": [tag.strip() for tag in row["mood_tags"].split(";")],
                "lyrical_theme": row["lyrical_theme"].strip(),
                "instrumentation": [item.strip() for item in row["instrumentation"].split(";")],
            })
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


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    
    """Rank songs by score and return the top recommendations with explanations."""
    
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored_songs.append((song, score, reasons))
    
    ranked_songs = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    
    top_songs = ranked_songs[:k]
    
    recommendations = []

    for song, score, reasons in top_songs:
        explanation = "; ".join(reasons)
        recommendations.append((song, score, explanation))

    return recommendations
    


