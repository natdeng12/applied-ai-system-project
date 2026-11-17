# 🎵 VibeFinder 1.0

A content-based music recommendation simulation with an integrated reliability and testing system.

## Project Summary

VibeFinder is a music recommendation application that suggests songs based on a user's preferred genre, mood, and energy level.

Users can interact with the application through a Streamlit web interface, customize their music preferences, and receive up to five ranked recommendations with explanations for each result.

The project also includes a reliability system that checks dataset records before they are used and validates recommendation results before displaying them. Invalid records are excluded and reported rather than silently included in the recommendation process.

## Features

- **Interactive Interface:** Select a preferred genre, mood, and energy level.
- **Content-Based Recommendations:** Compare user preferences with song characteristics and rank matching songs.
- **Recommendation Explanations:** Display the match score and reasons behind each recommendation.
- **Dataset Validation:** Check song records for missing information, invalid values, and duplicate IDs.
- **Invalid Record Handling:** Exclude invalid records and report why they were rejected.
- **Recommendation Validation:** Check generated recommendations for issues such as duplicate songs, invalid scores, and songs outside the valid dataset.
- **Logging:** Record dataset validation and recommendation activity.
- **Automated Tests:** Use pytest to check recommendation, validation, and evaluation behavior.
- **Evaluation Harness (stretch):** Run the recommender against 12 predefined test profiles and get a pass/fail report with metrics.
- **Specialized Mode (stretch):** Optionally tune recommendations to a listening context (Focus / Study, Workout, Relaxation, Emotional, Night Drive) using few-shot-inspired example songs. This is rule-based, **not** a fine-tuned model.

## How the System Works

VibeFinder uses a content-based recommendation approach. It compares a user's selected preferences with the characteristics of songs in its dataset.

It does not train a machine-learning model or use listening histories from other users. Instead, it uses a scoring algorithm to estimate how closely each song matches the selected preferences.

### Song Dataset

The dataset contains 20 songs and 15 columns:

| Feature | Description |
|---|---|
| id | Unique song identifier |
| title | Song title |
| artist | Artist name |
| genre | Music genre |
| mood | Song mood |
| energy | Energy level (0–1) |
| tempo_bpm | Speed of the song in beats per minute |
| valence | How positive or happy the song sounds (0–1) |
| danceability | How suitable the song is for dancing (0–1) |
| acousticness | How acoustic the song sounds (0–1) |
| popularity | Popularity value (0–100) |
| release_decade | Decade in which the song was released |
| mood_tags | Additional mood descriptors |
| lyrical_theme | Main lyrical theme |
| instrumentation | Instruments or sound elements |

### User Preferences

The Streamlit interface lets users select:

- Favorite genre
- Desired mood
- Target energy level (0–1)

### Recommendation Scoring

The current application uses three main scoring rules:

- Genre match: +1.0 point
- Mood match: +1.0 point
- Energy similarity: up to +2.0 points

Energy similarity is calculated using:

`2.0 × (1 - abs(song_energy - preferred_energy))`

The scores are added together. Songs are ranked from highest to lowest, and the application displays up to five recommendations.

Each recommendation includes its score and an explanation of the matching preferences.

## Reliability and Testing System

Reliability is an important part of VibeFinder. The system checks both the dataset and the recommendations generated from it.

### 1. Dataset Validation

Before recommendations are generated, the application checks the song dataset for:

- Missing required information
- Invalid numerical values
- Energy, valence, danceability, or acousticness outside the 0–1 range
- Popularity outside the 0–100 range
- Invalid tempo values
- Invalid release decade formats
- Duplicate song IDs

If multiple records share the same song ID, all records with that ID are excluded.

Invalid records are skipped, and the system reports the affected rows and reasons for exclusion. If no valid songs remain, the system stops with a helpful error.

### 2. Recommendation Validation

After recommendations are generated, the system checks that:

- The number of recommendations does not exceed the requested limit.
- Every recommended song belongs to the validated dataset.
- Recommendation scores are valid finite numbers.
- Each recommendation has an explanation.
- No song appears more than once.

