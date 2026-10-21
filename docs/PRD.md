# SwapTrace — Product Requirements Document

**Product:** SwapTrace — Charging Health & Fault Attribution  
**Version:** 1.0  
**Status:** Implementation specification  
**Target submission:** 27 October 2026  
**Product category:** Battery observability, anomaly detection, diagnostic decision support  
**Reference use case:** Gogoro-like battery-swapping network  
**Data environment:** Public charging telemetry + explicitly semi-synthetic swapping network  
**Product principle:** No actionable owner, no maintenance alert.

---

## 1. Executive Summary

SwapTrace converts battery charging-session telemetry into explainable, owner-specific anomaly signals for operations engineers.

Every battery swap creates a repeatable charging experiment. Batteries move across docks, docks serve different batteries, cells exist within packs, and multiple docks share station-level environmental conditions.

The product exploits these relationships to distinguish four diagnostic ownership categories:

1. **CHARGER_DOCK:** Charging hardware, connector, power delivery, control or local dock cooling.
2. **PACK:** Pack-level electrical, thermal, sensing, BMS or integration issues.
3. **CELL_CHEMISTRY:** Cell-level divergence, electrochemical aging signatures, or chemistry/lot-cohort abnormalities requiring battery engineering investigation.
4. **ENVIRONMENT:** Ambient/site thermal or upstream power conditions affecting otherwise healthy equipment.

The system must not confuse anomaly detection with proven root-cause identification. It produces evidence-supported operational hypotheses and abstains when evidence is insufficient.

## 2. Problem Statement

Traditional anomaly detection may flag a charging session as abnormal without determining who should investigate.

A slow charging session can result from charger current limiting, pack impedance growth, cell voltage constraints, legitimate thermal derating, or upstream supply limitations.

Without attribution, operations teams may inspect healthy chargers, remove healthy packs, or ignore systemic site conditions.

**The product must convert an observed deviation into a defensible operational decision.**

## 3. Product Goals

**G1 — Detect meaningful deviations.** Identify charging behavior outside context-conditioned healthy operating envelopes.

**G2 — Attribute responsibility.** Use historical pack, dock, cell/cohort, and site comparisons to rank the four operational hypotheses.

**G3 — Produce actionable evidence.** Every emitted maintenance alert identifies the entity, responsible team, supporting observations, recommended next step and uncertainty.

**G4 — Control alert fatigue.** Use persistence, suppression, episode deduplication and severity-aware routing.

**G5 — Demonstrate reproducible validation.** Evaluate on public telemetry and a documented, seeded semi-synthetic benchmark with challenging fault scenarios.

**G6 — Provide an operator experience.** Enable engineers to inspect, acknowledge, investigate and resolve alerts.

**G7 — Demonstrate production-oriented engineering.** Deliver modular, tested, deterministic, observable code with documented assumptions and a realistic scaling path.

## 4. Non-Goals

- Autonomous charging-control changes or physical shutdowns.
- Claiming a specific electrochemical degradation mechanism from an ambiguous signal.
- Estimating true SOH or remaining useful life without appropriate labels and validation.
- Building a general-purpose battery digital twin.
- Deploying Kafka, Kubernetes or a multi-service production cluster for the take-home.
- Training large neural networks merely to increase model complexity.
- Pretending that synthetic swapping data are real Gogoro operations.
- Emitting equipment-health alerts for telemetry corruption.
- Providing unsupported numerical confidence probabilities.
- Building an LLM-based diagnostic decision-maker.

## 5. Primary Users

| Persona | Job to be done | Required outcome |
|---|---|---|
| Fleet operations engineer | Prioritize abnormal assets across stations | Actionable alert queue |
| Charging infrastructure technician | Diagnose malfunctioning docks | Dock-specific evidence and inspection instructions |
| Battery service technician | Identify suspect packs | Pack history, independent-dock evidence, diagnostic recommendation |
| Cell/chemistry engineer | Investigate cell/cohort deviations | Cell curves, comparable cohort, limitations |
| Site/facilities operator | Identify shared thermal/power conditions | Station-level correlations and recommended site checks |
| Reliability/data engineer | Trust and operate the pipeline | Data quality, lineage, reproducibility, failure visibility |

