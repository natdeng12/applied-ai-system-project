"""
Evaluation harness for VibeFinder.

This script runs the real recommendation engine against a fixed collection of
test profiles and checks the results with measurable pass/fail criteria.

It is different from the pytest unit tests: instead of testing small pieces of
code in isolation, it tests the end-to-end recommendation *behavior* on the
real dataset (data/songs.csv) and writes a reproducible JSON report.

Run it from the project root with:

    python -m src.evaluation_runner

The script exits with code 1 if any check fails, so failures can never
silently pass.
"""

import argparse
import json
import logging
import math
from pathlib import Path

from .recommender import load_songs_with_report, recommend_songs
from .specialization import SPECIALIZED_PROFILES, recommend_songs_specialized


DEFAULT_DATASET = "data/songs.csv"
DEFAULT_OUTPUT = "reports/evaluation_results.json"

# The specialized mode must change results for at least this many profiles.
MIN_PROFILES_WITH_DIFFERENT_RESULTS = 3


# ---------------------------------------------------------------------------
# Predefined test profiles
# ---------------------------------------------------------------------------
# Each case describes:
#   - name:   a readable label
#   - prefs:  the user preferences passed to the recommender
#   - k:      how many recommendations to request
#   - expect: what a *reasonable* top result should look like
#
# Expectations describe preference patterns (genre, mood, energy range),
# not specific song titles, so they test behavior rather than memorized output.
#
# Supported expectation keys:
#   top_genre:         the #1 song's genre must equal this value
#   top_mood:          the #1 song's mood must equal this value
#   top_energy_range:  [low, high] range for the #1 song's energy
#   avg_feature_range: {feature: [low, high]} range for the average value of a
#                      numeric feature across all returned songs
TEST_CASES = [
    {
        "name": "High-Energy Pop",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.90},
        "k": 5,
        "expect": {
            "top_genre": "pop",
            "top_mood": "happy",
            "top_energy_range": [0.70, 1.00],
        },
    },
    {
        "name": "Chill Lofi",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35},
        "k": 5,
        "expect": {
            "top_genre": "lofi",
            "top_mood": "chill",
            "avg_feature_range": {"energy": [0.0, 0.60]},
        },
    },
    {
        "name": "Deep Intense Rock",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.88},
        "k": 5,
        "expect": {
            "top_genre": "rock",
            "top_mood": "intense",
            "top_energy_range": [0.75, 1.00],
        },
    },
    {
        "name": "Relaxed Jazz",
        "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.35},
        "k": 5,
        "expect": {
            "top_genre": "jazz",
            "top_mood": "relaxed",
            "avg_feature_range": {"energy": [0.0, 0.60]},
        },
    },
    {
        "name": "Sad R&B",
        "prefs": {"genre": "R&B", "mood": "sad", "energy": 0.30},
        "k": 5,
        "expect": {
            "top_genre": "r&b",
            "top_mood": "sad",
            "top_energy_range": [0.0, 0.50],
        },
    },
    {
        # Edge case: "metal" does not exist in the dataset, so no song can get
        # the genre bonus. A sensible result should still match mood and energy.
        "name": "Unknown Genre (Metal)",
        "prefs": {"genre": "metal", "mood": "intense", "energy": 0.95},
        "k": 5,
        "expect": {
            "top_mood": "intense",
            "top_energy_range": [0.80, 1.00],
        },
    },
    {
        # Edge case: asking for more songs than exist. The system should
        # return every valid song (20), not crash and not invent extra songs.
        "name": "Oversized Request (k=25)",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.50},
        "k": 25,
        "expect": {},
    },
]

