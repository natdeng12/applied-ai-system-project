# AI Interactions Log

## Agentic Workflow (SF8)

### What task did you give the agent?

I asked my AI coding assistant to expand my VibeFinder music recommender by adding five advanced song attributes and updating the Python scoring logic to use them.

The goal was to make recommendations more detailed while keeping the original three user profiles working.

### Prompts used:

**Prompt 1 – Expand the dataset**

I asked the AI agent to add five new attributes to all 20 songs in `data/songs.csv`:

- Popularity (0–100)
- Release decade
- Detailed mood tags
- Lyrical theme
- Instrumentation

I also asked it to preserve the original columns, song IDs, and existing values.

**Prompt 2 – Update the recommender**

I asked the AI agent to update `load_songs()` and `score_song()` in `src/recommender.py`.

The new features needed to be optional so existing user profiles would continue working without additional preferences. I also asked the agent to explain its changes and show examples of advanced user profiles.

### What did the agent generate or change?

The AI agent made the following changes:

**1. `data/songs.csv`**
- Added five new columns to the existing 20 songs.
- Preserved all original columns and song IDs.
- Added fictional values for popularity, release decade, mood tags, lyrical themes, and instrumentation.

**2. `src/recommender.py`**
- Updated `load_songs()` to load the five new attributes.
- Converted popularity into an integer.
- Split mood tags and instrumentation into lists.
- Added a `_clean_list()` helper function to standardize text comparisons.
- Updated `score_song()` to award points for advanced preferences.
- Kept advanced preferences optional so existing profiles still work.

### What did you verify or fix manually?

I checked that:

- The CSV contains exactly 20 songs and 15 columns.
- Song IDs 1–20 remained unchanged.
- The original 10 columns retained their values and order.
- All 20 songs still load successfully.
- The original three profiles produced the same recommendation scores as before.
- The AI agent's scoring calculations and optional preference rules were reviewed.

The initial unit test attempt could not run because pytest was not installed. I then installed pytest and ran the tests. [Add the actual test result here.]

I also reviewed the AI-generated code to understand how the new attributes are loaded and used in the scoring process.

I also tested an Advanced Rock profile in `main.py` using all five new song attributes. Storm Runner ranked first with a score of 10.65. I checked the score breakdown and confirmed that popularity, release decade, mood tags, lyrical theme, and instrumentation all contributed correctly. The original three profiles also continued producing their expected recommendations without requiring the new attributes.

### Reflection

This experience helped me understand how an AI agent can make changes across multiple parts of a project. I learned that I still need to review the generated code, check calculations, and run tests instead of assuming that everything works just because the AI completed the task.

---

## Design Pattern (SF10)

Empty, did not attempt