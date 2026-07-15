<!-- markdownlint-disable-file -->
# Implementation Details: Draft Winners and Losers Page

## Context Reference

Sources: .copilot-tracking/research/2026-07-15/draft-winners-losers-page-research.md, .copilot-tracking/research/subagents/2026-07-15/draft-winners-losers-subagent-research.md, user request on 2026-07-15.

## Implementation Phase 1: End-Of-Draft Refresh and Aggregation Helpers

<!-- parallelizable: false -->

### Step 1.1: Add end-of-draft probability refresh helper

Add a helper that re-fetches league market probabilities at finished-page render time and builds a normalized lookup keyed by league and team.

Files:
* draft.py - Add helper that reuses league ticker configuration and safely refreshes market probabilities.

Discrepancy references:
* Requirement reference: UR-01 and UR-03 from implementation plan objectives.
* Research traceability: Implementation paths section in planning log with accepted IP-02.

Success criteria:
* Helper returns a refreshed DataFrame for selected leagues without crashing when individual league fetches fail.
* Returned dataset can be used as a deterministic lookup for standings computation.

Context references:
* draft.py (Lines 58-86) - Existing per-event fetch and probability logic.
* draft.py (Lines 89-94) - League ticker map used to fetch data.

Dependencies:
* Existing setup and draft pages in draft.py.

### Step 1.2: Add helper for winners/losers ranking computation using refreshed odds

Add a helper that converts draft records into a standings DataFrame with drafter, picks count, total win probability, and average pick probability by mapping drafted teams to refreshed odds. Sort descending by total win probability and apply deterministic tie-breakers.

Files:
* draft.py - Add helper function near existing helpers.

Success criteria:
* Helper returns a stable, sorted DataFrame for all drafters.
* Missing team matches from refreshed data safely contribute 0 probability.
* Empty or partial drafts produce a valid empty or non-crashing result.

Context references:
* draft.py (Lines 31-42) - Existing helper pattern and CSV helper structure.

Dependencies:
* Step 1.1 completion.

### Step 1.3: Validate phase changes

Run app startup and quick manual validation for helper paths because no automated lint/test scripts are defined.

Validation commands:
* make app - Validate Streamlit app boots with updated state model.

## Implementation Phase 2: Finished Page Winners/Losers Presentation

<!-- parallelizable: true -->

### Step 2.1: Extend finished page with standings table sorted high-to-low

Add a new section on the finished page that renders winners/losers standings from the aggregation helper, including total odds and rank order from highest to lowest.

Files:
* draft.py - Update finished branch UI with standings section below final draft results.

Discrepancy references:
* Requirement reference: UR-01 from implementation plan objectives.
* Research traceability: Recommended Planning Direction section in .copilot-tracking/research/2026-07-15/draft-winners-losers-page-research.md.

Success criteria:
* Finished page displays drafter ranking ordered by total win probability descending.
* Existing final draft table and results download remain functional.

Context references:
* draft.py (Lines 491-544) - Finished page rendering and download flow.

Dependencies:
* Step 1.2 completion.

### Step 2.2: Preserve compatibility in final results export behavior

Ensure create_results_csv still emits the historical output shape while supporting string-based pick records.

Files:
* draft.py - Update create_results_csv logic to accept structured picks.

Success criteria:
* CSV download still provides Drafter, Pick, Team columns.
* Export behavior works for existing in-memory draft shape.

Context references:
* draft.py (Lines 31-42) - Existing CSV helper.

Dependencies:
* Existing draft state shape.

### Step 2.3: Validate phase changes

Validation commands:
* make app - Confirm finished page renders both draft results and standings.

## Implementation Phase 3: Historical Persistence

<!-- parallelizable: false -->

### Step 3.1: Add persistent storage helper for completed drafts and standings

Add helper utilities to append completed draft summaries to a local history file in repository scope.

Files:
* draft.py - Add helper(s) to serialize and append completed draft and standings data.
* draft_history.csv or draft_history.json - New persistent history artifact created on first write.

Discrepancy references:
* Requirement reference: UR-02 from implementation plan objectives.

Success criteria:
* Helper creates history storage when missing.
* Helper appends without corrupting existing history data.

Context references:
* draft.py (Lines 491-544) - Finished-page flow where persistence should trigger.

Dependencies:
* Phase 2 standings DataFrame available in finished flow.

### Step 3.2: Persist completed draft picks and standings at finish time

At draft completion, write rows containing run timestamp, drafter, picks, total odds, and rank to history storage.

Files:
* draft.py - Integrate history write call in finished-page flow with one-time-per-run guard.

Success criteria:
* Completed drafts append one historical snapshot per finished run.
* Reruns of the finished page do not duplicate persistence writes.

Context references:
* draft.py (Lines 491-544) - Finished-page execution area.

Dependencies:
* Step 3.1 completion.

### Step 3.3: Validate phase changes

Validation commands:
* make app - Complete at least one draft and confirm history file contains persisted standings snapshot.

## Implementation Phase 4: Input and Data-Quality Guardrails

<!-- parallelizable: false -->

### Step 4.1: Add setup validation for unique drafter names and non-empty pool

Before starting a draft, reject duplicate and blank names and prevent start when selected leagues return no valid rows.

Files:
* draft.py - Add setup-time guardrails in Start Draft action block.

Success criteria:
* Duplicate names show user-facing error and block draft start.
* Empty pool after filtering shows user-facing error and block draft start.

Context references:
* draft.py (Lines 194-217) - Draft start action and data preparation.

Dependencies:
* None.

### Step 4.2: Harden API fetch and normalization failure handling

Add minimal error handling for HTTP failures, malformed payloads, and zero-denominator normalization while keeping user flow understandable.

Files:
* draft.py - Update get_event to fail gracefully and return empty DataFrame shape when needed.

Success criteria:
* App does not crash on network and schema errors from Kalshi responses.
* Probability normalization avoids divide-by-zero and preserves numeric stability.

Context references:
* draft.py (Lines 58-86) - Existing API fetch and normalization logic.

Dependencies:
* None.

### Step 4.3: Validate phase changes

Validation commands:
* make app - Smoke test setup flow with failing and successful data scenarios.

## Implementation Phase 5: Final Validation

<!-- parallelizable: false -->

### Step 4.1: Run full project validation

Execute available validation commands for the repository.

Validation commands:
* make app

### Step 4.2: Fix minor validation issues

Address straightforward runtime or UI regressions discovered in smoke testing.

### Step 4.3: Report blocking issues

Document any failures requiring broader refactors or additional research before implementation completion.

## Dependencies

* Streamlit runtime from current repository environment
* Kalshi markets API availability for live fetch behavior

## Success Criteria

* Finished page includes winner/loser standings sorted from highest to lowest summed win odds.
* Standings derive from end-of-draft refreshed market probabilities.
* Existing draft completion output and CSV export remain intact.
* Completed drafts and standings are persisted for historical review.
* Setup and fetch paths gracefully handle duplicate names, empty data, and API failures.