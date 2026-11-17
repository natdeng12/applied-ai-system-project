import streamlit as st

from src.recommender import load_songs_with_report, recommend_songs
from src.logging_config import setup_logging


# Set up logging
logger = setup_logging()

# Configure the webpage
st.set_page_config(
    page_title="VibeFinder",
    page_icon="🎵",
    layout="wide",
)

# App heading
st.title("🎵 VibeFinder")
st.subheader("Find music that matches your vibe.")

st.write(
    "Tell us what kind of music you're in the mood for, "
    "and VibeFinder will recommend songs based on your preferences."
)

st.divider()

st.header("🎧 Customize Your Vibe")

genre = st.selectbox(
    "What's your favorite genre?",
    ["pop", "rock", "lofi", "hip-hop", "jazz", "classical", "electronic"],
    key="genre",
)

mood = st.selectbox(
    "What mood are you looking for?",
    ["happy", "calm", "energetic", "sad", "focused", "romantic"],
    key="mood",
)

energy = st.slider(
    "How energetic should the music be?",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    key="energy",
)

st.write(f"Your selected vibe: **{genre.title()} · {mood.title()} · {energy:.1f} energy**")

st.divider()

st.header("🛡️ Dataset Reliability")

try:
    dataset_songs, dataset_issues = load_songs_with_report("data/songs.csv")

    total_songs = len(dataset_songs) + len(dataset_issues)
    valid_count = len(dataset_songs)
    excluded_count = len(dataset_issues)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Songs Checked", total_songs)
    col2.metric("Valid Songs", valid_count)
    col3.metric("Excluded Songs", excluded_count)

    if excluded_count == 0:
        st.success("All dataset records passed validation!")
    else:
        st.warning(f"{excluded_count} song(s) were excluded.")

        with st.expander("View validation issues"):
            for issue in dataset_issues:
                st.write(
                    f"Row {issue['row']} — {issue['title']}: "
                    f"{', '.join(issue['reasons'])}"
                )

except (ValueError, FileNotFoundError) as error:
    logger.error("Dataset validation failed: %s", error)
    st.error(f"Could not validate the dataset: {error}")



if st.button("🎵 Find My Songs"):
    user_preferences = {
        "genre": genre,
        "mood": mood,
        "energy": energy,
    }

    try:
        recommendations = recommend_songs(
            user_preferences,
            dataset_songs,
            k=5,
        )

        st.session_state["recommendations"] = recommendations
        st.session_state["user_preferences"] = user_preferences

    except ValueError as error:
        logger.error("Could not generate recommendations: %s", error)
        st.error(f"Something went wrong: {error}")


if "recommendations" in st.session_state:
    st.divider()
    st.header("🎶 Your Recommendations")

    for index, (song, score, explanation) in enumerate(
        st.session_state["recommendations"],
        start=1,
    ):
        st.subheader(f"{index}. {song['title']}")
        st.write(f"**Artist:** {song['artist']}")
        st.write(f"**Genre:** {song['genre'].title()}")
        st.write(f"**Match score:** {score:.2f}")
        st.caption(explanation)


if "recommendations" in st.session_state:
    st.divider()
    st.header("🎶 Your Recommendations")

    for index, (song, score, explanation) in enumerate(
        st.session_state["recommendations"],
        start=1,
    ):
        st.subheader(f"{index}. {song['title']}")
        st.write(f"**Artist:** {song['artist']}")
        st.write(f"**Genre:** {song['genre'].title()}")
        st.write(f"**Match score:** {score:.2f}")
        st.caption(explanation)