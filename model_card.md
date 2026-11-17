# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0**

## 2. Intended Use

VibeFinder is a beginner-friendly music recommendation simulation designed to suggest songs based on a user's preferred genre, mood, and energy level.

The system is intended for classroom exploration and learning about content-based recommendation algorithms. It is not designed for commercial music streaming or professional music discovery.

## 3. How the System Works

VibeFinder uses a content-based filtering approach. It compares the features of songs with a user's selected preferences to calculate recommendation scores.

The current Streamlit application uses three main scoring rules:

1. **Genre match (+1.0):** A song receives 1 point if its genre matches the user's preferred genre.
2. **Mood match (+1.0):** A song receives 1 point if its mood matches the user's preferred mood.
3. **Energy similarity (up to +2.0):** The system compares the song's energy level with the user's preferred energy. The closer the values are, the higher the score.

Energy similarity is calculated using:

`2.0 × (1 - abs(song_energy - preferred_energy))`

The scores are added together. Songs are sorted from highest to lowest score, and the application returns up to five recommendations.

Each recommendation includes an explanation showing the matching preferences and its score.

The project also contains optional scoring logic for additional song attributes, such as popularity, release decade, mood tags, lyrical themes, and instrumentation. However, these additional attributes are not currently exposed as preferences in the Streamlit interface.

VibeFinder is a rule-based recommendation simulation, not a trained machine-learning model. It does not learn from user listening histories or automatically adjust its scoring rules.

VibeFinder also has an optional **specialized mode** that adjusts scoring for a chosen listening context, such as Focus / Study or Workout. It uses hand-written example songs and is still rule-based. No model was trained or fine-tuned. See Section 13.

## 4. Data

The recommender uses a CSV dataset containing 20 fictional songs and 15 columns.

The dataset includes:

- Song ID
- Title
- Artist
- Genre
- Mood
- Energy
- Tempo (BPM)
- Valence
- Danceability
- Acousticness
- Popularity
- Release decade
- Mood tags
- Lyrical theme
- Instrumentation

The catalog includes different genres and moods, such as pop, rock, lofi, jazz, hip-hop, and Latin music.

The original dataset contained 10 songs. Ten additional fictional songs were added to expand the catalog and provide more variety.

Although the dataset contains several musical attributes, the current Streamlit recommendation flow primarily uses genre, mood, and energy.

The catalog is relatively small and does not represent every genre or musical preference equally.

## 5. Strengths

The system is simple, understandable, and easy to test. It can identify songs that match a user's preferred genre and mood while also considering energy similarity.

One strength is that every recommendation includes an explanation, allowing users to understand why a song received its score.

The application also includes a reliability system that checks input data and generated recommendations. Invalid dataset records can be excluded and reported, helping prevent problematic records from being used in the recommendation process.

The Streamlit interface makes the system easier to interact with by allowing users to select preferences and view recommendations without using the terminal.

## 6. Limitations and Bias

VibeFinder has several limitations.

### Small Dataset

The dataset contains only 20 songs. Some genres and moods have fewer examples than others, which limits recommendation variety and may cause certain preferences to receive fewer relevant results.

### Rule-Based Scoring

The system uses manually defined scoring rules rather than learning from listening history or user feedback.

The scoring weights influence which songs rank highest. A higher score does not necessarily mean a user will enjoy a song more.

### Energy Can Have a Strong Influence

Energy similarity contributes up to 2.0 points, while genre and mood each contribute 1.0 point.

As a result, energy can have a significant influence on rankings. A song with a close energy match may rank highly even if it does not match the user's preferred genre or mood.

For example, a high-energy pop preference may produce a recommendation with a matching genre and energy level but a different mood.

### Exact Matching

Genre and mood matching use exact labels. For example, "indie pop" is not automatically treated as "pop," and "relaxed" is not automatically treated as "calm."

Users whose preferences do not match the dataset's exact labels may receive weaker recommendations.

This can also contribute to a filter bubble because the system rewards exact matches rather than exploring related genres, moods, or unfamiliar music.

