---
title: Field pick and color distinctiveness research
description: Implementation context and recommendations for adding a Field pick feature and higher-contrast league colors in the sports-draft app
ms.date: 2026-07-15
ms.topic: reference
---

## Research scope

Investigate implementation context for adding a new draft feature called the field, plus improved league color distinctiveness.

Research questions:

1. Which existing architecture and code paths in draft.py govern setup-selected leagues, draft pool rendering and actions, draft normalization model, and finished-page analytics?
2. How should the canonical pick model represent field picks while preserving backward compatibility?
3. What post-draft algorithm should compute field probabilities, including edge-case behavior?
4. What analytics/export updates are required?
5. Where should field UI controls be placed in the draft room for lowest risk in this single-file architecture?
6. How can league color assignment become more distinctive while staying deterministic?

## Findings

### 1) Existing architecture and code paths

The app is a single-file Streamlit state machine with three page phases in draft.py:

* Setup phase gate: draft.py:700
* Draft room phase gate: draft.py:859
* Finished phase gate: draft.py:1129

Setup-selected leagues and draft pool creation:

* League selector: selected_leagues multiselect at draft.py:759.
* League data fetch loop (Kalshi): draft.py:768-778 via get_event (draft.py:250).
* Start button and setup validation: draft.py:784-835.
* Initial draft pool materialization and sorting: draft.py:836-845.
* Session state assignment for players, leagues, pool, drafts, and round counters: draft.py:854-876.

Draft pool rendering and draft action buttons:

* Available pool header and filters begin at draft.py:915.
* Filter controls and toggles: draft.py:921-970.
* Pool table rendering loop: draft.py:982-1024.
* Draft action button per row: draft.py:1025.
* Pick normalization and commit using normalize_pick_entry: draft.py:1034-1043.
* Pick append into st.session_state.drafts: draft.py:1045-1048.
* Removal from available pool and turn progression: draft.py:1052-1081.

Draft data structure and normalization helpers:

* Canonical pick normalizer: normalize_pick_entry at draft.py:37.
* Drafter picks normalizer: normalize_drafter_picks at draft.py:81.
* Whole draft normalizer: normalize_all_drafts at draft.py:98.
* Current canonical pick keys returned by normalize_pick_entry:
  * team
  * league
  * prob_at_pick
  * round
  * pick_in_round
  * overall_pick

Finished-page standings and analytics calculations:

* Round grid construction: build_round_grid_dataframe at draft.py:146.
* Round grid styling using league palette: style_round_grid at draft.py:223.
* League color palette generation: build_league_color_palette at draft.py:194.
* Flat results DataFrame for CSV: create_results_csv at draft.py:111.
* Refreshed league probabilities for standings lookup: refresh_selected_league_probabilities at draft.py:304.
* Winners/losers standings: build_winners_losers_standings at draft.py:334.
* Top selections analytics: build_top_selections_by_drafter at draft.py:432.
* League ownership analytics: build_league_ownership_analytics at draft.py:516.
* Persistence snapshot writer: persist_completed_draft_snapshot at draft.py:598.
* Finished-page rendering and export buttons: draft.py:1129-1376.

### 2) Canonical representation for field picks with backward compatibility

Recommended canonical pick model extension:

* Keep existing fields unchanged.
* Add optional metadata fields:
  * pick_type: one of team or field (default team for backward compatibility)
  * is_field: boolean convenience mirror (true when pick_type is field)
  * field_scope: league-level for this feature (future-safe for broader scopes)
  * field_value: nullable float, filled post-draft during final computation

Example canonical field pick:

```json
{
  "team": "The Field",
  "league": "NBA",
  "prob_at_pick": 0.0,
  "round": 2,
  "pick_in_round": 1,
  "overall_pick": 7,
  "pick_type": "field",
  "is_field": true,
  "field_scope": "league",
  "field_value": null
}
```

Backward compatibility strategy:

* normalize_pick_entry (draft.py:37) already accepts string picks and dict picks and applies defaults, which is a strong compatibility anchor.
* Extend normalize_pick_entry to default missing pick_type to team, infer field only for explicit markers (for example team == The Field with explicit toggle, not by free text alone).
* Keep existing consumers resilient by:
  * treating missing pick_type as team
  * preserving existing team and league semantics
  * never requiring new fields at read time
* Keep persisted snapshot compatibility by appending new keys only, not renaming old keys.

Alternative model:

* Keep team as empty string for field and rely only on pick_type plus league.
* This avoids a pseudo-team label but increases UI/export branching complexity because many existing renderers expect a displayable team string.

### 3) Post-draft field probability computation algorithm

Target rule from scope:

For each league where at least one drafter selected a field pick:

* field_value = 100 - sum(prob_at_pick of drafted non-field teams in that league)

Recommended implementation details:

1. Build league-level drafted totals from normalized picks:
   * Include only non-field picks with matching league.
   * Use prob_at_pick captured at draft time, not refreshed post-draft odds.
2. Compute base field value per league as 100 - drafted_total.
3. Clamp final field value to [0, 100] to avoid negative values from bad source data or duplicates.
4. Assign this same league field value to every field pick in that league unless product decision says one field pick should consume the whole field and make later field picks zero.

Edge-case behavior recommendation:

* Multiple field picks in same league:
  * Default behavior: each field pick in that league gets the same computed field_value.
  * Rationale: aligns with literal formula provided and is lowest-risk implementation.
  * Alternative: split equally among field picks (field_value / count_field_picks), but this changes game mechanics and should be opt-in.
* All teams drafted in a league:
  * drafted_total near 100, so field_value near 0.
* No teams drafted in a league and field pick exists:
  * field_value = 100.
* Missing league data on a field pick:
  * treat as invalid input for field math; assign 0 and emit warning/caption.
* Duplicate non-field picks in same league:
  * current app removes drafted row from available pool at draft.py:1052-1055, so normal UI path should prevent true duplicates.
  * still protect computation with clamping and optional duplicate detection in analytics pipeline.

Suggested helper insertion:

* Add a new helper near analytics functions, after build_winners_losers_standings (draft.py:334) or before finished-page section.
* Proposed helper shape:
  * compute_field_values_by_league(drafts) -> dict[league, field_value]
  * apply_field_values_to_picks(drafts, strategy="replicate") -> normalized drafts with resolved field_value per pick

### 4) Required updates to analytics and exports

Round-grid labels:

* Current labels are produced by format_pick_cell_label (draft.py:129) and consumed in build_round_grid_dataframe (draft.py:146).
* Update label logic for field picks to display The Field and optionally the resolved field_value in odds mode.

Flat CSV:

* Current flat CSV generator create_results_csv (draft.py:111) outputs Drafter, Pick, Team only.
* Add columns with safe defaults:
  * League
  * Pick Type
  * Pick-Time Probability
  * Field Value (resolved)

Winners/losers standings logic:

* Current build_winners_losers_standings (draft.py:334) recalculates pick probability from refreshed market data lookup.
* For field picks, standings should use resolved field_value, not refreshed team lookup.
* For non-field picks, keep existing lookup behavior unless product decision is to use pick-time probability consistently for all picks.

Top selections and ownership analytics:

* Top selections (draft.py:432): decide whether field picks participate in top-N ranking.
  * Recommendation: include them using resolved field_value as comparable probability metric.
* League ownership matrix (draft.py:516): include field picks by adding resolved field_value into league totals to preserve ownership meaning.

Persistence snapshot:

* persist_completed_draft_snapshot at draft.py:598 currently stores normalized drafts and standings plus analytics.
* Ensure snapshots include new pick metadata fields and resolved field_value to make history reproducible.
* Keep hash payload stable by deterministic key ordering (already in place via json.dumps sort_keys=True at draft.py:633).

### 5) UI placement options in draft room and recommended path

Option A: Right side panel (Draft Board column)

* Insert a compact field action card at the top of the right column near draft.py:1089.
* Control shape:
  * Select league for field pick (from selected leagues)
  * Draft Field button
