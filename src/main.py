"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_profiles = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.90
    },

    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35
    },

    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.88
    },
    
    "Advanced Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.88,
        "min_popularity": 60,
        "preferred_decade": "2010s",
        "preferred_mood_tags": ["driving", "defiant"],
        "preferred_lyrical_theme": "freedom",
        "preferred_instruments": ["electric guitar", "drums"]
    }
    
}

    for profile_name, user_prefs in user_profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\n" + "=" * 50)
        print(f"PROFILE: {profile_name}")
        print("=" * 50)

        for number, rec in enumerate(recommendations, start=1):
            song, score, explanation = rec

            print(f"\n{number}. {song['title']}")
            print(f"   Score:   {score:.2f}")
            print(f"   Reasons: {explanation}")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