### Limited Understanding of Music

The system does not actually understand a song's sound, lyrics, or personal meaning. It relies on the attributes recorded in the dataset.

The reliability system can identify invalid data and problematic recommendation outputs, but it cannot guarantee that recommendations are musically relevant or enjoyable.

## 7. Evaluation

### User Profiles Tested

I tested the recommender using three different user profiles:

- **High-Energy Pop:** Pop genre, happy mood, and energy level of 0.90.
- **Chill Lofi:** Lofi genre, chill mood, and energy level of 0.35.
- **Deep Intense Rock:** Rock genre, intense mood, and energy level of 0.88.

Each profile returned a different set of recommendations, showing that the system responds to changes in genre, mood, and energy preferences.

### Comparing the Results

**1. High-Energy Pop vs. Chill Lofi**

The High-Energy Pop profile recommended songs such as "Sunrise City" and "Corazon de Verano," while the Chill Lofi profile ranked "Library Rain" and "Midnight Coding" highly.

This makes sense because the first profile prefers happy, energetic pop music, while the second prefers calmer lofi music. The different genre, mood, and energy preferences changed which songs received the most points.

**2. High-Energy Pop vs. Deep Intense Rock**

The High-Energy Pop profile ranked "Sunrise City" first, while the Deep Intense Rock profile ranked "Storm Runner" first.

Both profiles have high energy preferences, but their genre and mood preferences are different.

An interesting result was that "Gym Hero" also ranked highly for the High-Energy Pop profile even though its mood is intense rather than happy. This happened because it matched the pop genre and had an energy level close to the user's preference.

**3. Chill Lofi vs. Deep Intense Rock**

The Chill Lofi profile ranked "Library Rain" first, while the Deep Intense Rock profile ranked "Storm Runner" first.

Their results are very different because one profile prefers low-energy, chill music and the other prefers high-energy, intense rock. This shows how energy preference helps distinguish between users who want relaxing music and users who want more intense music.

### Scoring Weight Experiment

During development, I experimented with changing the scoring weights to understand how different priorities affect recommendation rankings.

The original scoring rules were:

- Genre match: +2.0
- Mood match: +1.0
- Energy similarity: up to +1.0

In the experimental version, I changed the weights to:

- Genre match: +1.0
- Mood match: +1.0
- Energy similarity: up to +2.0

The maximum possible score remained 4.0.

For the High-Energy Pop profile, "Corazon de Verano" moved above "Gym Hero" because its energy level was closer to the user's target. However, the top recommendation for each tested profile stayed the same.

This demonstrated that changing scoring weights can affect the order of recommendations, but a different ranking does not automatically mean the recommendations are more accurate.

### Reliability Evaluation

The project also includes automated tests for its reliability system.

The dataset validation checks for missing required information, invalid numerical values, invalid release decade formats, and duplicate song IDs.

When multiple records share a duplicate ID, all records with that ID are excluded. Other valid records remain available for recommendations.

The recommendation validation checks that generated results contain valid scores and explanations, do not exceed the requested recommendation limit, do not contain duplicate songs, and only include songs from the validated dataset.

The automated test suite originally contained 14 passing tests. After the stretch features were added, it contains **39 passing tests**: the original 14, 14 for the evaluation harness, and 11 for the specialized mode. A separate evaluation harness also tests end-to-end behavior on 12 profiles (see Section 14).

Manual testing also confirmed that an invalid song record was excluded while valid songs remained available for recommendations.

### Overall Evaluation

VibeFinder successfully changes its recommendations based on different user preferences. It demonstrates how a content-based recommendation system can compare song attributes and rank results using manually defined scoring rules.

However, it does not actually understand the sound, lyrics, or personal meaning of a song. Its small dataset and fixed scoring rules limit its ability to represent individual music preferences.

The reliability system improves how the application handles invalid data and checks recommendation outputs, but it cannot guarantee that every recommendation is a good match.

