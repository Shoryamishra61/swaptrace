# SwapTrace — Definition of Done & Quality Gates

**Release:** Submission Candidate 1.0  
**Deadline:** 27 October 2026  
**Gate owners:** Engineering, Data Science, Battery Domain, QA, Product  
**Release rule:** All P0 gates must pass. No critical scientific-integrity or correctness failures are permitted.

---

## GATE 0 — Requirements and Traceability

- [ ] PRD and SRS are committed.
- [ ] Requirements have stable IDs and priorities.
- [ ] Each P0 requirement maps to code, a test and observable output.
- [ ] Assumptions are documented separately from verified facts.
- [ ] Implemented functionality is distinguishable from proposed extensions.
- [ ] No feature exists solely because it is easy to calculate.
- [ ] Every alertable feature has an operational owner and action.
- [ ] Unsupported root-cause claims are prohibited.
- [ ] Reviewer can identify the project's central differentiator within 60 seconds of opening the README.

**Pass evidence:** Requirements traceability matrix and feature registry.

## GATE 1 — Dataset Integrity

- [ ] Public-data source, URL, attribution and access/usage terms are documented.
- [ ] Public-data fields are mapped to canonical units and schemas.
- [ ] Synthetic asset identities are explicitly identified.
- [ ] Injected faults are explicitly labeled in evaluation ground truth.
- [ ] Original observed measurements are not mislabeled as simulated or vice versa.
- [ ] Fixed random seeds reproduce the benchmark.
- [ ] Data generation does not use future evaluation labels in detection logic.
- [ ] Dataset splits avoid telemetry-row and reused-trajectory leakage.
- [ ] Sensor availability and missingness are explicit.
- [ ] Generated current, voltage, charge and energy are physically consistent within documented tolerances.
- [ ] Public-data download failure does not break the offline core demo.
- [ ] No unauthorized redistribution of third-party data occurs.

**Pass evidence:** Source manifest, dataset card, generator tests and deterministic regeneration.

## GATE 2 — Data Quality and Session Processing

- [ ] Event timestamps are normalized to UTC.
- [ ] Duplicate events are handled deterministically.
- [ ] Out-of-order samples are handled.
- [ ] Nonmonotonic timestamps are detected.
- [ ] Missing identifiers are rejected or explicitly inferred.
- [ ] Invalid numeric values are quarantined.
- [ ] Units and current sign conventions are tested.
- [ ] Sensor gaps are detected and not silently interpolated across invalid intervals.
- [ ] Session boundaries are reproducible.
- [ ] Partial/aborted sessions are distinguished from completed sessions.
- [ ] Charge phases include UNKNOWN when evidence is inadequate.
- [ ] Each feature checks required sensor capabilities.
- [ ] Data-quality incidents cannot be mislabeled as charger or battery faults.
- [ ] Replaying the same input does not create duplicate derived records.

**Pass evidence:** Unit/property tests, quality report and replay test.

## GATE 3 — Feature Engineering

For every P0 alertable feature:

- [ ] Operational question is defined.
- [ ] One primary owner category is assigned.
- [ ] Required telemetry is declared.
- [ ] Formula and units are documented.
- [ ] Valid charge windows are defined.
- [ ] Confounders are documented.
- [ ] Baseline comparison population is specified.
- [ ] Missingness behavior is specified.
- [ ] Minimum evidence support is specified.
- [ ] Action recommendation is documented.
- [ ] Feature version is recorded.
- [ ] Normal-case unit test passes.
- [ ] Positive fault-injection test passes.
- [ ] Negative-control test passes.
- [ ] Feature output can be traced to input sessions.
- [ ] Unsupported conditions produce NOT_COMPUTABLE rather than a misleading value.

**Pass evidence:** Feature catalog, registry validation and per-feature test reports.

## GATE 4 — Attribution and Uncertainty

- [ ] Dock faults are tested across multiple packs.
- [ ] Pack faults are tested across multiple docks.
- [ ] Cell/chemistry features use actual available cell/curve evidence.
- [ ] Environmental diagnoses require measured shared-condition support.
- [ ] Crossed pack/dock support is computed.
- [ ] Confounding by SOC, temperature, protocol and age is tested.
- [ ] Insufficient graph crossing triggers abstention.
- [ ] Conflicting hypotheses trigger abstention or explicit ambiguity.
- [ ] A site-wide shared-hardware failure is not automatically labeled environment.
- [ ] Competing owner evidence is inspectable.
- [ ] No uncalibrated model score is displayed as a probability.
- [ ] Future sessions do not influence historical attribution.
- [ ] Baseline contamination is tested.
- [ ] Concurrent faults are represented as an ambiguity or multi-incident challenge, not forced into an unjustified single cause.

