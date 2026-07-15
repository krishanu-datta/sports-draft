<!-- markdownlint-disable-file -->
# Implementation Details: Field Picks and Distinctive League Colors

## Context Reference

Sources: .copilot-tracking/research/2026-07-15/field-picks-distinctive-colors-research.md, .copilot-tracking/research/subagents/2026-07-15/field-pick-and-color-distinctiveness-research.md, user request on 2026-07-15.

## Implementation Phase 1: Canonical Field Pick Model and Draft Controls

<!-- parallelizable: false -->

### Step 1.1: Extend canonical pick normalization to support field metadata

Update normalization to preserve legacy compatibility while supporting explicit field semantics.

Files:
* draft.py - Extend normalize_pick_entry and related pick-normalization pathways.

Discrepancy references:
* Requirement traceability: canonical field metadata and resolver compatibility requirements from primary research.

Success criteria:
* normalize_pick_entry returns stable defaults for pick_type, is_field, field_scope, and field_value.
* Legacy string picks and existing dict picks continue to normalize without errors.

Context references:
* draft.py (Lines 37-79) - Existing normalize_pick_entry logic.
* draft.py (Lines 81-108) - Existing drafter and all-drafts normalization helpers.

Dependencies:
* Existing canonical pick model behavior.

### Step 1.2: Add The Field draft action in draft-room UI

Add a low-risk field control block in the right column so users can draft The Field for any selected league without modifying pool row rendering.

Files:
* draft.py - Add right-column field controls and commit path integration.

Discrepancy references:
* Requirement traceability: draft-room field action control requirement from user request and subagent research.

Success criteria:
* Users can select a league and draft The Field from draft room.
* Field picks append to st.session_state.drafts with field metadata and no live odds requirement.
* Duplicate field attempts in the same league are blocked with one-field-per-league enforcement.
* Turn progression and round advancement remain unchanged from normal pick flow.

Context references:
* draft.py (Lines 859-1081) - Draft phase and row pick commit flow.
* draft.py (Lines 1087-1122) - Right column draft board insertion point.

Dependencies:
* Step 1.1 completion.

### Step 1.3: Validate phase changes

Run startup and draft-room smoke checks including one field selection.

Validation commands:
* make app - Verify setup and draft-room load.
* Manual smoke flow - Verify field button action updates draft board and turn state.

## Implementation Phase 2: Post-Draft Field Resolution and Analytics Integration

<!-- parallelizable: false -->

### Step 2.1: Add helper(s) to resolve field values by league at draft completion

Compute league-level field values from drafted non-field picks and attach resolved values into downstream analytics inputs.

Files:
* draft.py - Add field-resolution helper(s) and integration point before finished-page analytics.

Discrepancy references:
* Requirement traceability: field-value formula, clamping, and one-field-per-league behavior from research.

Success criteria:
* field_value resolves as 100 - sum(non-field prob_at_pick by league), clamped to [0, 100].
* Resolved values are available for standings, top selections, ownership, and labels.
* Invalid field picks with missing or blank league resolve to 0.0 and emit a user-visible note in finished-page messaging.

Context references:
* draft.py (Lines 334-431) - Current standings helper behavior.
* draft.py (Lines 1129-1212) - Finished page analytics setup block.

Dependencies:
* Phase 1 completion.

### Step 2.2: Update standings and analytics to include field semantics

Use resolved field values in winners/losers, top selections, and league ownership outputs.

Files:
* draft.py - Update build_winners_losers_standings, build_top_selections_by_drafter, and build_league_ownership_analytics.

Discrepancy references:
* Requirement traceability: include field semantics in standings, top selections, and ownership analytics.
* Decision traceability: planning default uses pick-time consistency across field and non-field picks.

Success criteria:
* Field picks contribute correctly to totals and rankings.
* Non-field behavior remains correct for drafts with no field picks.

