# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

## 2. Intended Use

VibeFinder is a beginner-friendly music recommendation simulation designed to suggest songs based on a user's preferred genre, mood, and energy level.

The system assumes users can describe some of their music preferences. It is intended for classroom exploration and learning about how recommendation algorithms work, not for commercial music streaming.

## 3. How the Model Works

This recommender uses a content-based filtering approach. It compares the features of each song with the user's preferences to calculate a recommendation score.

The scoring system uses three rules:

1. **Genre match (+2.0):** A song receives 2 points if its genre matches the user's preferred genre.
2. **Mood match (+1.0):** A song receives 1 point if its mood matches the user's preferred mood.
3. **Energy similarity (up to +1.0):** The system compares the song's energy level with the user's preferred energy. The closer the values are, the higher the score.

The system adds these points together to calculate each song's final score. It then sorts songs from highest to lowest score and returns the top five recommendations.

Each recommendation includes an explanation showing which scoring rules contributed to its score. Compared with the starter logic, the implementation loads songs from a CSV file, calculates preference-based scores, ranks the songs, and generates explanations for the recommendations.

## 4. Data

The recommender uses a CSV dataset containing 20 fictional songs.

Each song includes information such as title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.

The catalog includes different genres and moods, such as pop, rock, lofi, jazz, ambient, synthwave, hip-hop, and Latin music.

The original dataset contained 10 songs, and 10 additional fictional songs were added to expand the catalog.

Although the dataset includes several musical features, the current scoring algorithm only considers genre, mood, and energy. The catalog is relatively small and does not represent every genre or musical preference equally.

## 5. Strengths

The system is simple, understandable, and easy to test. It can identify songs that match a user's preferred genre and mood while also considering energy similarity.

One strength is that every recommendation includes an explanation, allowing users to understand why a song received its score.

In testing, the default pop/happy profile ranked songs such as Sunrise City and Gym Hero near the top, which matched the expected preferences.

## 6. Limitations and Bias

The recommender only considers genre, mood, and energy when calculating scores. It does not currently use tempo, valence, danceability, or acousticness.

The dataset is small, and some genres and moods have fewer songs than others. This can affect the variety of recommendations.

The genre match is weighted more heavily than the mood match, meaning the system may favor a genre match even when another song has a closer mood or energy level.

The system also uses manually defined preferences rather than learning from listening history or feedback.

1. With a thin dataset, energy decides most recommendations.
Most genres and moods have only 0–1 songs, so for most users genre and mood stop counting after the first song or two. Energy, now worth up to 2.0, decides the rest. That produces recommendations with the right energy but the wrong style: a metal fan gets happy Latin pop, and a classical listener gets sad R&B. This is the clearest example of your data and your weights working together to create bias.

2. Genre and mood matching is exact, so it's all-or-nothing.
indie pop ≠ pop and relaxed ≠ chill. Users get rewarded only if their taste uses the dataset's exact labels. Everyone else, including fans of missing genres, people with several favorites, and people using similar words, gets weaker recommendations. It also creates a mild filter bubble, because the system only rewards "exactly the same," never "similar" or "new."




## 7. Evaluation

## Evaluation

### User Profiles Tested

I tested the recommender using three different user profiles:

- **High-Energy Pop:** Pop genre, happy mood, and energy level of 0.90.
- **Chill Lofi:** Lofi genre, chill mood, and energy level of 0.35.
- **Deep Intense Rock:** Rock genre, intense mood, and energy level of 0.88.

Each profile returned a different set of recommendations, showing that the system responds to changes in genre, mood, and energy preferences.

### Comparing the Results

**1. High-Energy Pop vs. Chill Lofi**

The High-Energy Pop profile recommended songs such as "Sunrise City" and "Corazon de Verano," while the Chill Lofi profile ranked "Library Rain" and "Midnight Coding" highest. This makes sense because the first profile prefers happy, energetic pop music, while the second prefers calmer lofi music. The different genre, mood, and energy preferences changed which songs received the most points.

**2. High-Energy Pop vs. Deep Intense Rock**

The High-Energy Pop profile ranked "Sunrise City" first, while the Deep Intense Rock profile ranked "Storm Runner" first. Both profiles have high energy preferences, but their genre and mood preferences are different. An interesting result was that "Gym Hero" also ranked highly for the High-Energy Pop profile even though its mood is intense rather than happy. This happened because it matched the pop genre and had an energy level close to the user's preference.

**3. Chill Lofi vs. Deep Intense Rock**

The Chill Lofi profile ranked "Library Rain" first, while the Deep Intense Rock profile ranked "Storm Runner" first. Their results are very different because one profile prefers low-energy, chill music and the other prefers high-energy, intense rock. This shows how the energy preference can help distinguish between users who want relaxing music and users who want more intense music.

### Surprising Findings

One surprising result was that a song could rank highly even when it did not match the user's preferred mood or genre. For example, "Gym Hero" received a high score for the High-Energy Pop profile because it matched the pop genre and had very similar energy. This demonstrates that energy similarity can influence rankings even when other preferences do not match.

In the weight-shift experiment, I increased the importance of energy and reduced the importance of genre. "Corazon de Verano" moved above "Gym Hero" for the High-Energy Pop profile because its energy was closer to the target. However, the top recommendation for each profile stayed the same. This showed me that changing scoring weights can affect the order of recommendations, but a different ranking does not automatically mean the recommendations are more accurate.

### Overall Evaluation

The recommender successfully changes its recommendations based on different user preferences. However, it only compares three features: genre, mood, and energy. It does not actually understand the sound, lyrics, or personal meaning of a song. The results are useful for demonstrating a basic content-based recommendation system, but they should not be treated as perfect predictions of someone's musical taste.

## 8. Future Work

Future improvements could include:

- Using additional song features such as tempo, valence, danceability, and acousticness.
- Allowing users to select different preference profiles.
- Improving recommendation diversity so the results are not overly focused on one genre.
- Adding user feedback, such as likes and dislikes, to improve future recommendations.
- Developing a graphical user interface instead of relying only on the terminal.

## 9. Personal Reflection

This project helped me understand how recommendation systems use data and user preferences to suggest content. I learned that even a simple scoring algorithm can produce personalized recommendations by comparing song features.

I also discovered that the weights assigned to different preferences can significantly affect the results. This helped me understand why real-world recommendation systems need careful testing and evaluation.