**Pass evidence:** Attribution scenario suite, evidence traces and confusion matrix.

## GATE 5 — Alert Actionability

- [ ] 100% of maintenance alerts have a valid owner category.
- [ ] 100% identify an affected entity.
- [ ] 100% contain a human-recommended action.
- [ ] 100% contain traceable evidence.
- [ ] 100% contain a severity.
- [ ] 100% contain provenance and version information.
- [ ] Routine transient anomalies do not flood the queue.
- [ ] Repeated detections consolidate into an incident episode.
- [ ] Severity and confidence are not conflated.
- [ ] Safety escalation uses configured, sourced limits.
- [ ] No autonomous physical control actions occur.
- [ ] Incident state transitions are auditable.
- [ ] Reprocessing does not duplicate alerts.
- [ ] Resolved and dismissed outcomes are distinguishable.

**Pass evidence:** Alert schema tests and incident lifecycle integration tests.

## GATE 6 — Evaluation

- [ ] Static threshold baseline is implemented.
- [ ] Contextual detector is evaluated.
- [ ] Full attribution pipeline is evaluated.
- [ ] Chronological holdout is used.
- [ ] Group-held-out asset test is included.
- [ ] At least one scenario exists for each owner.
- [ ] All four owner demo scenarios are reproducible.
- [ ] Healthy-but-unusual negative controls are included.
- [ ] Missing-sensor and insufficient-evidence tests are included.
- [ ] Concurrent/ambiguous fault test is included.
- [ ] Detection metrics are reported.
- [ ] Attribution metrics are reported.
- [ ] Abstention behavior is reported.
- [ ] False alert episodes per 1,000 healthy sessions are reported.
- [ ] Detection delay is reported.
- [ ] Ablation results are included.
- [ ] Results are generated by executable code, not hard-coded into reports.
- [ ] Evaluation explains synthetic-data limitations.

### Proposed engineering targets

These are acceptance targets to attempt and measure, not pre-established performance claims.

| Metric | Target |
|---|---|
| Actionable alert schema completeness | 100% |
| Canonical owner demo scenarios | 4/4 pass |
| Required negative controls | All pass |
| Deterministic replay | Equivalent logical outputs |
| Known leakage tests | 0 failures |
| Automated critical-path tests | 100% pass |
| Core-domain code coverage | ≥90% targeted, measured |
| False alerts on seeded healthy benchmark | Aim ≤20 per 1,000 healthy sessions |
| Attribution macro-F1 on held-out synthetic faults | Aim ≥0.80, with abstention and coverage reported separately |
| P0 pipeline performance | Benchmark against documented runtime/memory targets |

Do not manipulate scenario difficulty or thresholds merely to hit a headline number. Report failures honestly.

## GATE 7 — Software Engineering

- [ ] Package installs from a fresh checkout.
- [ ] Lockfile is committed.
- [ ] No hidden dependency on local absolute paths.
- [ ] No credentials in repository.
- [ ] CLI commands are documented.
- [ ] Tests pass in CI.
- [ ] Ruff checks pass.
- [ ] Required mypy checks pass.
- [ ] Critical functions have type hints.
- [ ] Core modules have meaningful docstrings.
- [ ] No broad exception swallowing.
- [ ] Structured logs identify pipeline stage and run.
- [ ] Pipeline failures return nonzero exit status.
- [ ] Configurations are externalized.
- [ ] Randomness is controlled.
- [ ] Generated artifacts include provenance manifests.
- [ ] Docker path is tested.
- [ ] No oversized generated data are committed.
- [ ] Core logic is outside notebooks.
- [ ] A reviewer can run the demo without cloud credentials.

**Pass evidence:** Clean CI, clean-container smoke test and reproducibility manifest.

## GATE 8 — Operations Dashboard

- [ ] Dashboard launches against generated artifacts.
- [ ] Fleet summary is visible.
- [ ] Alert queue prioritizes actionable incidents.
- [ ] Four ownership categories are distinguishable.
- [ ] Incident drilldown displays observed and expected curves.
- [ ] Cross-asset evidence is visible.
- [ ] Competing hypotheses or limitations are visible.
- [ ] Data quality and sensor eligibility are visible.
- [ ] Recommended human action is prominent.
- [ ] Acknowledgement/resolution workflow functions.
- [ ] Synthetic demo data are labeled.
- [ ] Screenshots match the actual running application.
- [ ] No fabricated screenshots, metrics or alert evidence are used.

**Pass evidence:** Recorded end-to-end demo and screenshots from the actual application.

## GATE 9 — Documentation

