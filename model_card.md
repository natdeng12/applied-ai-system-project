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

The automated test suite currently contains **14 passing tests**.

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