If the output fails validation, the system reports an error instead of treating the results as valid.

### 3. Logging

VibeFinder records important events in `vibefinder.log`, including dataset validation results, excluded records, and recommendation generation.

### 4. Automated Testing

The project uses pytest to test recommendation behavior, dataset validation, and recommendation output validation.

Run the tests with:

```powershell
python -m pytest
```

The suite currently contains **39 passing tests** (the original 14, plus 14 for the evaluation harness and 11 for the specialized mode).

## Stretch Feature 1: Evaluation Harness

`src/evaluation_runner.py` runs the **real** recommendation engine on the **real** dataset against a fixed set of test profiles. It then grades the results with measurable checks. It does not just rerun the unit tests. It tests end-to-end recommendation behavior.

### What it tests

There are 12 predefined profiles:

- **7 baseline profiles:** High-Energy Pop, Chill Lofi, Deep Intense Rock, Relaxed Jazz, Sad R&B, plus two edge cases. *Unknown Genre (Metal)* uses a genre that is not in the dataset. *Oversized Request* asks for 25 songs when only 20 exist.
- **5 specialized profiles:** one per listening context (see Stretch Feature 2).

Every profile is checked for:

| Check | What it means |
|---|---|
| `engine_ran_without_error` | The engine did not crash (a crash counts as a failure) |
| `returned_requested_count` | Returned `k` songs, or all songs if `k` is larger than the dataset |
| `songs_in_dataset` | Every song's ID **and** title exist in the validated dataset |
| `no_duplicates` | No song appears twice |
| `scores_finite` | Scores are real, finite numbers |
| `explanations_present` | Every song has a non-empty explanation |
| `sorted_by_score` | Results are ranked from highest to lowest score |
| Expectation checks | Top song's genre/mood/energy, or average energy/acousticness/valence, fall in the expected range for that profile |

Expectations describe preference *patterns* (for example, "a workout list should have average energy ≥ 0.75") rather than specific song titles. They were written from each profile's intent before the results were inspected.

### How to run it

```powershell
python -m src.evaluation_runner
```

Options:

```powershell
python -m src.evaluation_runner --no-save                 # print only, don't write JSON
python -m src.evaluation_runner --output my_report.json   # choose output file
python -m src.evaluation_runner --dataset path\to\songs.csv
```

The script prints a readable report and saves `reports/evaluation_results.json`. The JSON has no timestamps, so rerunning it on the same data produces an identical file. The script **exits with code 1 if any profile fails**, so failures cannot silently pass. A test proves this by running the harness on a tiny dataset where most expectations cannot be met.

### Sample evaluation result (actual output)

```text
[PASS] Unknown Genre (Metal)  (mode: baseline, k=5)
       Top pick: Gym Hero (pop, intense) score 2.96
       ok   engine_ran_without_error: no exception
       ok   returned_requested_count: expected 5, got 5
       ok   songs_in_dataset: all songs found in dataset
       ok   no_duplicates: no duplicates
       ok   scores_finite: all scores finite
       ok   explanations_present: all explanations present
       ok   sorted_by_score: scores in descending order
       ok   top_mood_matches: expected 'intense', top song 'Gym Hero' is 'intense'
       ok   top_energy_in_range: expected 0.80-1.00, top song energy is 0.93
...
================================================================
SUMMARY
================================================================
Profiles passed: 12/12 (100%)
Checks passed:   110/110 (100%)
...
Profiles with different results: 5/5 (required: 3)
Context checks met overall: baseline 8/9, specialized 9/9

OVERALL RESULT: PASS
```

The full output is stored in [reports/evaluation_results.json](reports/evaluation_results.json).

## Stretch Feature 2: Specialized Recommendation Mode

> **Honesty note:** No machine-learning model was trained or fine-tuned. VibeFinder is still a rule-based simulation. The specialized mode is a *few-shot-inspired* technique. Hand-written example songs guide the scoring, much like a few-shot prompt guides an AI model with examples.

