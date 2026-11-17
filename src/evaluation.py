
import math


def validate_recommendations(recommendations, valid_songs, k):
    """
    Check whether recommendation results are safe and consistent.

    Returns:
        is_valid: True if all checks pass.
        issues: A list of problems found.
    """

    issues = []

    # Check that the requested number is valid.
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        return False, ["Requested recommendation count must be a positive integer."]

    # Check that the system did not return too many songs.
    if len(recommendations) > k:
        issues.append("More recommendations returned than requested.")

    # Build a set of IDs from the validated dataset.
    valid_ids = {str(song["id"]) for song in valid_songs}

    recommended_ids = []

    for song, score, explanation in recommendations:

        song_id = str(song.get("id", ""))

        # Check that the song belongs to the validated dataset.
        if song_id not in valid_ids:
            issues.append(f"Song ID {song_id} is not in the validated dataset.")

        recommended_ids.append(song_id)

        # Check that the score is a real, finite number.
        if not isinstance(score, (int, float)) or not math.isfinite(score):
            issues.append(f"Song ID {song_id} has an invalid score.")

        # Check that the explanation exists.
        if not isinstance(explanation, str) or not explanation.strip():
            issues.append(f"Song ID {song_id} has no explanation.")

    # Check for duplicate recommendations.
    if len(recommended_ids) != len(set(recommended_ids)):
        issues.append("Duplicate songs found in recommendations.")

    return len(issues) == 0, issues
