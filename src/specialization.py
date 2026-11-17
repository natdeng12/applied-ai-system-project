"""
Specialized recommendation mode for VibeFinder.

HONESTY NOTE: This is NOT machine-learning fine-tuning. No model is trained
and no weights are learned. It is a transparent, rule-based technique
inspired by "few-shot" prompting:

1. Each listening context (Focus / Study, Workout, ...) is described by a
   handful of hand-written EXAMPLE songs. These examples are fictional and
   are not in data/songs.csv.
2. The examples are averaged into a "prototype" (the typical tempo, valence,
   danceability, acousticness, and energy for that context), and their mood
   tags and instruments are collected into keyword sets.
3. Each song keeps its normal baseline score from score_song(), and then gets
   a context-fit bonus based on how closely it resembles the prototype.

The baseline recommender (recommend_songs / score_song) is not changed.
"""

from typing import Dict, List, Tuple

from .evaluation import validate_recommendations
from .logging_config import setup_logging
from .recommender import _clean_list, score_song

logger = setup_logging()


# Numeric features compared against the prototype. The baseline only uses
# energy, so tempo, valence, danceability, and acousticness are new signals.
FEATURES = ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]

# Tempo is measured in BPM, not 0-1, so it is divided by this value
# (and capped at 1.0) to put it on the same scale as the other features.
TEMPO_SCALE = 200.0

# Bonus weights. The baseline's core rules are worth up to 4.0 points, and
# the context bonus can also add up to 4.0, so the listening context
# matters about as much as genre + mood + energy together.
FEATURE_WEIGHT = 2.0        # up to +2.0 for audio-feature similarity
TAG_POINTS = 0.5            # +0.5 per shared mood tag...
TAG_MAX = 1.0               # ...up to +1.0
INSTRUMENT_POINTS = 0.5     # +0.5 per shared instrument...
INSTRUMENT_MAX = 1.0        # ...up to +1.0