## 6. Core Product Experience

### Journey A — Dock fault

An operations engineer opens an alert for dock D-017.

The system shows a persistent charging-current deficit across several independent packs. Those packs charge normally on other docks, while sibling docks at the station remain within expected behavior.

**Output:** CHARGER_DOCK hypothesis, affected dock, evidence counts, curve overlay and inspection action.

### Journey B — Pack fault

A pack exhibits abnormal heating across multiple docks. Other packs using those docks remain normal under comparable charging conditions.

**Output:** PACK hypothesis, affected pack, thermal evidence and battery-service recommendation.

### Journey C — Cell/chemistry investigation

A pack develops persistent cell-voltage divergence during comparable charging windows. The system rules out obvious charger-control anomalies but does not claim a uniquely established degradation mechanism.

**Output:** CELL_CHEMISTRY investigation, suspect cell(s), supporting curves and recommended controlled diagnostics.

### Journey D — Environment/site fault

Several unrelated packs and docks exhibit concurrent power derating associated with abnormal site thermal conditions.

**Output:** ENVIRONMENT hypothesis, affected station, common-mode evidence and facilities investigation.

### Journey E — Insufficient evidence

One pack has only been observed on one dock. A slow-charge anomaly is detected, but the system cannot distinguish pack from charger.

**Output:** Insufficient-attribution state, explanation of missing crossover evidence, and request for an independent diagnostic observation. No unsupported maintenance-fault alert is emitted.

## 7. Feature Scope and Priorities

### P0 — Required for submission

- Canonical telemetry and session contracts.
- Public-data adapter or documented offline fixture with provenance.
- Seeded semi-synthetic pack/dock/station benchmark.
- Session validation, segmentation and charge-phase identification.
- Context-conditioned expected behavior and residual scoring.
- At least one working diagnostic signal per ownership category.
- Cross-pack and cross-dock attribution.
- Explicit insufficient-evidence/abstention behavior.
- Alert persistence, deduplication and owner/action enforcement.
- Reproducible evaluation and four canonical fault demos.
- Operations dashboard and drilldown.
- Automated tests, CLI, README, architecture and limitations.

### P1 — High-value differentiation

- Eight implemented and tested owner-specific feature contracts.
- Crossed-effect or robust peer-contrast attribution.
- Negative-control and ambiguous-case evaluation.
- Point-in-time baseline versioning.
- Alert acknowledgement and resolution feedback.
- Cost-sensitive alert budget analysis.
- Evidence graph and diagnostic comparison visualization.
- Baseline-vs-full-system ablation.

### P2 — Optional, only after P0/P1 pass

- Calibrated probabilistic hypothesis ranking.
- Hierarchical Bayesian modeling.
- Incremental-capacity or differential-voltage analysis with validated sampling conditions.
- Live telemetry ingestion and online/offline parity tests.
- External incident-management integration.
- Grounded LLM incident summarization.
- Production cloud deployment.

P2 work must never jeopardize the complete P0 vertical slice.

## 8. Core Product Requirements

| ID | Requirement | Priority |
|---|---|---|
| PR-01 | Every emitted maintenance alert belongs to exactly one of the four operational categories | P0 |
| PR-02 | Every alert identifies a specific entity or affected site/cohort | P0 |
| PR-03 | Every alert includes evidence and a recommended human action | P0 |
| PR-04 | Every diagnosis exposes supporting and contradicting comparisons | P0 |
| PR-05 | The system can explicitly abstain from unsupported attribution | P0 |
| PR-06 | Healthy but unusual charging conditions do not automatically create maintenance alerts | P0 |
| PR-07 | The operator can inspect raw/derived charge behavior behind an alert | P0 |
| PR-08 | Duplicate observations consolidate into a persistent incident episode | P0 |
| PR-09 | Public, synthetic and injected data are distinguishable by provenance | P0 |
| PR-10 | All demo scenarios are reproducible from a fixed seed | P0 |
| PR-11 | Alert outcomes can be recorded for future evaluation | P1 |
| PR-12 | The dashboard shows data quality and attribution coverage | P1 |
| PR-13 | The system exposes model, feature and baseline versions | P1 |
| PR-14 | Site-wide anomalies can be separated from isolated asset faults when supporting telemetry exists | P1 |

