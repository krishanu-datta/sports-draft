<!-- markdownlint-disable-file -->
# Implementation Details: Multi-Sport Draft Grid and Analytics

## Context Reference

Sources: .copilot-tracking/research/2026-07-15/multi-sport-draft-grid-analytics-research.md, .copilot-tracking/research/subagents/2026-07-15/multi-sport-draft-board-analytics-subagent-research.md, user request on 2026-07-15.

## Implementation Phase 1: League Expansion and Canonical Pick Model

<!-- parallelizable: false -->

### Step 1.1: Expand LEAGUES with requested Kalshi event IDs

Add eight requested sports to the LEAGUES mapping so they appear in setup multiselect and participate in data fetch.

Files:
* draft.py - Update LEAGUES dictionary entries.

Discrepancy references:
* Requirement reference: UR-01, UR-02, UR-03 from implementation plan.
* Research traceability: Requested league expansion table in primary research.

Success criteria:
* Setup multiselect shows all existing and newly requested leagues.
* Data fetch loop requests all selected leagues and still handles empty responses safely.

Context references:
* draft.py (Lines 296-301) - Existing league map.
* draft.py (Lines 381-396) - League selection and fetch loop.

Dependencies:
* Existing get_event helper and setup flow.

### Step 1.2: Convert draft pick storage to canonical structured payload

Store each pick as a dict with team, league, prob_at_pick, round, pick_in_round, and overall_pick to support round-grid and analytics views.

Files:
* draft.py - Update draft commit logic and add pick normalization helper for backward compatibility.

Discrepancy references:
* Addresses DR-01 by eliminating team-name-only ambiguity across leagues.

Success criteria:
* Every newly drafted pick includes league and pick-time probability metadata.
* Existing logic that reads picks remains compatible with old string entries.

Context references:
* draft.py (Lines 647-656) - Current draft append logic.
* draft.py (Lines 36-52, 139-221, 224-293) - Existing helper consumers of pick values.

Dependencies:
* Step 1.1 completion.

### Step 1.3: Validate phase changes

Run app startup and quick setup flow smoke check.

Validation commands:
* make app - Ensure app starts and setup multiselect renders expanded league list.

## Implementation Phase 2: Round-Grid Final Results View

<!-- parallelizable: false -->

### Step 2.1: Build round-grid result transformation helpers

Add helpers to shape picks into a rounds-by-drafters table and optional label formatting with odds.

Files:
* draft.py - Add helper(s) for round-grid dataframe creation and cell text formatting.

Discrepancy references:
* Requirement reference: UR-04 and UR-05 from implementation plan.

Success criteria:
* Grid rows map to rounds and columns map to drafter names.
* Empty cells in incomplete rounds render as em dash markers.

Context references:
* draft.py (Lines 740-767) - Existing finished-page results section to replace/augment.

Dependencies:
* Step 1.2 completion.

### Step 2.2: Add league color coding and odds toggle in finished page

Render round-grid table with color by league, and add a toggle to append odds to selection labels.

Files:
* draft.py - Update finished-page result rendering block and add color map helper.

Discrepancy references:
* Addresses DR-02 by implementing requested visualization semantics.

Success criteria:
* Cells are visually distinguished by league color.
* Toggle switches between Team and Team plus Odds views without state loss.

Context references:
* draft.py (Lines 760-767) - Existing results download section.
* draft.py (Lines 770-834) - Existing winners section location.

Dependencies:
* Step 2.1 completion.

### Step 2.3: Add round-grid export support while preserving flat CSV

Provide round-grid CSV download and keep existing flat results CSV for compatibility.

Files:
* draft.py - Update finished-page download controls.

Success criteria:
* Existing Download Draft Results still works.
* New grid-format download is available and reflects current odds-toggle text format or canonical raw format.

Dependencies:
* Step 2.1 completion.

### Step 2.4: Validate phase changes

Validation commands:
* make app - Complete one short draft and verify round-grid table and toggle behavior.

