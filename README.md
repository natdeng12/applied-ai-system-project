# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world music recommendation systems, such as Spotify, use information about users' listening behavior and song characteristics to predict what they might enjoy. They may combine collaborative filtering, which recommends music based on the preferences of similar users, with content-based filtering, which recommends songs based on their features. My Music Recommender Simulation will initially prioritize content-based filtering. It will compare a user's music preferences with each song's characteristics, calculate a matching score, and rank songs from the highest score to the lowest. This will allow the system to recommend songs that best match the user's preferred music style and mood.

### Song Features

Each `Song` object will use:

- `id` – Unique song identifier
- `title` – Song title
- `artist` – Artist name
- `genre` – Music genre
- `mood` – Song mood
- `energy` – Energy level (0–1)
- `tempo_bpm` – Speed of the song in beats per minute
- `valence` – How positive or happy the song sounds (0–1)
- `danceability` – How suitable the song is for dancing (0–1)
- `acousticness` – How acoustic the song sounds (0–1)

### UserProfile Features

Each `UserProfile` object will store the user's music preferences:

- `preferred_genres` – Genres the user enjoys
- `preferred_moods` – Moods the user prefers
- `preferred_energy` – Preferred energy level (0–1)
- `preferred_tempo_bpm` – Preferred song speed
- `preferred_valence` – Preferred positivity or happiness level (0–1)

Algorithm Recipe – Version 1

The recommender will use content-based filtering to compare each song with the user's taste profile.

Each song will receive points using three scoring rules:

Genre Match: Award 2.0 points if the song's genre matches the user's preferred genre.

Mood Match: Award 1.0 point if the song's mood matches the user's preferred mood.

Energy Similarity: Award up to 1.0 point based on how close the song's energy is to the user's target energy.

Energy similarity formula:

Energy Score = 1 - abs(song_energy - preferred_energy)

The three scores will be added together, giving each song a maximum possible score of 4.0 points.

The program will calculate scores for all songs and rank them from highest to lowest. If songs have the same score, the song with energy closer to the user's target will rank higher. If they are still tied, the lower song ID will come first. The system will display the top 5 recommendations.

Potential Biases and Limitations

The scoring system gives genre more importance than mood and energy combined. This could cause the recommender to prioritize a song that matches the user's preferred genre while overlooking another song that better matches their mood and energy.

The initial dataset also contains only one rock song and two intense songs, which limits how much genre and mood matching can influence the recommendations. Additionally, Version 1 only considers genre, mood, and energy, ignoring other song features such as tempo, valence, danceability, and acousticness.

Future versions may adjust the scoring weights, expand the dataset, and include additional song features to improve recommendation variety and accuracy.
---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

## Sample Recommendation Output

The following is an example of the program's terminal output using the default user profile (`pop`, `happy`, energy `0.8`).

```text
========================================
       TOP SONG RECOMMENDATIONS
========================================

1. Sunrise City
   Score:   3.98
   Reasons: Genre matches (+2.0); Mood matches (+1.0); Energy similarity (+0.98)

2. Gym Hero
   Score:   2.87
   Reasons: Genre matches (+2.0); Energy similarity (+0.87)

3. Rooftop Lights
   Score:   1.96
   Reasons: Mood matches (+1.0); Energy similarity (+0.96)

4. Corazon de Verano
   Score:   1.92
   Reasons: Mood matches (+1.0); Energy similarity (+0.92)

5. City Dreams
   Score:   0.98
   Reasons: Energy similarity (+0.98)

========================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