### How it works (`src/specialization.py`)

1. **Few-shot examples.** Each of 5 listening contexts is described by 3 fictional example songs. The examples have energy, tempo, valence, danceability, acousticness, mood tags, and instruments. None of them are in `data/songs.csv`.

   | Context | Example songs | Typical feel |
   |---|---|---|
   | Focus / Study | Desk Lamp Glow, Notebook Margins, Quiet Algorithm | ~0.37 energy, ~77 BPM, acoustic, "calm/steady" |
   | Workout / High Energy | Last Rep Standing, Sprint Interval, Pulse Check | ~0.91 energy, ~139 BPM, danceable, "energetic/driving" |
   | Relaxation / Chill | Hammock Hours, Low Tide, Tea Steam | ~0.28 energy, ~74 BPM, very acoustic, "peaceful/warm" |
   | Emotional / Reflective | Unsent Postcard, Empty Platform, Faded Porch Light | low valence (~0.30), "bittersweet/melancholy" |
   | Night Drive | Highway Neon, Exit 42, Taillight Trails | ~0.72 energy, ~108 BPM, synth-heavy, "nocturnal" |

2. **Prototype.** The examples are averaged into one prototype per context, and their tags and instruments are collected into keyword lists.
3. **Scoring.** `specialized score = baseline score_song() (unchanged) + context bonus`. The context bonus has three parts:
   - Audio-feature similarity to the prototype: up to **+2.0**. This uses tempo, valence, danceability, and acousticness, which the baseline ignores, plus energy.
   - Shared mood tags with the examples: **+0.5 each, max +1.0**
   - Shared instruments with the examples: **+0.5 each, max +1.0**
4. **Explanation.** Each result shows the baseline reasons, every bonus, and the **closest example song**.

### How it differs from baseline

| | Baseline | Specialized |
|---|---|---|
| Inputs | genre, mood, energy | genre, mood, energy **+ listening context** |
| Features used | genre, mood, energy | adds tempo, valence, danceability, acousticness, mood tags, instruments |
| Max core score | 4.0 | 4.0 + up to 4.0 context bonus |
| Code | `recommend_songs()` (unchanged) | `recommend_songs_specialized()` |

The baseline mode is unchanged and is still the default in the app. In Streamlit, choose **Recommendation mode → Specialized** to reveal a **Listening context** picker.

### Baseline vs specialized example (actual output)

Reflective Evening profile: country / nostalgic / 0.45 energy, with the Emotional / Reflective context.

| Rank | Baseline | Specialized |
|---|---|---|
| 1 | Golden Fields | **Old Photographs** |
| 2 | Old Photographs | Golden Fields |
| 3 | Midnight Coding | **Rainy Window** |
| 4 | Focus Flow | **Quiet Memories** |
| 5 | Coffee Shop Stories | **Library Rain** |

The average valence of the top 5 dropped from 0.62 to 0.47. That means more bittersweet songs, which is what the context asks for.

Across all 5 comparison profiles:

| Profile | Shared songs (of 5) | Positions changed | Top pick changed |
|---|---|---|---|
| Study Session (lofi) | 3 | 2 | no |
| Workout Mix (pop) | 3 | 4 | no |
| Wind Down (jazz) | 2 | 4 | no |
| Reflective Evening (country) | 2 | 5 | yes |
| Night Drive (synthwave) | 3 | 3 | no |

All 5 profiles produced different results (the requirement was at least 3). Some caveats: the top pick usually stays the same, because the user's genre/mood/energy still count. The baseline already met 8 of the 9 context expectations, so on those loose thresholds the specialized mode's clear win is the Reflective profile. In the other profiles it mostly reshuffles positions 2–5.

## Getting Started

### Requirements

- Python 3
- pip
- VS Code or another code editor

### 1. Clone the repository

```powershell
git clone https://github.com/natdeng12/applied-ai-system-project.git
cd applied-ai-system-project
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment (Windows PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Run the application

```powershell
streamlit run app.py
```

Streamlit will open the application in your browser. If it does not open automatically, visit:

`http://localhost:8501`

