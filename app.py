import streamlit as st

from src.recommender import load_songs_with_report, recommend_songs
from src.specialization import SPECIALIZED_PROFILES, recommend_songs_specialized
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

mode = st.radio(
    "Recommendation mode",
    ["Baseline", "Specialized"],
    horizontal=True,
    key="mode",
    help=(
        "Baseline scores songs on genre, mood, and energy only. "
        "Specialized also compares songs to a few example songs for a "
        "listening context. It is rule-based, not a trained AI model."
    ),
)

profile_key = None

# The context picker only appears in Specialized mode to keep the UI simple.
if mode == "Specialized":
    profile_key = st.selectbox(
        "Listening context",
        list(SPECIALIZED_PROFILES.keys()),
        format_func=lambda key: SPECIALIZED_PROFILES[key]["label"],
        key="profile_key",
    )
    st.caption(SPECIALIZED_PROFILES[profile_key]["description"])

vibe_text = f"{genre.title()} · {mood.title()} · {energy:.1f} energy"
if profile_key:
    vibe_text += f" · {SPECIALIZED_PROFILES[profile_key]['label']}"

st.write(f"Your selected vibe: **{vibe_text}**")

st.divider()

st.header("🛡️ Dataset Reliability")

# Start empty so a failed load shows a clear error instead of crashing later.
dataset_songs = []

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
        if profile_key:
            recommendations = recommend_songs_specialized(
                user_preferences,
                dataset_songs,
                profile_key,
                k=5,
            )
            mode_label = f"Specialized: {SPECIALIZED_PROFILES[profile_key]['label']}"
        else:
            recommendations = recommend_songs(
                user_preferences,
                dataset_songs,
                k=5,
            )
            mode_label = "Baseline"

        st.session_state["recommendations"] = recommendations
        st.session_state["user_preferences"] = user_preferences
        st.session_state["mode_label"] = mode_label

    except ValueError as error:
        logger.error("Could not generate recommendations: %s", error)
        st.error(f"Something went wrong: {error}")


if "recommendations" in st.session_state:
    st.divider()
    st.header("🎶 Your Recommendations")
    st.caption(f"Mode: {st.session_state.get('mode_label', 'Baseline')}")

    if st.session_state.get("mode_label", "Baseline") != "Baseline":
        st.info(
            "Specialized scores = baseline score + a bonus for resembling a few "
            "hand-written example songs for this context. This is a rule-based "
            "simulation, not a fine-tuned model."
        )

    for index, (song, score, explanation) in enumerate(
        st.session_state["recommendations"],
        start=1,
    ):
        st.subheader(f"{index}. {song['title']}")
        st.write(f"**Artist:** {song['artist']}")
        st.write(f"**Genre:** {song['genre'].title()}")
        st.write(f"**Match score:** {score:.2f}")
        st.caption(explanation)