# Specialized-mode cases. "profile" picks the listening context from
# src/specialization.py. Expectations describe what that context should feel
# like (e.g. a workout list should have high average energy).
SPECIALIZED_TEST_CASES = [
    {
        "name": "Study Session (lofi)",
        "mode": "specialized",
        "profile": "focus_study",
        "prefs": {"genre": "lofi", "mood": "focused", "energy": 0.45},
        "k": 5,
        "expect": {
            "top_energy_range": [0.0, 0.60],
            "avg_feature_range": {"acousticness": [0.50, 1.00]},
        },
    },
    {
        "name": "Workout Mix (pop)",
        "mode": "specialized",
        "profile": "workout",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.75},
        "k": 5,
        "expect": {
            "top_energy_range": [0.80, 1.00],
            "avg_feature_range": {"energy": [0.75, 1.00]},
        },
    },
    {
        "name": "Wind Down (jazz)",
        "mode": "specialized",
        "profile": "relax_chill",
        "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.45},
        "k": 5,
        "expect": {
            "avg_feature_range": {"energy": [0.0, 0.50], "acousticness": [0.60, 1.00]},
        },
    },
    {
        "name": "Reflective Evening (country)",
        "mode": "specialized",
        "profile": "emotional_reflective",
        "prefs": {"genre": "country", "mood": "nostalgic", "energy": 0.45},
        "k": 5,
        "expect": {
            "avg_feature_range": {"valence": [0.0, 0.60]},
        },
    },
    {
        "name": "Night Drive (synthwave)",
        "mode": "specialized",
        "profile": "night_drive",
        "prefs": {"genre": "synthwave", "mood": "moody", "energy": 0.70},
        "k": 5,
        "expect": {
            "top_energy_range": [0.55, 0.90],
            "avg_feature_range": {"acousticness": [0.0, 0.40]},
        },
    },
]

ALL_TEST_CASES = TEST_CASES + SPECIALIZED_TEST_CASES


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------
# Every check returns a dictionary: {"check": name, "passed": bool, "detail": str}

def _result(check, passed, detail):
    return {"check": check, "passed": bool(passed), "detail": detail}


def check_count(recommendations, songs, k):
    """The system should return k songs, or every song if k is larger than the dataset."""
    expected = min(k, len(songs))
    actual = len(recommendations)
    return _result(
        "returned_requested_count",
        actual == expected,
        f"expected {expected}, got {actual}",
    )


def check_songs_in_dataset(recommendations, songs):
    """Every recommended song must exist in the validated dataset with the same title."""
    titles_by_id = {str(song["id"]): song["title"] for song in songs}
    bad = []

    for song, _score, _explanation in recommendations:
        song_id = str(song.get("id", ""))
        if titles_by_id.get(song_id) != song.get("title"):
            bad.append(f"{song_id}:{song.get('title')}")

    detail = "all songs found in dataset" if not bad else f"unknown songs: {', '.join(bad)}"
    return _result("songs_in_dataset", not bad, detail)


def check_no_duplicates(recommendations):
    """No song should appear more than once."""
    ids = [str(song.get("id", "")) for song, _score, _explanation in recommendations]
    duplicates = sorted({song_id for song_id in ids if ids.count(song_id) > 1})
    detail = "no duplicates" if not duplicates else f"duplicate IDs: {', '.join(duplicates)}"
    return _result("no_duplicates", not duplicates, detail)


def check_scores_finite(recommendations):
    """Scores must be real, finite numbers (not NaN, infinity, or text)."""
    bad = []

    for song, score, _explanation in recommendations:
        # bool is a subclass of int in Python, so exclude it explicitly.
        is_number = isinstance(score, (int, float)) and not isinstance(score, bool)
        if not is_number or not math.isfinite(score):
            bad.append(str(song.get("id", "?")))

    detail = "all scores finite" if not bad else f"invalid scores for IDs: {', '.join(bad)}"
    return _result("scores_finite", not bad, detail)


def check_explanations_present(recommendations):
    """Every recommendation must come with a non-empty explanation."""
    missing = [
        str(song.get("id", "?"))
        for song, _score, explanation in recommendations
        if not isinstance(explanation, str) or not explanation.strip()
    ]
    detail = "all explanations present" if not missing else f"missing for IDs: {', '.join(missing)}"
    return _result("explanations_present", not missing, detail)


def check_sorted_by_score(recommendations):
    """Results should be ranked from highest to lowest score."""
    scores = [score for _song, score, _explanation in recommendations]

    try:
        is_sorted = all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))
    except TypeError:
        # Scores that cannot be compared (e.g. text) mean the ranking is broken.
        is_sorted = False

    detail = "scores in descending order" if is_sorted else f"scores out of order: {scores}"
    return _result("sorted_by_score", is_sorted, detail)


