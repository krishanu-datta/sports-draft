<!-- markdownlint-disable-file -->
# Planning Log: Draft Winners and Losers Page

## Discrepancy Log

Gaps and differences identified between research findings and the implementation plan.

### Unaddressed Research Items

* None currently. Previously logged DR-01 through DR-04 are covered in planned implementation steps and no longer represent unaddressed research gaps.

### Plan Deviations from Research

* DD-01: Scoring strategy changed from draft-time odds capture to end-of-draft probability refresh.
  * Research recommends: Preserve pick-time values for deterministic scoring.
  * Plan implements: Re-fetch probabilities at draft completion and accept minor drift.
  * Rationale: User-approved tradeoff favoring lower computational complexity.
* DD-02: Runtime validation deferred due local environment tool gap.
  * Plan specifies: Validate each phase and full flow using make app.
  * Implementation differs: make app cannot run in current environment because streamlit executable is unavailable.
  * Rationale: Resolved by installing Streamlit in the project virtual environment and validating startup plus end-to-end draft completion.

### Validation Notes

* VN-01: Completed startup validation with make app after environment setup.
* VN-02: Completed end-to-end UI validation by finishing a one-round draft and verifying persisted snapshot write to draft_history.jsonl.
* VN-03: Streamlit emitted deprecation warnings for use_container_width; these are non-blocking and can be addressed in follow-on cleanup.

## Implementation Paths Considered

### Selected: End-Of-Draft Probability Refresh Plus Finished-Page Standings

* Approach: Re-query league markets at draft completion, map drafted team names to refreshed probabilities, aggregate totals, and render standings in finished page.
* Rationale: Accepted by user as an accuracy-versus-cost tradeoff and avoids draft-time payload migration.
* Evidence: User decision in conversation on 2026-07-15.

### IP-01: Late Lookup From Original Pool Snapshot

* Approach: Keep string-only picks and map team names back to odds from a preserved baseline DataFrame at end of draft.
* Trade-offs: Lower immediate migration cost, but fragile under duplicate team names across leagues and missing lookup keys.
* Rejection rationale: Higher risk of incorrect aggregation compared with explicit structured pick payload.

### IP-02: Re-fetch Probabilities At Draft End

* Approach: Re-query live API at finish time and compute totals using current market prices.
* Trade-offs: Captures latest market state but disconnects scoring from drafted selection context and adds runtime/API variability.
* Selection rationale: User approved this path for lower computational cost and accepted small scoring drift.

## Suggested Follow-On Work

* WI-01: Add separate standings CSV export. Provide downloadable winners/losers summary table with totals and rank for sharing (medium)
  * Source: Open question in research
  * Dependency: Base standings section implemented
* WI-02: Replace use_container_width with width argument in dataframes to align with Streamlit deprecation timeline (low)
  * Source: Runtime warnings during validation
  * Dependency: None

## User Decisions

* ID-01: Scoring strategy for standings - Option B selected
  * Rationale: Re-fetching probabilities at draft end is acceptable if computationally cheaper, even with slight drift.
* ID-02: Historical persistence scope - Option A selected
  * Rationale: Promote WI-02 into current implementation scope.