Context references:
* draft.py (Lines 334-431) - Standings helper.
* draft.py (Lines 432-515) - Top selections helper.
* draft.py (Lines 516-597) - Ownership helper.

Dependencies:
* Step 2.1 completion.

### Step 2.3: Update exports and persistence payloads for field picks

Expose field semantics in flat and grid outputs and persist resolved field values for reproducible history.

Files:
* draft.py - Update create_results_csv, round-grid label formatting, and persist_completed_draft_snapshot payload composition.

Discrepancy references:
* Requirement traceability: field semantics must be reflected in exports and persistence outputs.

Success criteria:
* Flat CSV includes field-friendly columns and values.
* Round-grid odds toggle shows resolved field values for field picks.
* Persisted snapshot includes field metadata and resolved values without breaking compatibility.

Context references:
* draft.py (Lines 111-127) - Flat CSV helper.
* draft.py (Lines 129-193) - Grid label and dataframe helpers.
* draft.py (Lines 598-699) - Snapshot persistence helper.

Dependencies:
* Step 2.1 completion.

### Step 2.4: Validate phase changes

Run finished-page validation flows for field and non-field scenarios.

Validation commands:
* make app - Run draft through finished state.
* Manual scenarios - Validate field value math, rankings, ownership, and downloads.
* Manual scenario matrix:
	* Scenario A: No field picks in draft (baseline behavior unchanged).
	* Scenario B: Single field pick in one league with partial non-field picks.
	* Scenario C: Second field pick attempt in same league is blocked.
	* Scenario D: All teams drafted in league with field pick (field resolves to 0.0).
	* Scenario E: No non-field teams drafted in league with field pick (field resolves to 100.0).

## Implementation Phase 3: Distinctive League Color Palette Upgrade

<!-- parallelizable: false -->

### Step 3.1: Replace palette generation with deterministic high-contrast categorical mapping

Introduce curated distinct colors with deterministic league assignment and collision fallback.

Files:
* draft.py - Replace build_league_color_palette internals while preserving caller contract.

Discrepancy references:
* Requirement traceability: improve visual league distinction with deterministic higher-contrast palette.

Success criteria:
* League colors are more distinguishable in round-grid cells and legend.
* Color assignment remains deterministic across reruns.

Context references:
* draft.py (Lines 194-211) - Existing palette builder.
* draft.py (Lines 1163-1191) - Grid and legend rendering.

Dependencies:
* None beyond existing grid display path.

### Step 3.2: Validate contrast and readability in styled grid

Confirm text-contrast helper still produces legible foreground color for updated palette.

Files:
* draft.py - Verify _text_color_for_background and style_round_grid usage.

Success criteria:
* Grid text remains readable across all displayed league colors.
* Empty-marker and non-colored fallback styling still behave correctly.

Context references:
* draft.py (Lines 213-248) - Text contrast and style application helpers.

Dependencies:
* Step 3.1 completion.

### Step 3.3: Validate phase changes

Validation commands:
* make app - Verify finished-page rendering and legend clarity with multiple leagues.

## Implementation Phase 4: Final Validation and Reporting

<!-- parallelizable: false -->

### Step 4.1: Run full project validation

Execute startup and end-to-end draft checks for both snake and non-snake modes.

Validation commands:
* make app

### Step 4.2: Fix minor validation issues

Address straightforward runtime, formatting, and rendering issues discovered during smoke testing.

### Step 4.3: Report blocking issues and follow-on recommendations

Document unresolved product decisions and any out-of-scope improvements in planning log and release tracking artifacts.

## Dependencies

* Python environment with streamlit, pandas, requests installed.
* Kalshi API reachability for selected league pulls.

## Success Criteria

* The Field can be drafted for any selected league with correct metadata.
* Finished-page field values are resolved per requested formula and integrated in analytics.
* Exports and persisted snapshots reflect field semantics and remain backward compatible.
* League colors are visibly more distinctive while maintaining readable text.