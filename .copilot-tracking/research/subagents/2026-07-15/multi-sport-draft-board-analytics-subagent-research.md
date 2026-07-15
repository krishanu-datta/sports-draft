---
title: Multi-sport draft board analytics subagent research
description: Research-only implementation plan for league expansion, round-grid results, and enhanced winners/losers analytics in draft.py
ms.date: 2026-07-15
ms.topic: reference
---

## Scope

Plan a multi-part enhancement in the current Streamlit workspace, without implementation.

Requested outcomes:

* Expand Draft Pool leagues to include eight new entries and Kalshi IDs.
* Replace or augment final results with a round-by-round draft grid.
* Add richer winners/losers analytics, including top selections per drafter and sport-level dominance.
* Recommend best design path with minimum redundancy and justified file-structure choice.

## Workspace baseline

Current structure:

* draft.py is a single-file Streamlit app with setup, draft, and finished views.
* events.csv and draft_history.jsonl are data artifacts, not authoritative runtime sources.
* Makefile provides one run target: make app -> streamlit run draft.py.

Current finished-page behavior in draft.py:

* Displays flat results table built from create_results_csv.
* Displays winners/losers standings from build_winners_losers_standings.
* Persists standings snapshots to draft_history.jsonl.

## Requested league expansion

Add these entries to LEAGUES:

| Label                    | Kalshi ID            |
|--------------------------|----------------------|
| WNBA                     | kxwnba-26            |
| MLB                      | kxmlb-26             |
| F1 Belgian Grand Prix    | kxf1race-belgp26     |
| NFL                      | kxsb-27              |
| College Basketball       | kxmarmad-27          |
| UCL                      | kxucl-27             |
| NBA                      | kxnba-27             |
| NHL                      | kxnhl-27             |

Exact insertion point:

* draft.py lines 296-301 (LEAGUES dict literal).

Design note:

* Keep existing leagues and append new entries; preserve user defaults behavior in setup multiselect.

## Exact insertion points in draft.py

### 1) League dictionary expansion

* Location: draft.py lines 296-301.
* Change: append eight requested league-name -> event-ticker mappings.

### 2) Data model hardening for picks

* Location: draft.py lines 647-656 (Draft button commit path).
* Current: stores only row["team"] string.
* Planned: store structured pick payload per selection with at least:
  * team
  * league
  * prob_at_pick
  * round
  * pick_in_round
  * overall_pick

### 3) Round-grid results helper(s)

* Location: helper section near draft.py lines 36-52 (adjacent to create_results_csv).
* Planned additions:
  * build_round_grid(drafts, players, rounds): DataFrame with rows=rounds, columns=drafters.
  * format_pick_cell(pick, include_odds): string formatter for name-only or name+odds display.
  * build_round_grid_style_map(grid, league_palette): style annotations keyed by league.

### 4) Finished page replacement/augmentation

* Location: draft.py lines 740-767 (final results table + CSV section).
* Planned UI:
  * Keep existing flat table as optional secondary view for export compatibility.
  * Primary display becomes round-by-round grid table.
  * Add toggle to show odds in each cell label, for example Team (12.3%).

### 5) Enhanced winners/losers analytics

* Location: draft.py lines 770-834 (standings section).
* Planned additions:
  * top selections per drafter view (top N by prob_at_pick, default N=3).
  * sport-level dominance view:
    * aggregate total odds by league for each drafter
    * compute ownership winner per league using highest summed odds
    * show tie handling explicitly when equal totals

### 6) Optional persistence schema expansion

* Location: draft.py lines 224-293 (persist_completed_draft_snapshot).
* Planned update:
  * continue writing standings for backward compatibility
  * optionally include a compact analytics block for top selections and sport ownership to avoid recomputation across sessions

## Data model changes needed

Current picks model is list[str] or list[dict] with optional team only. For round-grid and sport analytics, this is insufficient.

Recommended canonical pick model:

```text
{
  "team": str,
  "league": str,
  "prob_at_pick": float,
  "round": int,
  "pick_in_round": int,
  "overall_pick": int
}
```

Migration strategy:

* Maintain backward compatibility where historical pick entries may be plain strings.
* Normalization helper should coerce legacy string picks into dicts with missing fields defaulted.
* Existing create_results_csv should read both formats safely.

Why this is required:

* Round grid needs deterministic round/slot metadata under snake and non-snake flows.
* Sport analytics needs league identity per pick.
* Top selections needs stable probability value at draft time, not refreshed post-draft API values.

## Round-grid design recommendation

Recommended UX:

* Table rows are rounds 1..N.
* Table columns are drafter names in setup order.
* Each cell is the drafted selection label.
* Background color denotes league category.
* Toggle controls whether odds are appended to cell text.