## 9. Success Metrics

Metrics are separated into three layers.

### Detection

- Event-level precision and recall.
- PR-AUC when evaluation labels support it.
- Detection delay in sessions after injected fault onset.
- False alert episodes per 1,000 healthy sessions.
- Detection performance by fault family and operating condition.

### Attribution

- Correct operational-owner classification on held-out injected scenarios.
- Macro-F1 and confusion matrix for the four owners.
- Abstention rate and accuracy on ambiguous cases.
- Evidence support: independent packs, docks, sites and sessions.
- Performance under missing or contradictory evidence.

### Operational usefulness

- 100% of emitted maintenance alerts contain owner, entity, evidence, severity and action.
- Alerts per station/day.
- Deduplicated incident count.
- Percentage of alerts with inspectable evidence.
- Time from detection to simulated acknowledgement.
- Recorded resolution outcomes.

**Important:** Numerical detection and attribution results must be measured, never prewritten or invented. Synthetic-benchmark performance is not field-performance evidence.

## 10. Alert Product Contract

Each maintenance alert must contain:

- Stable alert and episode identifiers.
- Operational owner category and responsible team.
- Affected entity identifier.
- Feature identifier and version.
- Severity and lifecycle state.
- Observed versus expected values, including units.
- Evidence for and against the hypothesis.
- Independent support counts.
- Detection timestamp and evidence time window.
- Data-quality status.
- Baseline/model version.
- Uncertainty or confidence semantics.
- Human-recommended action.
- Supporting session IDs and curve references.
- Audit and provenance metadata.

If mandatory fields cannot be populated, the alert cannot enter the actionable queue.

## 11. Severity Policy

**CRITICAL:** An OEM-defined safety guardrail is breached or imminent safety risk is established. Escalate immediately to an authorized human operator. No automatic physical control action.

**HIGH:** Persistent, well-supported fault with significant operational impact or credible risk requiring prompt inspection.

**MEDIUM:** Repeated abnormality with adequate evidence but lower urgency.

**LOW:** Nonurgent investigation or trend; do not page.

**INSUFFICIENT_EVIDENCE:** An abnormal observation without enough evidence for an owner-specific maintenance diagnosis. Store for investigation, not as a confirmed owner alert.

Severity and attribution confidence are different concepts.

## 12. Dashboard Requirements

### Screen 1 — Fleet health

Display total sessions, eligible sessions, quality rejects, open incidents, affected assets, owner breakdown and alert rate.

### Screen 2 — Actionable alert inbox

Provide severity, owner, entity, summary, support, state, time and recommended action.

Support filters for station, owner, severity and incident state.

### Screen 3 — Incident drilldown

Show:

- Observed versus expected charging behavior.
- Same pack on other docks.
- Other packs on the same dock.
- Sibling dock and station comparisons.
- Cell-level evidence when available.
- Environment and data-quality context.
- Supporting and contradicting evidence.
- Explicit diagnostic limitations.
- Human next action.

### Screen 4 — Evaluation and reliability

Show benchmark metrics, confusion matrix, negative controls, abstentions, feature coverage, run metadata and pipeline quality.

## 13. Data and Scientific Integrity

The product must distinguish:

**Observed:** A measured current shortfall or temperature increase.

**Estimated:** A context-conditioned expected value or residual.

**Inferred:** A likely operational owner based on comparative evidence.

**Unverified:** The underlying physical failure mechanism pending inspection.

The user interface must never present an inferred owner as laboratory-confirmed causality.

## 14. Launch / Submission Acceptance

The submission is acceptable only if a reviewer can:

1. Install and run the project from documented commands.
2. Generate or load traceable telemetry.
3. Produce features and alerts end to end.
4. Reproduce all four diagnostic categories.
5. Inspect at least one convincing pack-versus-dock counterfactual.
6. Reproduce an abstention case.
7. Execute automated tests.
8. Inspect measured evaluation results.
9. Understand assumptions, limitations and production migration.
10. Identify exactly what was implemented versus only designed.

**Product completion condition:** A real engineer can understand the evidence, decide what to investigate, and see why the proposed action is more appropriate than an alternative.