## Implementation Phase 3: Detailed Winners and Losers Analytics

<!-- parallelizable: false -->

### Step 3.1: Add top selections per drafter analytics

Compute and render per-drafter top picks sorted by pick-time probability.

Files:
* draft.py - Add analytics helper and finished-page section rendering.

Discrepancy references:
* Requirement reference: UR-06 from implementation plan.

Success criteria:
* Each drafter shows top N picks with league and probability.
* Sorting is deterministic and stable.

Context references:
* draft.py (Lines 770-834) - Current winners/losers block to extend.

Dependencies:
* Step 1.2 completion.

### Step 3.2: Add league ownership matrix and majority owner summary

Aggregate summed odds by league and drafter, then assign each league to top drafter with co-owner handling for ties.

Files:
* draft.py - Add matrix helper and ownership summary rendering.

Discrepancy references:
* Addresses DR-03 tie-handling ambiguity with explicit co-owner display.

Success criteria:
* Ownership matrix is visible and readable.
* Leagues with equal top sums show co-owners instead of arbitrary tiebreak unless configured.

Context references:
* draft.py (Lines 139-221) - Existing standings helper baseline.

Dependencies:
* Step 3.1 completion.

### Step 3.3: Integrate analytics with persistence snapshot schema

Persist compact analytics output without duplicating heavy structures or breaking existing snapshot format compatibility.

Files:
* draft.py - Update persistence payload writing with optional analytics block.

Success criteria:
* Snapshot writing remains idempotent for same draft state.
* Existing consumers of historical file remain readable.

Context references:
* draft.py (Lines 224-293) - Current persistence helper.

Dependencies:
* Step 3.1 and Step 3.2 completion.

### Step 3.4: Validate phase changes

Validation commands:
* make app - Verify top picks, ownership matrix, and snapshot writing on finished page.

## Implementation Phase 4: Redundancy Reduction and Helper Cleanup

<!-- parallelizable: false -->

### Step 4.1: Centralize pick normalization logic

Refactor repeated pick parsing from create_results_csv, standings helper, and persistence helper into one shared normalization utility.

Files:
* draft.py - Add normalization utility and update helper call sites.

Discrepancy references:
* Addresses DR-04 maintainability risk from duplicated transformation logic.

Success criteria:
* No duplicated conditional parsing paths remain across helper functions.
* All downstream helpers use normalized pick records.

Dependencies:
* Phase 1 and Phase 3 completion.

### Step 4.2: Keep single-file design unless complexity threshold exceeded

Retain helpers in draft.py with clearer sectioning and only extract module(s) if complexity justifies split.

Files:
* draft.py - Reorder helper sections if needed for readability.

Success criteria:
* Function boundaries are clear and cohesive.
* No unnecessary module fragmentation introduced.

Dependencies:
* Step 4.1 completion.

### Step 4.3: Validate phase changes

Validation commands:
* make app - smoke verify no regressions in setup, draft, finished states.

## Implementation Phase 5: Final Validation and Reporting

<!-- parallelizable: false -->

### Step 5.1: Run full project validation

Execute full startup and manual flow checks for both snake and non-snake drafts.

Validation commands:
* make app

### Step 5.2: Fix minor validation issues

Address straightforward runtime warnings and UI issues discovered during smoke testing.

### Step 5.3: Report blocking issues and follow-on work

Document unresolved items, especially stylistic constraints and optional exports.

## Dependencies

* Streamlit runtime and Python dependencies in .venv
* Kalshi API reachability for selected league fetches

## Success Criteria

* Expanded league list includes all user-requested sports and fetches draft pool entries.
* Finished results primary view is a round-grid table with league color coding and odds toggle.
* Detailed winners analytics includes top selections per drafter and league ownership summary.
* Redundant pick-parsing logic is centralized and maintainable.
* Existing workflows (drafting, CSV export, start new draft, persistence) remain functional.