def check_expectations(recommendations, expect):
    """Check the top result (and averages) against the case's expected preference pattern."""
    results = []

    if not expect:
        return results

    if not recommendations:
        return [_result("expectations", False, "no recommendations to compare")]

    top_song = recommendations[0][0]

    if "top_genre" in expect:
        wanted = expect["top_genre"].strip().lower()
        actual = str(top_song.get("genre", "")).strip().lower()
        results.append(_result(
            "top_genre_matches",
            actual == wanted,
            f"expected '{wanted}', top song '{top_song.get('title')}' is '{actual}'",
        ))

    if "top_mood" in expect:
        wanted = expect["top_mood"].strip().lower()
        actual = str(top_song.get("mood", "")).strip().lower()
        results.append(_result(
            "top_mood_matches",
            actual == wanted,
            f"expected '{wanted}', top song '{top_song.get('title')}' is '{actual}'",
        ))

    if "top_energy_range" in expect:
        low, high = expect["top_energy_range"]
        energy = float(top_song.get("energy", -1))
        results.append(_result(
            "top_energy_in_range",
            low <= energy <= high,
            f"expected {low:.2f}-{high:.2f}, top song energy is {energy:.2f}",
        ))

    for feature, (low, high) in expect.get("avg_feature_range", {}).items():
        values = [float(song.get(feature, 0)) for song, _s, _e in recommendations]
        average = sum(values) / len(values)
        results.append(_result(
            f"avg_{feature}_in_range",
            low <= average <= high,
            f"expected {low:.2f}-{high:.2f}, average {feature} is {average:.2f}",
        ))

    return results


# ---------------------------------------------------------------------------
# Running cases
# ---------------------------------------------------------------------------

def run_case(case, songs, recommend_fn=None):
    """
    Run one test case and return a result dictionary.

    recommend_fn lets tests swap in a deliberately broken recommender to prove
    the harness catches problems. By default the real engine is used.
    """
    if recommend_fn is None:
        recommend_fn = default_recommend_fn

    k = case.get("k", 5)
    result = {
        "name": case["name"],
        "mode": case.get("mode", "baseline"),
        "profile": case.get("profile"),
        "prefs": case["prefs"],
        "k": k,
        "checks": [],
        "recommendations": [],
        "error": None,
    }

    try:
        recommendations = recommend_fn(case, songs, k)
    except Exception as error:  # noqa: BLE001 - any crash counts as a failed case
        # A crash is a failure, not something to skip over.
        result["error"] = f"{type(error).__name__}: {error}"
        result["checks"].append(_result("engine_ran_without_error", False, result["error"]))
        result["passed"] = False
        return result

    result["checks"].append(_result("engine_ran_without_error", True, "no exception"))
    result["checks"].extend([
        check_count(recommendations, songs, k),
        check_songs_in_dataset(recommendations, songs),
        check_no_duplicates(recommendations),
        check_scores_finite(recommendations),
        check_explanations_present(recommendations),
        check_sorted_by_score(recommendations),
    ])
    result["checks"].extend(check_expectations(recommendations, case.get("expect", {})))

    # Store a compact copy of the output so the report shows what was evaluated.
    for song, score, _explanation in recommendations:
        safe_score = round(score, 4) if isinstance(score, float) and math.isfinite(score) else str(score)
        result["recommendations"].append({
            "id": song.get("id"),
            "title": song.get("title"),
            "genre": song.get("genre"),
            "mood": song.get("mood"),
            "score": safe_score,
        })

    result["passed"] = all(check["passed"] for check in result["checks"])
    return result


def default_recommend_fn(case, songs, k):
    """Call the real engine: baseline by default, specialized if the case asks for it."""
    if case.get("mode") == "specialized":
        return recommend_songs_specialized(case["prefs"], songs, case["profile"], k)
    return recommend_songs(case["prefs"], songs, k)


