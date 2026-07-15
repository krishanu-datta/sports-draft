---
title: Draft winners losers subagent research
description: Research findings for planning a Streamlit page that ranks drafters by summed win probabilities of drafted teams
ms.date: 2026-07-15
ms.topic: reference
---

## Research scope

Investigate the current workspace to plan a Streamlit enhancement that adds a post-draft winners/losers page.

Research questions:

1. What is the current architecture and state flow in draft.py, including how picks and probabilities are represented?
2. What data model constraints could affect winner aggregation correctness?
3. What is the safest implementation approach with concrete insertion points?
4. What local validation commands are available?

## Findings

### Current architecture and state flow

The app is a single-file Streamlit state machine in draft.py with three page states.

* Setup page gate: st.session_state.page defaults to "setup" in draft.py:49-50.
* Setup inputs and draft bootstrapping happen in draft.py:100-229.
* Draft room flow and pick mutation happen in draft.py:237-483.
* Finished view and CSV export happen in draft.py:491-534.

Draft state objects and transitions:

* Drafters are stored in st.session_state.players in draft.py:213.
* Draft order settings are st.session_state.snake and st.session_state.rounds in draft.py:214-215.
* Available draft pool is st.session_state.data, a DataFrame with columns team, prob, league, created in draft.py:169-174 and assigned in draft.py:217.
* Picks are stored as a dict of lists keyed by drafter name in st.session_state.drafts (example shape: {"A": ["Team1", ...]}) in draft.py:219-222.
* Current position is tracked via st.session_state.round and st.session_state.pick in draft.py:224-225.
* Page transition setup -> draft happens in draft.py:227.
* Page transition draft -> finished happens when round exceeds rounds in draft.py:434-439.

How picks are stored:

* On draft click, only row["team"] is appended to the drafter list in draft.py:408-412.
* The selected row is dropped from st.session_state.data by index in draft.py:415-418.

How winner probabilities are represented today:

* Probabilities are fetched and computed in get_event in draft.py:58-86.
* Raw market midpoint probability is computed from ask and bid in draft.py:73-76.
* Per-event probabilities are normalized to sum to 100 for each fetched event ticker in draft.py:84.
* In the finished page, exported results include only Drafter, Pick, Team via create_results_csv in draft.py:31-42 and draft.py:496-515.
* No finished-page aggregation by probability currently exists in draft.py:491-534.

### Data model constraints and risks

1. Team identity ambiguity across leagues.
* Picks persist only team names, not league or probability, in draft.py:408-412.
* Team names can collide across leagues and even within sports contexts; events.csv shows league as a distinct dimension and includes generic names that can overlap by competition model in events.csv:1.
* Without league in each pick record, a lookup by team name alone is unsafe.

2. Drafted odds are not retained in draft records.
* After a pick, the selected row is removed from st.session_state.data in draft.py:415-418.
* Draft records keep only team strings in st.session_state.drafts in draft.py:219-222 and draft.py:408-412.
* Result: finished-page winner sums cannot be reconstructed safely from st.session_state.drafts alone.

3. Potential key collision for duplicate drafter names.
* Drafts dict uses drafter name as dict key in draft.py:219-222.
* Duplicate input names are not validated; duplicate names would overwrite keys and lose picks.

4. Error handling gaps around remote data.
* requests.get has no timeout and no response status check in draft.py:63.
* response.json()['markets'] is accessed without schema guards in draft.py:68.
* No exception handling for network, decoding, or missing fields in draft.py:58-86.

5. Probability normalization edge case.
* df["prob"] is divided by df["prob"].sum() in draft.py:84.
* If all computed probabilities are zero, this can produce division by zero and NaN values.

6. Empty league selection path.
* selected_leagues can be empty from multiselect in draft.py:159-164.
* Start Draft currently checks data is not None (always true for DataFrame) in draft.py:182.
* No explicit validation that draft_pool has rows before starting in draft.py:201-210.

## Safest implementation approach for planner

Goal: add a post-draft winners/losers page that ranks each drafter by sum of drafted-team win probabilities.

Recommended minimal-risk approach:

1. Preserve full pick payload at draft time.
* At pick commit point in draft.py:403-442, store structured pick objects that include at least team, league, prob, and optionally source_row_index.
* Keep backward-compatible support for existing list-of-strings drafts in case of in-session mixed state.

2. Introduce a single aggregation helper near existing helpers.
* Add helper close to create_results_csv in draft.py:31-42.
* Helper should flatten drafted picks and compute:
  * total_prob per drafter = sum(prob)
  * pick_count per drafter
  * optional avg_prob = total_prob / pick_count
* Sort descending by total_prob.
* Return DataFrame used directly by the new page.

3. Keep immutable reference data for safe joins.
* At draft start (around draft.py:217), preserve a non-mutating copy such as st.session_state.initial_data.
* Continue mutating st.session_state.data for available pool only.
* If legacy pick entries are team strings, recover probability via a deterministic merge on (team, league) when possible, else mark unresolved.

4. Add new finished subview, do not replace existing results.
* Extend finished page block in draft.py:491-534 to include a "Winners and Losers" table below current final draft results.
* Preserve existing CSV download behavior first; optionally add a second CSV for ranking table.

5. Add guardrails before draft begins.
* Validate unique non-empty drafter names before st.session_state.drafts creation in draft.py:187-222.
* Validate non-empty draft_pool before page transition in draft.py:201-229.

6. Add resilient fetch handling.
* Wrap get_event request and parsing in try/except near draft.py:58-86.
* Use timeout and response.raise_for_status.
* Handle zero-sum probability normalization by returning zeros or skipping normalization with warning.

Concrete insertion points:

* Helper area: draft.py:20-42 and nearby.
* Session initialization for immutable baseline: draft.py:213-225.
* Pick commit payload: draft.py:403-418.
* Finished-page ranking UI: draft.py:491-534.
* Validation and error checks in setup flow: draft.py:182-210 and draft.py:194-198.

## Validation commands discovered

From Makefile:

* make app -> runs streamlit run draft.py (Makefile:1-2)

From README.md:

* No additional run/test/lint commands documented (README.md:1)

Practical validation plan for planner after implementation:

1. Run make app.
2. Draft across at least two leagues with overlapping or similar team names where possible.
3. Verify winners table ordering and tie behavior.
4. Verify totals match manual sums from drafted rows.
5. Verify behavior with zero-probability picks and empty-league selection blocked.

## Clarifying questions for planner

1. Should probabilities be normalized globally across all selected leagues, or remain league/event-local as currently computed in draft.py:84?
2. Should "losers" mean bottom-N rows only, or full descending table where lower rows are implicit losers?
3. Should winner scoring include 0% picks, or exclude them from totals and count?
4. Should duplicate drafter names be blocked or auto-disambiguated?

## Research status

Complete for current workspace scope.