# ---------------------------------------------------------------------------
# Few-shot examples: 3 fictional example songs per listening context
# ---------------------------------------------------------------------------
SPECIALIZED_PROFILES = {
    "focus_study": {
        "label": "Focus / Study",
        "description": "Steady, low-distraction music with moderate tempo and acoustic textures.",
        "examples": [
            {"title": "Desk Lamp Glow", "energy": 0.38, "tempo_bpm": 76, "valence": 0.55,
             "danceability": 0.50, "acousticness": 0.80,
             "mood_tags": ["calm", "steady", "concentrated"],
             "instrumentation": ["piano", "soft drums"]},
            {"title": "Notebook Margins", "energy": 0.32, "tempo_bpm": 70, "valence": 0.50,
             "danceability": 0.45, "acousticness": 0.85,
             "mood_tags": ["mellow", "calm", "introspective"],
             "instrumentation": ["electric piano", "vinyl crackle"]},
            {"title": "Quiet Algorithm", "energy": 0.42, "tempo_bpm": 84, "valence": 0.58,
             "danceability": 0.55, "acousticness": 0.70,
             "mood_tags": ["steady", "focused", "cozy"],
             "instrumentation": ["synth pads", "soft drums", "bass"]},
        ],
    },
    "workout": {
        "label": "Workout / High Energy",
        "description": "Fast, loud, danceable tracks that keep you moving.",
        "examples": [
            {"title": "Last Rep Standing", "energy": 0.94, "tempo_bpm": 140, "valence": 0.72,
             "danceability": 0.86, "acousticness": 0.06,
             "mood_tags": ["energetic", "motivational", "relentless"],
             "instrumentation": ["808 bass", "synthesizer", "claps"]},
            {"title": "Sprint Interval", "energy": 0.90, "tempo_bpm": 150, "valence": 0.65,
             "danceability": 0.80, "acousticness": 0.08,
             "mood_tags": ["driving", "determined", "aggressive"],
             "instrumentation": ["electric guitar", "drums", "bass guitar"]},
            {"title": "Pulse Check", "energy": 0.88, "tempo_bpm": 128, "valence": 0.80,
             "danceability": 0.90, "acousticness": 0.10,
             "mood_tags": ["energetic", "bold", "confident"],
             "instrumentation": ["synthesizer", "drum machine", "808 bass"]},
        ],
    },
    "relax_chill": {
        "label": "Relaxation / Chill",
        "description": "Soft, slow, warm music for unwinding.",
        "examples": [
            {"title": "Hammock Hours", "energy": 0.28, "tempo_bpm": 74, "valence": 0.68,
             "danceability": 0.45, "acousticness": 0.88,
             "mood_tags": ["peaceful", "laid-back", "warm"],
             "instrumentation": ["acoustic guitar", "soft percussion"]},
            {"title": "Low Tide", "energy": 0.24, "tempo_bpm": 66, "valence": 0.62,
             "danceability": 0.40, "acousticness": 0.90,
             "mood_tags": ["serene", "calm", "dreamy"],
             "instrumentation": ["synth pads", "field recordings"]},
            {"title": "Tea Steam", "energy": 0.33, "tempo_bpm": 82, "valence": 0.70,
             "danceability": 0.50, "acousticness": 0.82,
             "mood_tags": ["gentle", "easygoing", "warm"],
             "instrumentation": ["piano", "upright bass", "brushed drums"]},
        ],
    },
    "emotional_reflective": {
        "label": "Emotional / Reflective",
        "description": "Slower, lower-valence songs with bittersweet or wistful feelings.",
        "examples": [
            {"title": "Unsent Postcard", "energy": 0.30, "tempo_bpm": 70, "valence": 0.28,
             "danceability": 0.38, "acousticness": 0.80,
             "mood_tags": ["bittersweet", "longing", "reflective"],
             "instrumentation": ["piano", "strings"]},
            {"title": "Empty Platform", "energy": 0.36, "tempo_bpm": 76, "valence": 0.22,
             "danceability": 0.42, "acousticness": 0.65,
             "mood_tags": ["melancholy", "lonely", "introspective"],
             "instrumentation": ["piano", "synth pads"]},
            {"title": "Faded Porch Light", "energy": 0.40, "tempo_bpm": 86, "valence": 0.40,
             "danceability": 0.45, "acousticness": 0.85,
             "mood_tags": ["wistful", "tender", "homesick"],
             "instrumentation": ["acoustic guitar", "cello"]},
        ],
    },
    "night_drive": {
        "label": "Night Drive",
        "description": "Mid-tempo, moody, synth-heavy tracks for late-night roads.",
        "examples": [
            {"title": "Highway Neon", "energy": 0.72, "tempo_bpm": 108, "valence": 0.45,
             "danceability": 0.72, "acousticness": 0.15,
             "mood_tags": ["nocturnal", "brooding", "nostalgic"],
             "instrumentation": ["synthesizer", "arpeggiator", "drum machine"]},
            {"title": "Exit 42", "energy": 0.66, "tempo_bpm": 100, "valence": 0.50,
             "danceability": 0.68, "acousticness": 0.20,
             "mood_tags": ["late-night", "mellow", "nostalgic"],
             "instrumentation": ["electric bass", "synthesizer", "electric piano"]},
            {"title": "Taillight Trails", "energy": 0.78, "tempo_bpm": 116, "valence": 0.40,
             "danceability": 0.75, "acousticness": 0.12,
             "mood_tags": ["driving", "tense", "nocturnal"],
             "instrumentation": ["synthesizer", "drum machine", "electric guitar"]},
        ],
    },
}


def _scaled(feature: str, value: float) -> float:
    """Put every feature on a 0-1 scale so differences are comparable."""
    if feature == "tempo_bpm":
        return min(float(value) / TEMPO_SCALE, 1.0)
    return float(value)


def build_prototype(profile_key: str) -> Dict:
    """
    Combine a profile's example songs into one prototype.

    The prototype holds the AVERAGE of each numeric feature across the
    examples, plus every mood tag and instrument that appears in them.
    """
    if profile_key not in SPECIALIZED_PROFILES:
        raise ValueError(
            f"Unknown specialized profile '{profile_key}'. "
            f"Choose from: {', '.join(SPECIALIZED_PROFILES)}"
        )

    examples = SPECIALIZED_PROFILES[profile_key]["examples"]

    averages = {
        feature: sum(example[feature] for example in examples) / len(examples)
        for feature in FEATURES
    }

    # sorted() keeps the order stable so explanations are reproducible.
    tags = sorted({tag for example in examples for tag in _clean_list(example["mood_tags"])})
    instruments = sorted({
        item for example in examples for item in _clean_list(example["instrumentation"])
    })

    return {"averages": averages, "tags": tags, "instruments": instruments}