def compare_modes(songs, cases=None):
    """
    Run each specialized case twice (baseline and specialized, same user
    preferences) and measure how much the results differ.
    """
    if cases is None:
        cases = SPECIALIZED_TEST_CASES

    profiles = []
    for case in cases:
        k = case.get("k", 5)
        baseline = recommend_songs(case["prefs"], songs, k)
        specialized = recommend_songs_specialized(case["prefs"], songs, case["profile"], k)

        baseline_titles = [song["title"] for song, _s, _e in baseline]
        specialized_titles = [song["title"] for song, _s, _e in specialized]

        # positions_changed counts rank slots that now hold a different song.
        positions_changed = sum(
            1 for before, after in zip(baseline_titles, specialized_titles) if before != after
        )

        # Apply the SAME context expectations to both lists. This shows whether
        # the specialized mode actually fits the context better than baseline.
        baseline_expect = check_expectations(baseline, case.get("expect", {}))
        specialized_expect = check_expectations(specialized, case.get("expect", {}))

        profiles.append({
            "name": case["name"],
            "specialized_profile": SPECIALIZED_PROFILES[case["profile"]]["label"],
            "k": k,
            "baseline_top": baseline_titles,
            "specialized_top": specialized_titles,
            "top_pick_changed": baseline_titles[0] != specialized_titles[0],
            "shared_songs": len(set(baseline_titles) & set(specialized_titles)),
            "positions_changed": positions_changed,
            "results_differ": baseline_titles != specialized_titles,
            "baseline_context_checks_passed": sum(c["passed"] for c in baseline_expect),
            "specialized_context_checks_passed": sum(c["passed"] for c in specialized_expect),
            "context_checks_total": len(specialized_expect),
            "baseline_context_details": [c["detail"] for c in baseline_expect],
        })

    differing = sum(1 for item in profiles if item["results_differ"])
    return {
        "profiles": profiles,
        "profiles_with_different_results": differing,
        "baseline_context_checks_passed": sum(p["baseline_context_checks_passed"] for p in profiles),
        "specialized_context_checks_passed": sum(p["specialized_context_checks_passed"] for p in profiles),
        "context_checks_total": sum(p["context_checks_total"] for p in profiles),
        "required_minimum": MIN_PROFILES_WITH_DIFFERENT_RESULTS,
        "passed": differing >= MIN_PROFILES_WITH_DIFFERENT_RESULTS,
    }


def summarize(case_results):
    """Calculate overall metrics from a list of case results."""
    total_cases = len(case_results)
    passed_cases = sum(1 for case in case_results if case["passed"])

    all_checks = [check for case in case_results for check in case["checks"]]
    total_checks = len(all_checks)
    passed_checks = sum(1 for check in all_checks if check["passed"])

    # Pass counts for each type of check, e.g. how often "no_duplicates" passed.
    per_check = {}
    for check in all_checks:
        stats = per_check.setdefault(check["check"], {"passed": 0, "total": 0})
        stats["total"] += 1
        stats["passed"] += int(check["passed"])

    return {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": total_cases - passed_cases,
        "case_success_rate": round(passed_cases / total_cases, 4) if total_cases else 0.0,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "check_pass_rate": round(passed_checks / total_checks, 4) if total_checks else 0.0,
        "per_check": dict(sorted(per_check.items())),
        "failed_case_names": [case["name"] for case in case_results if not case["passed"]],
        # An empty run must not count as a success.
        "overall_passed": total_cases > 0 and passed_cases == total_cases,
    }