- [ ] README includes the problem, insight and architecture.
- [ ] README provides a quickstart with exact commands.
- [ ] PRD is included.
- [ ] SRS is included.
- [ ] Feature catalog is included.
- [ ] Dataset provenance is included.
- [ ] Benchmark design is included.
- [ ] Evaluation methodology is included.
- [ ] Results and failures are included.
- [ ] Architecture tradeoffs are explained.
- [ ] Production migration is described.
- [ ] Limitations and identifiability constraints are explicit.
- [ ] Alert runbook maps each owner to a human investigation.
- [ ] Repository contains a short reviewer walkthrough.
- [ ] Known limitations are not hidden.

## GATE 10 — Adversarial Reviewer Defense

A reviewer should be able to ask each question and receive a defensible answer backed by code or evidence.

| Question | Required defense |
|---|---|
| Why isn't Isolation Forest enough? | Detection alone does not identify operational ownership |
| How do you distinguish pack from dock? | Crossed observations and independent peer contrasts |
| What if a pack only visits one dock? | Insufficient crossing; abstain |
| How do you prevent leakage? | Temporal cutoffs, source-trajectory isolation and point-in-time baselines |
| Is your dataset real? | Explicit real/synthetic/injected provenance |
| Why should synthetic accuracy be trusted? | It tests controlled localization logic, not field accuracy |
| What if high ambient causes slow charging? | Condition on temperature and examine shared site evidence |
| How do you distinguish environment from shared station hardware? | Require measured explanatory signals or abstain |
| Can cell voltage spread prove chemistry failure? | No; it is a cell-level investigation signal |
| Can you estimate true resistance from arbitrary charge samples? | No; require valid excitation/measurement geometry |
| Why not use a Transformer? | No demonstrated incremental operational value for the scoped problem |
| What happens when sensors are missing? | Capability gating and explicit non-computability |
| What prevents alert fatigue? | Persistence, episodes, deduplication and alert budget evaluation |
| How are confidence values calibrated? | Use qualitative evidence support unless calibrated probabilities are validated |
| What happens with simultaneous faults? | Competing hypotheses and explicit ambiguity |
| What does production-ready mean here? | Production-oriented contracts/tests/replay, not falsely claimed deployment |
| How would the system improve after launch? | Technician feedback, outcome labels and monitored baseline/model updates |
| What is the strongest product insight? | The pack–dock rotation structure enables operational counterfactual diagnosis |

## GATE 11 — Submission Package

- [ ] Public/private repository access is correctly configured for reviewers.
- [ ] README renders cleanly.
- [ ] Quickstart is tested from a clean environment.
- [ ] Main branch is green.
- [ ] Release commit/tag is recorded.
- [ ] Demo scenarios work without manual source editing.
- [ ] Evaluation artifacts are regenerated from code.
- [ ] Architecture diagram is readable.
- [ ] Dashboard screenshots are authentic.
- [ ] A concise technical memo is included.
- [ ] A short walkthrough video is recorded if time permits.
- [ ] No unfinished P0 task is described as complete.
- [ ] Final submission instructions and deadline are verified.

---

## Six-Day Execution Plan

### 21 October — Architecture and data foundation

**Deliver:** PRD, SRS, repository scaffold, schema contracts, generator design, source manifest, working installation.

**Exit gate:** Generate valid sessions and run schema tests.

### 22 October — Physics and feature extraction

**Deliver:** Sessionization, phase handling, charge/energy integration, feature registry and first owner-specific features.

**Exit gate:** Positive and negative feature tests pass.

### 23 October — Context and attribution

**Deliver:** Contextual baselines, residuals, pack–dock graph, cross-asset comparisons, abstention.

**Exit gate:** Same symptom can be correctly localized to pack or dock.

### 24 October — Benchmark and evaluation

**Deliver:** Four owner demos, fault injection suite, negative controls, temporal holdout, baseline comparison and metrics.

**Exit gate:** End-to-end evaluation runs reproducibly.

### 25 October — Operator product

**Deliver:** Alert policy, deduplication, evidence drilldown, dashboard, resolution feedback and runbook.

**Exit gate:** A reviewer can investigate all four fault categories in the UI.

### 26 October — Release hardening

**Deliver:** CI, Docker, reproducibility checks, adversarial testing, measured results, README, screenshots and technical memo.

**Exit gate:** All P0 gates pass on a clean checkout.

### 27 October — Submission buffer

**Deliver:** Final verification, submission and confirmation.

No major new feature development unless correcting a release-blocking defect.

---

## Release Decision

**PASS:** All P0 gates are green, demo is reproducible, owner attribution is evidenced, and limitations are disclosed.

**CONDITIONAL:** Core pipeline works but a noncritical P1 feature is incomplete; disclose and submit.

**FAIL:** Pipeline cannot run end to end, evaluation is fabricated/leaky, or maintenance alerts lack defensible ownership/action.

**Final rule:** Prefer a smaller verified product over a larger unverified claim.
