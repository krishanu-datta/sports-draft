<!-- markdownlint-disable-file -->
# Planning Log: Multi-Sport Draft Grid and Analytics

## Discrepancy Log

Gaps and differences identified between research findings and the implementation plan.

### Unaddressed Research Items

* None currently. Previously logged DR-01, DR-02, and DR-04 were fully resolved across Phases 1, 2, and 4.

### Plan Deviations from Research

* DD-01: Keep single-file architecture for this change set.
  * Research considers: Optional extraction to analytics.py if helper complexity grows.
  * Plan implements: No immediate file split; helper reorganization in draft.py.
  * Rationale: Current app size remains manageable and user requested splitting only if justified.
* DD-02: Detailed analytics default to pick-time odds.
  * Research open decision: winners metric could be refreshed odds or pick-time odds.
  * Plan implements: Pick-time odds for detailed sections; refreshed odds can remain legacy standings view if retained.
  * Rationale: Prevents drift and preserves draft-state integrity for analytics attribution.
* DD-03: Runtime startup validation requires explicit virtual environment PATH in current shell.
  * Plan specifies: Validation via make app.
  * Implementation differs: make app only resolves streamlit when PATH includes .venv/bin in current shell session.
  * Rationale: Environment configuration is shell-specific; feature code remains valid.
* DD-04: Detailed analytics persisted as optional analytics payload fields.
  * Plan specifies: Extend persistence schema for analytics while preserving compatibility.
  * Implementation differs: Added optional analytics block alongside legacy standings keys rather than replacing persisted shape.
  * Rationale: Backward compatibility with existing snapshot consumers.

### Validation Notes

* VN-01: Phase 3 browser flow validation completed with one-round draft to finished page.
* VN-02: Top selections section, ownership matrix, and ownership summary render as expected.
* VN-03: Persisted snapshot includes analytics block with top selections and league ownership data.

### Validation Notes

* VN-01: Completed make app startup validation using PATH="$PWD/.venv/bin:$PATH".
* VN-02: Completed quick finished-page flow with one-round two-drafter draft.
* VN-03: Verified Top Selections and League Ownership sections render using pick-time probabilities.
* VN-04: Verified persisted snapshot includes analytics block with tie-aware ownership summary schema.
* VN-05: Completed Phase 4 smoke startup regression via PATH="$PWD/.venv/bin:$PATH" make app.
* VN-06: Confirmed helper cleanup retained single-file architecture and removed repeated normalization loops.
* VN-07: Final Phase 5 startup validation completed successfully with PATH="$PWD/.venv/bin:$PATH" make app.

## Implementation Paths Considered

### Selected: Canonical Pick Model Plus Round-Grid and Detailed Analytics in Single File

* Approach: Expand leagues, persist structured picks, build round-grid and analytics helpers, and render detailed finished-page sections within draft.py.
* Rationale: Directly addresses requested outcomes with minimal architectural churn.
* Evidence: .copilot-tracking/research/2026-07-15/multi-sport-draft-grid-analytics-research.md (Lines 48-61)

### IP-01: Keep String Picks and Infer Metadata Post Hoc

* Approach: Preserve string picks and reconstruct league and odds using lookup merges at finish time.
* Trade-offs: Lower migration effort but error-prone with duplicate team names across leagues.
* Rejection rationale: Unreliable for ownership analytics and round-grid fidelity.

### IP-02: Extract Analytics Into Separate Module Immediately

* Approach: Create analytics.py and styling utilities now.
* Trade-offs: Better separation but adds project structure overhead for a still-small app.
* Rejection rationale: Not yet justified by current complexity; can be follow-on if growth continues.

## Suggested Follow-On Work

* WI-01: Replace use_container_width with width in dataframes before Streamlit deprecation date (medium)
  * Source: Runtime warnings from previous validation cycle
  * Dependency: None
* WI-02: Add configurable grouping for soccer leagues (UCL plus Premier League combined vs separate) (low)
  * Source: Open decision in research
  * Dependency: Detailed analytics baseline implemented
* WI-03: Add optional refreshed-odds analytics comparison mode (low)
  * Source: Open decision in research
  * Dependency: Canonical pick model and pick-time analytics complete

## User Decisions Pending

* PD-01: Soccer grouping model
  * Options: Separate leagues or aggregate into one sport bucket.
  * Current planning default: Keep separate by league.
* PD-02: League ownership tie display
  * Options: Co-owners list or deterministic single-owner tiebreak.
  * Current planning default: Co-owners list.