def feature_similarity(song: Dict, target: Dict) -> float:
    """
    Return a 0-1 similarity between a song and a target (prototype or example).
    1.0 means identical audio features; lower means more different.
    """
    differences = [
        abs(_scaled(feature, song[feature]) - _scaled(feature, target[feature]))
        for feature in FEATURES
    ]
    return 1.0 - sum(differences) / len(differences)


def closest_example(song: Dict, profile_key: str) -> Tuple[str, float]:
    """Find which example song this song most resembles (for the explanation)."""
    best_title, best_similarity = "", -1.0

    for example in SPECIALIZED_PROFILES[profile_key]["examples"]:
        similarity = feature_similarity(song, example)
        # Strict ">" keeps the first example on ties, so results are deterministic.
        if similarity > best_similarity:
            best_title, best_similarity = example["title"], similarity

    return best_title, best_similarity


def context_bonus(song: Dict, profile_key: str, prototype: Dict = None) -> Tuple[float, List[str]]:
    """Score how well a song fits the listening context. Returns (bonus, reasons)."""
    if prototype is None:
        prototype = build_prototype(profile_key)

    label = SPECIALIZED_PROFILES[profile_key]["label"]
    reasons = []

    # Part 1: audio-feature similarity to the prototype (up to +2.0).
    similarity = feature_similarity(song, prototype["averages"])
    feature_points = FEATURE_WEIGHT * max(similarity, 0.0)
    bonus = feature_points
    reasons.append(f"{label} sound profile {similarity:.0%} similar (+{feature_points:.2f})")

    # Part 2: mood tags shared with the examples (+0.5 each, max +1.0).
    shared_tags = [tag for tag in _clean_list(song["mood_tags"]) if tag in prototype["tags"]]
    if shared_tags:
        tag_points = min(len(shared_tags) * TAG_POINTS, TAG_MAX)
        bonus += tag_points
        reasons.append(f"Shares example mood tags: {', '.join(shared_tags)} (+{tag_points:.1f})")

    # Part 3: instruments shared with the examples (+0.5 each, max +1.0).
    shared_instruments = [
        item for item in _clean_list(song["instrumentation"]) if item in prototype["instruments"]
    ]
    if shared_instruments:
        instrument_points = min(len(shared_instruments) * INSTRUMENT_POINTS, INSTRUMENT_MAX)
        bonus += instrument_points
        reasons.append(
            f"Shares example instruments: {', '.join(shared_instruments)} (+{instrument_points:.1f})"
        )

    title, _similarity = closest_example(song, profile_key)
    reasons.append(f"Closest example song: '{title}'")

    return bonus, reasons


def score_song_specialized(user_prefs: Dict, song: Dict, profile_key: str,
                           prototype: Dict = None) -> Tuple[float, List[str]]:
    """Baseline score (unchanged) plus the listening-context bonus."""
    base_score, base_reasons = score_song(user_prefs, song)
    bonus, bonus_reasons = context_bonus(song, profile_key, prototype)
    return base_score + bonus, base_reasons + bonus_reasons


def recommend_songs_specialized(
    user_prefs: Dict,
    songs: List[Dict],
    profile_key: str,
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """
    Rank songs using specialized scoring. Returns the same
    (song, score, explanation) format as recommend_songs(), and runs the same
    reliability check before returning.
    """
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k must be a positive integer.")

    if not songs:
        raise ValueError("Cannot recommend songs from an empty dataset.")

    # Build the prototype once instead of once per song.
    prototype = build_prototype(profile_key)
    label = SPECIALIZED_PROFILES[profile_key]["label"]

    scored_songs = []
    for song in songs:
        score, reasons = score_song_specialized(user_prefs, song, profile_key, prototype)
        explanation = f"[{label} mode] " + "; ".join(reasons)
        scored_songs.append((song, score, explanation))

    # sorted() is stable: tied songs keep their dataset order (deterministic).
    ranked = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    recommendations = ranked[:k]

    is_valid, issues = validate_recommendations(recommendations, songs, k)
    if not is_valid:
        logger.error("Specialized recommendation check failed: %s", "; ".join(issues))
        raise ValueError("Recommendation reliability check failed: " + "; ".join(issues))

    logger.info(
        "Generated %s specialized (%s) recommendations from %s valid songs.",
        len(recommendations), profile_key, len(songs),
    )
    return recommendations