### 6. Run automated tests

```powershell
python -m pytest
```

### 7. Run the evaluation harness

```powershell
python -m src.evaluation_runner
```

## Project Structure

```text
applied-ai-system-project/
│
├── app.py
├── requirements.txt
├── README.md
├── model_card.md
├── ai_interactions.md
├── vibefinder.log
│
├── data/
│   └── songs.csv
│
├── diagrams/
│   └── architecture.mmd
│
├── reports/
│   └── evaluation_results.json     # output of the evaluation harness
│
├── src/
│   ├── main.py
│   ├── recommender.py
│   ├── specialization.py           # specialized (few-shot-inspired) mode
│   ├── validation.py
│   ├── evaluation.py
│   ├── evaluation_runner.py        # evaluation harness
│   └── logging_config.py
│
└── tests/
    ├── test_recommender.py
    ├── test_validation.py
    ├── test_evaluation.py
    ├── test_evaluation_runner.py
    └── test_specialization.py
```

## Experiments and Evaluation

During development, I experimented with changing the scoring weights to understand how different priorities affect recommendation rankings.

The original scoring rules gave genre a higher weight:

- Genre match: +2.0
- Mood match: +1.0
- Energy similarity: up to +1.0

In the experimental version, I changed the weights:

- Genre match: +1.0
- Mood match: +1.0
- Energy similarity: up to +2.0

The maximum possible score remained 4.0.

The experiment showed that increasing the importance of energy similarity changed some rankings. For example, Corazon de Verano moved above Gym Hero for the High-Energy Pop profile because its energy level was closer to the user's target.

This demonstrated that recommendation results depend on the scoring rules chosen by the developer. A higher score does not necessarily mean a song is objectively better or that a user will enjoy it more.

## Limitations and Risks

VibeFinder has several limitations:

- **Small Dataset:** The application currently uses only 20 songs, which limits recommendation variety.
- **Rule-Based Scoring:** The system uses manually defined scoring rules rather than learning from real listening behavior.
- **Limited Preferences:** The current interface only asks users for genre, mood, and energy preferences.
- **Subjective Preferences:** Music taste is personal, and matching numerical features does not guarantee that someone will enjoy a song.
- **Potential Bias:** The scoring weights influence which songs rank highest. Certain genres or moods may receive an advantage depending on the rules.
- **Limited Generalization:** Results from a small fictional dataset cannot represent the behavior of a real-world music recommendation platform.
- **Specialized Mode Reflects the Author's Taste:** The context example songs were written by hand. They encode one person's idea of what "study" or "workout" music sounds like.
- **Tag Overlap Can Mislead:** Mood tags and instruments are matched as exact words. For example, the Night Drive context ranks *Midnight Coding* (a lofi track) 4th, partly because it shares the tags "mellow" and "late-night" and the instrument "electric piano" with one example song.
- **Loose Evaluation Thresholds:** The harness's expectation ranges are intentionally broad. Passing them shows the results are *reasonable*, not that they are *optimal*.

The reliability system helps identify invalid data and problematic recommendation outputs, but it cannot guarantee that every recommendation is musically relevant or enjoyable.

## Reflection

Building VibeFinder helped me understand how recommendation systems turn data and user preferences into ranked results. Even a relatively simple scoring algorithm can produce different recommendations depending on how its features are weighted.

I also learned that reliability is not just about whether an application runs successfully. The quality of the input data and the validity of the generated output matter too. By adding dataset validation, recommendation checks, logging, and automated tests, I made the application more capable of identifying and handling errors instead of silently accepting potentially unreliable results.

This project also helped me recognize the limitations of rule-based recommendation systems. A high matching score does not necessarily represent someone's actual taste, and the data and rules chosen by a developer can influence what users see.

## Model Card

For more information about the system's intended use, evaluation, limitations, and risks, see [model_card.md](model_card.md).

## AI Development Documentation

For documentation of AI-assisted development and interactions, see [ai_interactions.md](ai_interactions.md).