def run_evaluation(dataset_path=DEFAULT_DATASET, cases=None, recommend_fn=None,
                   include_comparison=True):
    """Load the dataset, run every case, and return the full report dictionary."""
    if cases is None:
        cases = ALL_TEST_CASES

    songs, issues = load_songs_with_report(dataset_path)
    case_results = [run_case(case, songs, recommend_fn) for case in cases]
    summary = summarize(case_results)

    report = {
        "dataset": {
            "path": dataset_path,
            "valid_songs": len(songs),
            "excluded_songs": len(issues),
        },
        "summary": summary,
        "cases": case_results,
    }

    if include_comparison:
        try:
            comparison = compare_modes(songs)
        except Exception as error:  # noqa: BLE001 - report, never hide, a crash
            comparison = {"profiles": [], "profiles_with_different_results": 0,
                          "required_minimum": MIN_PROFILES_WITH_DIFFERENT_RESULTS,
                          "passed": False, "error": f"{type(error).__name__}: {error}"}
        report["specialization_comparison"] = comparison
        summary["comparison_passed"] = comparison["passed"]
        # The overall result fails if the specialized mode does not actually
        # change results, even when every individual case passed.
        summary["overall_passed"] = summary["overall_passed"] and comparison["passed"]
        if not comparison["passed"]:
            summary["failed_case_names"].append("Baseline vs specialized comparison")

    return report


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def format_report(report):
    """Turn the report dictionary into readable terminal text."""
    lines = []
    line = "=" * 64
    lines.append(line)
    lines.append("VIBEFINDER EVALUATION REPORT")
    lines.append(line)
    dataset = report["dataset"]
    lines.append(
        f"Dataset: {dataset['path']} "
        f"({dataset['valid_songs']} valid, {dataset['excluded_songs']} excluded)"
    )

    for case in report["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        lines.append("")
        mode = case["mode"] if not case.get("profile") else f"{case['mode']}: {case['profile']}"
        lines.append(f"[{status}] {case['name']}  (mode: {mode}, k={case['k']})")

        top = case["recommendations"][0] if case["recommendations"] else None
        if top:
            lines.append(f"       Top pick: {top['title']} ({top['genre']}, {top['mood']}) score {top['score']}")

        for check in case["checks"]:
            mark = "ok  " if check["passed"] else "FAIL"
            lines.append(f"       {mark} {check['check']}: {check['detail']}")

    summary = report["summary"]
    lines.append("")
    lines.append(line)
    lines.append("SUMMARY")
    lines.append(line)
    lines.append(
        f"Profiles passed: {summary['passed_cases']}/{summary['total_cases']} "
        f"({summary['case_success_rate']:.0%})"
    )
    lines.append(
        f"Checks passed:   {summary['passed_checks']}/{summary['total_checks']} "
        f"({summary['check_pass_rate']:.0%})"
    )
    lines.append("Per-check results:")
    for name, stats in summary["per_check"].items():
        lines.append(f"  - {name}: {stats['passed']}/{stats['total']}")

    # Optional section added by the specialization comparison.
    comparison = report.get("specialization_comparison")
    if comparison:
        lines.append("")
        lines.append(line)
        lines.append("BASELINE vs SPECIALIZED COMPARISON")
        lines.append(line)
        for item in comparison["profiles"]:
            lines.append(f"{item['name']} -> specialized mode: {item['specialized_profile']}")
            lines.append(f"  Baseline top 5:    {', '.join(item['baseline_top'])}")
            lines.append(f"  Specialized top 5: {', '.join(item['specialized_top'])}")
            lines.append(
                f"  Top pick changed: {'yes' if item['top_pick_changed'] else 'no'} | "
                f"shared songs: {item['shared_songs']}/{item['k']} | "
                f"positions changed: {item['positions_changed']}/{item['k']}"
            )
            lines.append(
                f"  Context checks met: baseline {item['baseline_context_checks_passed']}/"
                f"{item['context_checks_total']}, specialized "
                f"{item['specialized_context_checks_passed']}/{item['context_checks_total']}"
            )
        lines.append(
            f"Profiles with different results: "
            f"{comparison['profiles_with_different_results']}/{len(comparison['profiles'])} "
            f"(required: {comparison['required_minimum']})"
        )
        lines.append(
            f"Context checks met overall: baseline "
            f"{comparison['baseline_context_checks_passed']}/{comparison['context_checks_total']}, "
            f"specialized {comparison['specialized_context_checks_passed']}/"
            f"{comparison['context_checks_total']}"
        )
        if comparison.get("error"):
            lines.append(f"Comparison error: {comparison['error']}")

    lines.append("")
    if summary["overall_passed"]:
        lines.append("OVERALL RESULT: PASS")
    else:
        failed = ", ".join(summary["failed_case_names"]) or "no cases were run"
        lines.append(f"OVERALL RESULT: FAIL ({failed})")
    lines.append(line)
    return "\n".join(lines)


def save_report(report, output_path):
    """Write the report as JSON. No timestamps are included, so reruns produce identical files."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as file:
        json.dump(report, file, indent=2)
        file.write("\n")
    return path


def _quiet_console_logging():
    """
    Hide INFO log lines in the terminal so the report is readable.
    The log file (vibefinder.log) still receives every message.
    """
    for handler in logging.getLogger().handlers:
        # FileHandler is a subclass of StreamHandler, so check the exact type.
        if type(handler) is logging.StreamHandler:
            handler.setLevel(logging.WARNING)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the VibeFinder evaluation harness.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Path to the songs CSV.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Where to save the JSON report.")
    parser.add_argument("--no-save", action="store_true", help="Print the report without saving JSON.")
    args = parser.parse_args(argv)

    _quiet_console_logging()

    report = run_evaluation(args.dataset)
    print(format_report(report))

    if not args.no_save:
        path = save_report(report, args.output)
        print(f"Saved JSON report to {path.as_posix()}")

    # A non-zero exit code makes failures visible to scripts and CI.
    return 0 if report["summary"]["overall_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
