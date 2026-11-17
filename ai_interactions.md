# AI Interactions Log

## Agentic Workflow (SF8)

### What task did you give the agent?

I asked my AI coding assistant to expand my VibeFinder music recommender by adding five advanced song attributes and updating the Python scoring logic to use them.

The goal was to make recommendations more detailed while keeping the original three user profiles working.

### Prompts Used

**Prompt 1 – Expand the Dataset**

I asked the AI agent to add five new attributes to all 20 songs in `data/songs.csv`:

- Popularity (0–100)
- Release decade
- Detailed mood tags
- Lyrical theme
- Instrumentation

I also asked it to preserve the original columns, song IDs, and existing values.

**Prompt 2 – Update the Recommender**

I asked the AI agent to update `load_songs()` and `score_song()` in `src/recommender.py`.

The new features needed to be optional so existing user profiles would continue working without additional preferences. I also asked the agent to explain its changes and show examples of advanced user profiles.

### What Did the Agent Generate or Change?

The AI agent made the following changes:

**1. `data/songs.csv`**

- Added five new columns to the existing 20 songs.
- Preserved all original columns and song IDs.
- Added fictional values for popularity, release decade, mood tags, lyrical themes, and instrumentation.

**2. `src/recommender.py`**

- Updated the song-loading logic to support the five new attributes.
- Converted popularity into a numeric value.
- Split mood tags and instrumentation into lists.
- Added a `_clean_list()` helper function to standardize text comparisons.
- Updated `score_song()` to award points for advanced preferences.
- Kept advanced preferences optional so existing profiles could continue working.

### What Did You Verify or Fix Manually?

I checked that:

- The CSV contains exactly 20 songs and 15 columns.
- Song IDs 1–20 remained unchanged.
- The original 10 columns retained their values and order.
- All 20 songs still load successfully.
- The original three profiles continued working without requiring the new attributes.
- The AI agent's scoring calculations and optional preference rules were reviewed.

The initial unit test attempt could not run because pytest was not installed. I installed pytest and ran the tests successfully.

The final automated test suite contains **14 passing tests**:

- Recommendation tests
- Dataset validation tests
- Recommendation output validation tests

I also tested an Advanced Rock profile in `main.py` using all five new song attributes. Storm Runner ranked first with a score of 10.65. I checked the score breakdown and confirmed that popularity, release decade, mood tags, lyrical theme, and instrumentation contributed to the result.

The advanced scoring experiment is separate from the current Streamlit interface, which uses genre, mood, and energy as its main user preferences.

### Reflection

This experience helped me understand how an AI agent can make changes across multiple parts of a project. I learned that I still need to review the generated code, check calculations, and run tests instead of assuming that everything works just because the AI completed the task.

---

## Reliability and Testing System Development

### What Did I Work On?

I used AI assistance to plan and implement a reliability system for VibeFinder.

The goal was to make the application handle invalid dataset records and problematic recommendation results more safely.

### What Was Implemented?

**1. Dataset Validation (`src/validation.py`)**

- Checks for missing required information.
- Checks numerical values and valid ranges.
- Checks release decade formats.
- Identifies duplicate song IDs.
- Excludes invalid records and reports the reasons.

A specific decision was made to exclude all records sharing a duplicated ID rather than arbitrarily keeping one.

**2. Recommendation Output Validation (`src/evaluation.py`)**

- Checks that recommendation scores are valid finite numbers.
- Checks that recommendations belong to the validated dataset.
- Checks for duplicate recommendations.
- Checks that each recommendation has an explanation.
- Ensures the requested recommendation limit is not exceeded.

**3. Logging (`src/logging_config.py`)**

Added logging to record important validation and recommendation events in `vibefinder.log`.

**4. Automated Testing (`tests/`)**

Created tests for recommendation behavior, dataset validation, and recommendation output validation.

The final test run completed successfully with 14 passing tests.

### What Did I Verify Manually?

I tested the validation system using an invalid song record with an energy value outside the permitted 0–1 range.

The system excluded the invalid song, reported the reason, and continued using the remaining valid records.

I also tested duplicate song IDs and confirmed that all records sharing the duplicated ID were excluded.

### Reflection

This work helped me understand that a recommendation system needs more than a scoring algorithm. It also needs to check the quality of its input data and verify the results it produces.

I learned how automated tests can help catch problems early and how logging makes it easier to understand what happens inside an application.

---

## Streamlit Interface Development

### What Did I Work On?

I used AI assistance to plan and build a Streamlit web interface for VibeFinder.

Previously, the project primarily relied on a command-line interface. The goal was to make the recommender easier to use without requiring users to interact with the terminal.

### What Was Implemented?

**`app.py`**

- Added an interactive genre selector.
- Added a mood selector.
- Added an energy slider.
- Added a button to generate recommendations.
- Displayed up to five recommendations with artist names, genres, match scores, and explanations.
- Added dataset reliability metrics showing total, valid, and excluded records.
- Added messages to communicate validation issues and errors.

### What Did I Verify Manually?

I launched the Streamlit application and tested the preference selectors and recommendation button.

I confirmed that the application displayed five recommendations and that the selected preferences remained available during the active session.

### Reflection

This helped me understand how a Python application can be turned into an interactive web interface. I also learned that building a user interface requires connecting user inputs to the existing application logic rather than creating a separate recommendation system.

---

## Design Pattern (SF10)

**Not attempted.**

