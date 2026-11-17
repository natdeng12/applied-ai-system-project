
import logging
import re

from .logging_config import setup_logging

logger = setup_logging()


def validate_song_rows(rows):
    """
    Check song records and separate valid songs from invalid ones.

    Returns:
        valid_songs: Songs that passed validation.
        issues: Explanations of records that were excluded.
    """

    valid_songs = []
    issues = []
    seen_ids = set()
    duplicate_ids = set()

    # First, find IDs that appear more than once.
    id_counts = {}

    for row in rows:
        song_id = str(row.get("id", "")).strip()

        if song_id:
            id_counts[song_id] = id_counts.get(song_id, 0) + 1

    duplicate_ids = {
        song_id
        for song_id, count in id_counts.items()
        if count > 1
    }

    # Then validate each song.
    for row_number, row in enumerate(rows, start=2):
        errors = []

        song_id = str(row.get("id", "")).strip()
        title = str(row.get("title", "")).strip()
        artist = str(row.get("artist", "")).strip()
        genre = str(row.get("genre", "")).strip()
        mood = str(row.get("mood", "")).strip()

        # Check required text fields.
        required_fields = {
            "id": song_id,
            "title": title,
            "artist": artist,
            "genre": genre,
            "mood": mood,
        }

        for field, value in required_fields.items():
            if not value:
                errors.append(f"Missing {field}")

        # Exclude every record with a duplicated ID.
        if song_id in duplicate_ids:
            errors.append(f"Duplicate song ID: {song_id}")

        # Check numeric fields and their allowed ranges.
        numeric_rules = {
            "energy": (0, 1),
            "valence": (0, 1),
            "danceability": (0, 1),
            "acousticness": (0, 1),
            "tempo_bpm": (0, float("inf")),
            "popularity": (0, 100),
        }

        converted_values = {}

        for field, (minimum, maximum) in numeric_rules.items():
            try:
                value = float(row.get(field, ""))

                if not minimum <= value <= maximum:
                    errors.append(
                        f"{field} must be between {minimum} and {maximum}"
                    )
                else:
                    converted_values[field] = value

            except (ValueError, TypeError):
                errors.append(f"Invalid or missing number: {field}")

        # Check the release decade format.
        decade = str(row.get("release_decade", "")).strip()

        if not re.fullmatch(r"\d{4}s", decade):
            errors.append("Invalid release decade format")

        if errors:
            issues.append({
                "row": row_number,
                "id": song_id or "Unknown",
                "title": title or "Unknown",
                "reasons": errors,
            })
            continue

        # Keep the validated song and its converted numbers.
        cleaned_song = dict(row)
        cleaned_song.update(converted_values)

        cleaned_song["mood_tags"] = [
            tag.strip().lower()
            for tag in str(row.get("mood_tags", "")).split(";")
            if tag.strip()
        ]

        cleaned_song["instrumentation"] = [
            item.strip().lower()
            for item in str(row.get("instrumentation", "")).split(";")
            if item.strip()
        ]

        valid_songs.append(cleaned_song)

    logger.info(
        "Dataset validation complete: %s valid, %s excluded",
        len(valid_songs),
        len(issues),
    )

    for issue in issues:
        logger.warning(
            "Excluded row %s (ID: %s, Title: %s): %s",
            issue["row"],
            issue["id"],
            issue["title"],
            ", ".join(issue["reasons"]),
        )

    return valid_songs, issues
