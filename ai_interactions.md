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

## Stretch Features: Evaluation Harness and Specialized Mode

### What task did I give the AI?

I asked my AI coding assistant (Claude Code) to add two stretch features to the existing project without rebuilding it:

1. A **test harness / evaluation script** that runs VibeFinder on predefined profiles and reports measurable pass/fail results.
2. A **specialized recommendation mode** based on few-shot examples. I required it to be honest that this is rule-based, not real fine-tuning.

I asked it to work in stages: inspect, plan, build the harness, test, build the specialization, test, run the evaluation, test the Streamlit app, then update the documentation.

### Inspection and plan

The assistant read the code and ran the existing tests first. It confirmed 14 passing tests using the project's `.venv`. It also flagged some issues before writing code:

- `app.py` displayed the "Your Recommendations" section **twice** (a duplicated block). This was fixed while adding the mode selector.
- The app's dropdowns include values that are not in the dataset (genre `electronic`, moods `calm` and `energetic`). This was left unchanged and noted as a limitation.
- The project logger prints INFO messages to the terminal, which would clutter the report. The harness quiets only the console handler, so the log file still records everything.

### What was implemented

**1. `src/evaluation_runner.py`: evaluation harness**

- 12 predefined profiles: 7 baseline and 5 specialized. Examples:
  - `High-Energy Pop`: pop / happy / 0.90. Expects the top song to be pop, happy, with energy 0.70–1.00.
  - `Unknown Genre (Metal)`: a genre that does not exist. Expects an intense, high-energy top song.
  - `Oversized Request (k=25)`: expects all 20 songs back, with no crash and no invented songs.
  - `Workout Mix (pop)` in workout mode: expects average energy ≥ 0.75.
- Checks run independently of the engine's own validation: count, dataset membership (ID **and** title), duplicates, finite scores, explanations, descending order, and expectations.
- A crash is recorded as a failed check instead of being skipped. The script exits with code 1 on any failure.
- It writes `reports/evaluation_results.json` with no timestamps, so reruns produce identical files.
- It compares baseline and specialized results for the same user preferences.

**2. `src/specialization.py`: specialized mode**

- 5 listening contexts, each with 3 fictional example songs. For example, Workout uses "Last Rep Standing," "Sprint Interval," and "Pulse Check."
- The examples are averaged into a prototype. Specialized score = **unchanged baseline score** + similarity bonus (up to +2.0) + shared tags (up to +1.0) + shared instruments (up to +1.0).
- Explanations name the closest example song, for example: *"Closest example song: 'Sprint Interval'"*.

**3. `app.py`**

- Added a "Recommendation mode" toggle (Baseline is the default). The "Listening context" picker appears only in Specialized mode, to avoid clutter.
- Results show which mode produced them, plus a note that the mode is rule-based and not a fine-tuned model.

**4. Tests**

- `tests/test_evaluation_runner.py` (14 tests). These feed the harness deliberately broken recommenders (duplicates, NaN scores, fake songs, wrong count, blank explanations, unsorted output, crashes) and check that each problem is caught. They also check that the CLI exits with code 1 on a dataset where profiles fail.
- `tests/test_specialization.py` (11 tests). These cover the prototype math, that the score equals baseline + bonus, that the baseline is unchanged, that at least 3 profiles differ from baseline, determinism, and invalid input.

### Design decisions and changes during implementation

- **Expectations describe patterns, not song titles.** For example, "top song is lofi" rather than "top song is Library Rain." This tests behavior instead of memorized output. Specialized expectations were written from each context's intent before the results were inspected.
- **Example songs are fictional.** If the examples had been dataset songs, those songs would have trivially ranked first. A test checks that no example title appears in the catalog.
- **Comparison against baseline on the same expectations.** After the first run, every specialized profile passed. The assistant pointed out that this only matters if the baseline would *fail* some of those checks. It added a measurement that applies the same expectations to the baseline output. The result was baseline **8/9** and specialized **9/9**. This was reported honestly rather than tightening thresholds afterwards to create a bigger gap.
- **An observed weakness was documented, not hidden.** Night Drive ranked a lofi song (*Midnight Coding*) 4th because of shared words ("mellow," "late-night," "electric piano") with one example song. The examples were not edited to hide this, since that would be tuning the examples to the test output.
- **A `NameError` workaround was replaced.** An early version of the app change caught `NameError` in case the dataset failed to load. This was replaced with initializing `dataset_songs = []`, so the engine raises its own clear "empty dataset" error.

### Actual evaluation results

```text
Profiles passed: 12/12 (100%)
Checks passed:   110/110 (100%)
Profiles with different results: 5/5 (required: 3)
Context checks met overall: baseline 8/9, specialized 9/9
OVERALL RESULT: PASS
```

Example: Reflective Evening (country / nostalgic / 0.45, Emotional context)

- Baseline: Golden Fields, Old Photographs, Midnight Coding, Focus Flow, Coffee Shop Stories
- Specialized: Old Photographs, Golden Fields, Rainy Window, Quiet Memories, Library Rain
- Average valence of the top 5: 0.62 → 0.47

### What was verified

- The full test suite went from 14 to **39 passing tests**. All original tests are unchanged and still pass.
- The evaluation harness was run twice, and the JSON files were byte-identical.
- The Streamlit app was tested headlessly with Streamlit's `AppTest`. It was clicked in both modes with no exceptions, and the results header now appears once. The real server also started and passed its health check.

### Reflection

The most useful part of this process was questioning a result that looked too good. "All specialized checks pass" sounded impressive. Comparing against the baseline showed that the thresholds were loose and the real improvement was smaller. Documenting that honestly is more valuable than a 100% number with no context.

---

## Design Pattern (SF10)

**Not attempted.**