* Pros:
  * Minimal disruption to existing left-side pool table loop
  * Lowest risk to current row-index based draft buttons
  * Easy to conditionally disable per-league if field already drafted (if needed)
* Cons:
  * Separates field action from regular pool action visually

Option B: Top of available pool (left column)

* Insert a synthetic row/card above the pool table in left section around draft.py:915-982.
* Pros:
  * Field appears in the same decision area as normal picks
* Cons:
  * More coupling with current pool filtering, sorting, and row-button keying
  * Slightly higher regression risk in single-file architecture

Recommended lowest-risk path: Option A (right side panel).

* It avoids touching the pool DataFrame rendering loop and row indexing.
* It centralizes special-case logic for field picks in one UI block while reusing the same pick commit flow.

### 6) Distinctive league colors strategy

Current palette limitations (build_league_color_palette at draft.py:194):

* Uses hashed hue with fixed low saturation (0.22) and high value (0.98).
* Many resulting colors are pastel and visually close.
* Distinctiveness degrades as league count grows.
* Readability compensation exists via _text_color_for_background (draft.py:213), but color separation itself is the main issue.

Recommended deterministic high-contrast strategy:

1. Predefined categorical palette first:
   * Use a curated list of high-contrast colors (for example 12 to 20 entries) designed for categorical distinction and color-vision accessibility.
2. Deterministic league-to-color assignment:
   * Hash league name and map to palette index.
3. Collision fallback for adjacent collisions:
   * If two active leagues hash to same index in current view, step through palette with deterministic offset.
4. Long-tail fallback:
   * If leagues exceed palette size, generate extra colors with constrained HSV ranges that preserve contrast against white backgrounds.

Alternative:

* Keep pure hash-to-HSV, but widen saturation/value ranges and quantize hue buckets.
* Lower code complexity than categorical palette, but still weaker perceptual separation than curated categorical colors.

## Recommended implementation path

1. Extend normalize_pick_entry and any pick writers to support pick_type/is_field/field_scope/field_value defaults while preserving existing behavior for old picks.
2. Add field draft UI in right column (Option A) and route its commit through existing pick append and turn progression logic.
3. Add post-draft field resolver helpers and integrate before standings/top selections/ownership are built.
4. Update round-grid labels and flat CSV to expose field semantics and values.
5. Update standings/top selections/ownership to include resolved field values consistently.
6. Update snapshot payload to include resolved field metadata and verify dedupe behavior remains deterministic.
7. Replace league color builder with categorical deterministic strategy while retaining text contrast helper.

## Risks and validation recommendations

Key risks:

* Inconsistent scoring if non-field picks use refreshed probabilities while field uses pick-time-derived value.
* Ambiguous game behavior with multiple field picks in same league.
* Regression risk from introducing special-case pick types into code paths that currently assume team strings.
* Palette changes could reduce readability if contrast checks are not preserved.

Validation recommendations:

1. Functional draft flow tests:
   * Team picks only (no field) should match current behavior.
   * Single field pick in one league.
   * Multiple field picks in same league.
2. Edge-case tests:
   * All teams drafted in league.
   * No teams drafted in league but field drafted.
   * Missing/blank league on field pick.
   * Simulated duplicate picks in state payload.
3. Analytics consistency checks:
   * Manual recomputation of standings totals versus displayed totals.
   * Round-grid labels and CSV rows include expected field metadata.
4. Snapshot reproducibility checks:
   * Re-running finished page should not create duplicate snapshot for same state.
5. Visual checks:
   * League legend and grid color distinction with many leagues selected.

## Open questions requiring user decision

1. Multiple field picks in one league: should each receive full field_value, split equally, or should only first field pick be valid?
2. Should standings use refreshed live probabilities for non-field picks (current behavior) or pick-time probabilities for all picks to align with field formula inputs?
3. Should field picks appear in top selections ranking and league ownership exactly like team picks?
4. Should field be draftable once per league globally, or multiple times by different drafters?
5. Should The Field display as literal team label in exports/UI, or should it be represented via separate pick_type fields only?

## Status

Complete for current scope.