Implementation note for Streamlit:

* st.dataframe supports styled pandas Styler, but color rendering can vary by Streamlit version and theme.
* If styler limitations appear, fallback to st.markdown with a small HTML table for deterministic color blocks.

## Winners and losers detail design

### Top selections per drafter

* For each drafter, sort picks by prob_at_pick descending.
* Show top N picks with league and probability.
* Include aggregate stats: total odds, average odds, pick count.

### Sport-level dominance

* Build matrix: rows=drafters, columns=leagues, values=sum(prob_at_pick).
* For each league, assign owner = drafter with maximum value.
* Tie rule recommendation:
  * if shared max within epsilon threshold, mark as Co-owned (A, B).
  * avoid arbitrary tiebreak unless user explicitly wants one.

## Refactoring decision

Recommendation for this enhancement cycle:

* Do not split files yet.
* Keep draft.py as single file, but introduce clear helper regions and remove duplicated transformation logic.

Rationale:

* Repository is currently a small, single-entry Streamlit app.
* Requested changes are cohesive around one page flow and shared session state.
* Premature splitting adds import overhead and migration risk without strong scale pressure.

Refactor threshold for future split:

* If helper count grows beyond approximately 8-10 analytics or table-formatting functions, extract to one module:
  * analytics.py for draft normalization, round-grid shaping, and standings calculations.

## Redundancy reduction opportunities

* Consolidate pick-normalization logic currently repeated in create_results_csv, build_winners_losers_standings, and persist_completed_draft_snapshot.
* Use one canonical helper to parse pick objects and expose normalized fields.
* Keep standings and top-selection computations fed from the same normalized DataFrame.

## Risks and constraints

1. Duplicate team names across leagues.
   * Risk: incorrect odds mapping if keyed by team only.
   * Mitigation: use composite key league + team and persist league on each pick.

2. Ties in sport ownership.
   * Risk: unstable or confusing owner assignment.
   * Mitigation: explicit co-owner state with deterministic display ordering.

3. Streamlit styling constraints for table cell colors.
   * Risk: inconsistent background rendering in st.dataframe + Styler.
   * Mitigation: test styler path first; retain HTML-table fallback.

4. Probability drift from refresh-selected-league API calls.
   * Risk: winners/top picks shift after draft due to market movement.
   * Mitigation: top picks and dominance should use prob_at_pick for draft-history integrity; keep refreshed standings as optional secondary metric if desired.

5. Snake draft round indexing errors.
   * Risk: wrong round-grid placement under reverse order rounds.
   * Mitigation: persist round and pick metadata at draft time instead of reconstructing heuristically.

## Validation strategy and commands

Pre-flight validation:

1. Run app locally:

```bash
make app
```

2. Manual scenario matrix:

* snake on, 3+ drafters, 4 rounds, multiple leagues
* snake off, 2 drafters, 3 rounds
* include zero-odds picks and verify top-selection sorting
* verify duplicate team names across different leagues map correctly
* verify tie case in league ownership by forcing equal summed odds

3. Output verification:

* round grid shape equals rounds x drafters
* each drafted pick appears exactly once across all cells
* league color mapping is stable and deterministic
* toggle switches between label formats without recomputing draft state

4. Regression checks:

* CSV export still works
* Start New Draft still clears session state correctly
* draft_history.jsonl write path remains non-breaking

Optional quick checks:

```bash
streamlit run draft.py
```

```bash
python -m compileall draft.py
```

## Recommended implementation path

Phase 1: Foundations

* Expand LEAGUES.
* Introduce canonical pick model at draft commit point.
* Add normalization helper with legacy compatibility.

Phase 2: Final results redesign

* Build round-grid helper and style map.
* Replace default finished results table with round-grid primary view.
* Add odds-display toggle and keep flat export table as secondary.

Phase 3: Winners/losers deep analytics

* Extend standings with top picks per drafter.
* Add sport-level dominance matrix and ownership summary.
* Add tie-aware ownership logic.

Phase 4: Validation and polish

* Run scenario matrix and regression checks.
* Remove redundant transformations and duplicate helper logic.

## Clarifying decisions still needed

1. Should dominance use league-level grouping exactly as selected labels (for example UCL and Premier League separated), or roll up to higher sport buckets (for example Soccer total)?
2. Should refreshed live odds remain the primary winners metric, or should prob_at_pick become the default with live odds as optional secondary view?
3. In the round-grid view, should empty future cells be blank, em-dash text, or hidden by rendering only completed rounds?
4. For ties in league ownership, should UI show co-owners or apply a deterministic tiebreak rule?
5. Should the download export include the new round-grid format in addition to the existing flat CSV?

## Research status

Complete for current workspace scope.