The results are useful for demonstrating a basic content-based recommendation system, but they should not be treated as perfect predictions of someone's musical taste.

## 8. Future Work

Potential improvements include:

- Expanding the dataset with more songs and a wider variety of genres and moods.
- Allowing users to select additional preferences, such as tempo, popularity, and instrumentation.
- Improving recommendation diversity so the results are not overly focused on one genre.
- Adding user feedback, such as likes and dislikes, to improve future recommendations.
- Exploring more advanced recommendation methods that can learn from user behavior.
- Improving evaluation with a larger set of test profiles and measurable recommendation-quality criteria.

## 9. Personal Reflection

This project helped me understand how recommendation systems use data and user preferences to suggest content. I learned that even a simple scoring algorithm can produce personalized recommendations by comparing song features.

I also discovered that the weights assigned to different preferences can significantly affect the results. This helped me understand why recommendation systems need careful testing and evaluation.

Another important lesson was that reliability is not just about whether an application runs successfully. The quality of the input data and the validity of generated outputs matter too.

By adding dataset validation, recommendation checks, logging, and automated tests, I made the application more capable of identifying and handling errors instead of silently accepting potentially unreliable results.

This project also helped me recognize the limitations of rule-based recommendation systems. A high matching score does not necessarily represent someone's actual taste, and the data and rules chosen by a developer can influence what users see.

## 10. Ethical Considerations and Potential Misuse

VibeFinder is designed as an educational music recommendation project, but its recommendations could still be misunderstood or overtrusted. For example, users might assume that a higher-scoring song is objectively better or that the system fully understands their musical preferences.

The system could also contribute to a filter bubble by repeatedly prioritizing songs that match exact genre and mood labels instead of introducing users to different styles of music.

To reduce these risks, VibeFinder provides explanations for its recommendations and makes its scoring rules transparent. The application is intended for educational exploration rather than professional music discovery. It does not collect personal listening histories or make decisions that significantly affect users' lives.

## 11. What Surprised Me During Reliability Testing

One thing that surprised me was how important data validation became, even with a relatively small dataset. A single invalid record could affect the recommendation process if the system accepted it without checking.

During testing, I confirmed that the system could exclude an invalid song while keeping the remaining valid songs available for recommendations. I also tested duplicate song IDs and discovered that keeping only one record would not be a consistent solution. Instead, I decided to exclude every record sharing a duplicate ID.

This showed me that reliability involves more than checking whether the application runs. The system also needs to identify problematic data, explain what went wrong, and handle errors without unnecessarily stopping the entire application.

## 12. Collaboration with AI

I used AI as a development assistant throughout this project to help explain coding concepts, troubleshoot errors, suggest improvements, and develop the reliability system.

One suggestion I accepted was adding a dataset validation process that checks song records before they enter the recommendation engine. This helped the application identify missing information, invalid values, and duplicate IDs instead of silently processing unreliable data.

One suggestion I changed was the scope of the Streamlit interface. Although the project contains additional scoring features for popularity, release decade, mood tags, lyrical themes, and instrumentation, I kept the main interface focused on genre, mood, and energy. I chose this simpler approach to keep the application understandable and focused on the project's main goal rather than adding too many controls.

This collaboration taught me that AI-generated suggestions should not be accepted automatically. I needed to evaluate whether each suggestion was accurate, understandable, appropriate for my skill level, and aligned with the project's requirements.

## 13. Specialized Recommendation Mode

### What it is

The specialized mode lets a user pick a **listening context** in addition to genre, mood, and energy:

- Focus / Study
- Workout / High Energy
- Relaxation / Chill
- Emotional / Reflective
- Night Drive

**No model training or fine-tuning occurred.** The approach is *few-shot-inspired*. Each context is defined by three hand-written, fictional example songs that are not in the dataset. The examples are averaged into a "prototype" for that context. Each song's specialized score is:

`baseline score (unchanged genre + mood + energy rules) + context bonus`

The context bonus has three parts:

- **Audio-feature similarity to the prototype (up to +2.0):** energy, tempo, valence, danceability, and acousticness. Tempo is divided by 200 so it is on a 0–1 scale.
- **Shared mood tags with the examples:** +0.5 each, up to +1.0.
- **Shared instruments with the examples:** +0.5 each, up to +1.0.

Each explanation lists every bonus and names the closest example song, so users can see why a song was chosen. The baseline mode is unchanged and is still the default.

### Intended use

The mode is for classroom demonstration of how context and example-based templates can change recommendations. It is not meant to predict what any real person wants to hear while studying or exercising.

### Limitations

- **The examples are the author's opinion.** Three example songs per context is a very small sample. It encodes one person's idea of what "study music" or "workout music" sounds like.
- **Exact tag matching.** Tags and instruments only count when the words match exactly. This can cause odd results. Night Drive ranked *Midnight Coding* (a lofi track) 4th, partly because it shares the words "mellow," "late-night," and "electric piano" with one example song. Night Drive's average acousticness also went *up* slightly (0.26 → 0.31), the opposite of the intended direction.
- **Mood semantics are ignored.** For the Study profile, *Rainy Window* (a sad R&B song) entered the top 5 because its audio features are calm. The system does not know that "sad" may be distracting for studying.
- **Small catalog.** With only 20 songs, the same few low-energy acoustic songs appear in several contexts.
- **Weights were chosen by hand.** The context bonus (up to 4.0) was set to roughly equal the baseline core rules (4.0). Different weights would produce different rankings.

### Potential bias

The context templates favor the instruments and tags used in the examples, such as synthesizers for Night Drive and 808 bass for Workout. Genres whose songs use other instruments (for example, acoustic genres in a workout context) are less likely to receive the tag/instrument bonus. Because the example songs and catalog songs were written with overlapping vocabulary, the bonus partly measures how closely the author's word choices line up between the two.

### Measured results

Each specialized test profile was run in both modes with identical user preferences:

| Profile (context) | Baseline top pick | Specialized top pick | Shared songs (of 5) | Positions changed |
|---|---|---|---|---|
| Study Session (Focus / Study) | Focus Flow | Focus Flow | 3 | 2 |
| Workout Mix (Workout) | Sunrise City | Sunrise City | 3 | 4 |
| Wind Down (Relaxation) | Coffee Shop Stories | Coffee Shop Stories | 2 | 4 |
| Reflective Evening (Emotional) | Golden Fields | Old Photographs | 2 | 5 |
| Night Drive (Night Drive) | Night Drive Loop | Night Drive Loop | 3 | 3 |

- **5 of 5 profiles** produced different top-5 lists (the requirement was at least 3).
- Average features shifted in the intended direction for most contexts. Study energy went from 0.51 to 0.41, Workout energy from 0.83 to 0.87, Wind Down energy from 0.41 to 0.35, and Reflective valence from 0.62 to 0.47.
- On the harness's context expectations, the baseline met **8/9** and the specialized mode met **9/9**. The thresholds are broad, so the baseline already does reasonably well, and the clear threshold-level improvement is the Reflective profile. The top pick changed in only 1 of 5 profiles, because the user's genre, mood, and energy still carry significant weight.

## 14. Evaluation Harness Results

`src/evaluation_runner.py` runs 12 predefined profiles: 7 baseline (including an unknown-genre case and an oversized `k=25` request) and 5 specialized. Each profile is checked for correct count, dataset membership, duplicates, finite scores, explanations, descending order, and profile-specific expectations. The harness exits with an error code if any check fails.

Actual results on the current dataset:

- **Profiles passed:** 12/12 (100%)
- **Individual checks passed:** 110/110 (100%)
- **Baseline vs specialized comparison:** 5/5 profiles differ (required: 3)

These results mean the system behaves *consistently and reasonably* on these profiles. They do not prove the recommendations are *good* for real listeners. The expectation ranges are broad and were written by the developer, and the dataset is small and fictional. Full results are in `reports/evaluation_results.json`.
