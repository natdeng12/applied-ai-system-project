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
├── src/
│   ├── main.py
│   ├── recommender.py
│   ├── validation.py
│   ├── evaluation.py
│   └── logging_config.py
│
└── tests/
    ├── test_recommender.py
    ├── test_validation.py
    └── test_evaluation.py
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

The reliability system helps identify invalid data and problematic recommendation outputs, but it cannot guarantee that every recommendation is musically relevant or enjoyable.

## Reflection

Building VibeFinder helped me understand how recommendation systems turn data and user preferences into ranked results. Even a relatively simple scoring algorithm can produce different recommendations depending on how its features are weighted.

I also learned that reliability is not just about whether an application runs successfully. The quality of the input data and the validity of the generated output matter too. By adding dataset validation, recommendation checks, logging, and automated tests, I made the application more capable of identifying and handling errors instead of silently accepting potentially unreliable results.

This project also helped me recognize the limitations of rule-based recommendation systems. A high matching score does not necessarily represent someone's actual taste, and the data and rules chosen by a developer can influence what users see.

## Model Card

For more information about the system's intended use, evaluation, limitations, and risks, see [model_card.md](model_card.md).

## AI Development Documentation

For documentation of AI-assisted development and interactions, see [ai_interactions.md](ai_interactions.md).
