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

## 7. Evaluation

The system was evaluated by running the Python program in the terminal using the default pop/happy profile with an energy preference of 0.8.

Individual song scores were also tested to verify that genre, mood, and energy contributed the expected points.

The results were checked to make sure songs were ranked from highest to lowest score and that each recommendation displayed its scoring explanations.

For the default profile, Sunrise City received the highest score because it matched both the preferred genre and mood and had a similar energy level.

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