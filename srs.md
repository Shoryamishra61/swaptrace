# SwapTrace — Software Requirements Specification

**Specification version:** 1.0  
**Implementation language:** Python 3.12  
**Architecture:** Modular monolith with deterministic batch processing  
**Deployment target:** Reproducible local/Docker execution  
**Production evolution:** Event-driven ingestion and independently scalable processing  
**System status:** Proposed design; implementation and benchmarks must be verified

---

## 1. Architectural Overview

```text
PUBLIC TELEMETRY         SYNTHETIC SWAP NETWORK
       |                           |
       +-------------+-------------+
                     |
              RAW DATA LAYER
                     |
            SCHEMA VALIDATION
                     |
          SESSION RECONSTRUCTION
                     |
          CHARGE-PHASE DETECTION
                     |
           FEATURE COMPUTATION
                     |
          CONTEXTUAL BASELINES
                     |
          NORMALIZED RESIDUALS
                     |
         PACK × DOCK ATTRIBUTION
                     |
          PERSISTENCE + POLICY
                     |
             ALERT EPISODES
                     |
        +------------+------------+
        |                         |
   OPS DASHBOARD             EVALUATION
        |                         |
  HUMAN FEEDBACK          REPRODUCIBLE REPORT
```

The implementation must be organized as independent, testable modules with typed interfaces.

## 2. Technology Decisions

| Component | Selected technology | Rationale |
|---|---|---|
| Language | Python 3.12 | Scientific ecosystem, maintainability |
| Package management | uv + locked dependencies | Reproducible installation |
| Data processing | Polars | Efficient columnar processing |
| Analytical persistence | DuckDB + Parquet | Local analytical queries and portable artifacts |
| Contracts | Pydantic + explicit dataframe validators | Typed boundaries and quality rules |
| Modeling | NumPy, SciPy, scikit-learn | Interpretable baselines and robust statistics |
| CLI | Typer | Repeatable pipeline commands |
| Dashboard | Streamlit + Plotly | Fast operations-facing demonstration |
| Tests | pytest + Hypothesis where valuable | Unit, property and integration testing |
| Static quality | Ruff + mypy on core modules | Formatting, linting and type safety |
| Packaging | Docker + Makefile | Reproducible execution |
| CI | GitHub Actions | Automated quality gates |

Avoid adding infrastructure dependencies without a documented requirement.

## 3. Canonical Data Contracts

### 3.1 TelemetryEvent

Required fields:

| Field | Type | Unit / semantics |
|---|---|---|
| event_id | string | Stable unique event identifier |
| event_ts | UTC timestamp | Measurement event time |
| ingest_ts | UTC timestamp | Ingestion time |
| session_id | string | Charge-session identity |
| station_id | string | Station identity |
| dock_id | string | Dock identity |
| pack_id | string | Battery-pack identity |
| charge_protocol_id | string | Protocol/configuration identity |
| charger_current_a | float/null | Measured charger current, A |
| charger_voltage_v | float/null | Measured charger voltage, V |
| pack_current_a | float/null | Measured pack current, A |
| pack_voltage_v | float/null | Measured pack voltage, V |
| pack_temperature_c | float/null | Measured pack temperature, °C |
| soc_pct | float/null | BMS-estimated SOC, 0–100% |
| source_type | enum | PUBLIC / SYNTHETIC / INJECTED |
| source_record_id | string | Provenance reference |

Optional but high-value:

```text
commanded_current_a
commanded_voltage_v
charge_phase
charge_state
ambient_temperature_c
dock_temperature_c
cell_voltage_v[]
cell_temperature_c[]
chemistry_id
cell_lot_id
equivalent_cycles
rated_capacity_ah
ac_input_voltage_v
bms_limit_reason
charger_error_code
charger_fan_rpm
```

Missing optional fields must remain missing; they must never be silently fabricated as observations.

### 3.2 ChargeSession

```text
session_id
pack_id
dock_id
station_id
chemistry_id?
start_ts
end_ts
initial_soc_pct?
final_soc_pct?
initial_pack_temperature_c?
ambient_temperature_c?
charge_protocol_id
charge_status
phase_intervals
integrated_charge_ah?
integrated_energy_wh?
data_quality_status
data_quality_reasons[]
sensor_capabilities[]
source_type
source_dataset
pipeline_version
```

A session can be complete, partial, aborted or quality-rejected. Incomplete sessions must not be treated as healthy completed charges.

### 3.3 FeatureRecord

```text
feature_id
feature_version
session_id
entity_type
entity_id
value
unit
expected_value?
residual?
normalized_score?
context_signature
baseline_version
validity_status
invalidity_reason?
sample_count
supporting_session_ids[]
computed_at
```

### 3.4 AttributionResult

```text
session_id / episode_id
candidate_owners[]
owner_evidence
owner_counterevidence
crossing_support
selected_owner?
attribution_status
confidence_semantics
explanation
```

`attribution_status` must support:

```text
ATTRIBUTED
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
NOT_ELIGIBLE
```

### 3.5 AlertEpisode

```text
alert_id
episode_key
owner_category
owner_team
entity_id
severity
status
feature_ids[]
observed_values
expected_values
evidence
counterevidence
independent_support_counts
recommended_actions[]
first_seen_ts
last_seen_ts
opened_at
baseline_version
pipeline_version
data_provenance
resolution?
```

Valid lifecycle transitions:

```text
OPEN → ACKNOWLEDGED → INVESTIGATING → RESOLVED
                                  → DISMISSED
RESOLVED → REOPENED
```

Every transition must retain timestamp, actor and optional reason.

## 4. Functional Requirements

### FR-001 — Data ingestion

The system shall ingest at least one documented public charging dataset and one deterministic semi-synthetic network dataset.

**Acceptance:** The ingestion manifest identifies original source, download/access instructions, transformation version, data license/status, schema mapping and excluded fields.

### FR-002 — Provenance

The system shall distinguish real observed measurements from simulated topology and injected signals.

**Acceptance:** Any evaluated session can be traced to its generating seed or original public record.

### FR-003 — Data validation

The system shall validate identifiers, timestamps, units, numerical ranges, array dimensions and sensor capabilities.

**Acceptance:** Invalid rows are quarantined with machine-readable reasons.

### FR-004 — Idempotency

Repeated ingestion of the same event or batch shall not duplicate session features or alerts.

**Acceptance:** Replaying identical input yields identical logical outputs and stable identifiers.

### FR-005 — Event-time ordering

The system shall process events in event-time order, handling duplicates and out-of-order arrival.

**Acceptance:** Reordering the input file does not change final features for a completed session.

### FR-006 — Sessionization

The system shall reconstruct charging sessions using explicit IDs/state transitions when available.

If IDs are absent, deterministic inference must use documented rules and mark inferred identities.

**Acceptance:** No valid sample belongs to more than one session.

### FR-007 — Charge-phase detection

The system shall identify relevant charging phases using recorded state or validated signal-based inference.

**Acceptance:** Phase assignments are reproducible and include an UNKNOWN state for ambiguous intervals.

### FR-008 — Sensor-capability gating

Each feature shall declare mandatory sensors and minimum sampling/quality requirements.

**Acceptance:** Missing required signals produce NOT_COMPUTABLE, not a fabricated zero or false normal.

### FR-009 — Physical feature extraction

The system shall calculate charge, energy, current-tracking, thermal and voltage features only in physically valid windows.

For irregular sampling:

\[
Q_{Ah}=\frac{1}{3600}\sum_i \frac{I_i+I_{i+1}}{2}\Delta t_i
\]

\[
E_{Wh}=\frac{1}{3600}\sum_i \frac{P_i+P_{i+1}}{2}\Delta t_i
\]

Use consistent current direction and appropriate measurement boundaries.

**Acceptance:** Unit tests cover sign conventions, timestamps, units and irregular sampling.

### FR-010 — Session alignment

The system shall compare charging behavior over compatible SOC, voltage, charge-throughput or phase windows.

**Acceptance:** Unsupported extrapolation is prohibited and common comparison coverage is recorded.

### FR-011 — Contextual baselines

Expected behavior shall be conditioned on available operating context:

```text
initial SOC / matched charge window
initial pack temperature
ambient temperature
charge protocol
chemistry / cell type
age or equivalent cycles where available
```

**Acceptance:** The baseline reports its training population, version, coverage and unsupported contexts.

### FR-012 — Point-in-time correctness

Only observations available before the scored session's cutoff shall be used for historical baseline fitting or asset-history evidence.

**Acceptance:** Leakage tests fail if future sessions influence past predictions.

### FR-013 — Robust residuals

The system shall calculate context-normalized deviations with documented scale estimates and safeguards against zero variance.

**Acceptance:** Constant baselines, tiny cohorts and outliers are handled explicitly.

### FR-014 — Pack/dock graph construction

The system shall maintain the observed bipartite relationship between packs and docks.

**Acceptance:** The system can report distinct independent packs/docks, connected-component support and insufficient crossing.

### FR-015 — Cross-entity attribution

The system shall distinguish persistent dock effects from persistent pack effects using independent cross-asset observations.

**Acceptance:** The same slow-charge symptom injected as a dock fault and as a pack fault produces different diagnoses when sufficient evidence exists.

### FR-016 — Cell/chemistry attribution

The system shall support cell-level or chemistry/cohort signals where the required data exist.

**Acceptance:** Cell divergence is described as a diagnostic signature, not proof of a specific chemical mechanism.

### FR-017 — Environmental attribution

The system shall detect shared site/time effects supported by environmental or upstream power measurements.

**Acceptance:** A common-mode symptom without sufficient source evidence cannot automatically be declared environmental.

### FR-018 — Persistence

Non-safety maintenance alerts shall require configurable repeated evidence or a validated change detector.

**Acceptance:** A single ordinary transient does not create a maintenance episode.

### FR-019 — Safety escalation

Configured OEM/safety constraints may bypass persistence and route for immediate human review.

**Acceptance:** Thresholds are configuration-driven and never presented as verified OEM limits unless sourced.

### FR-020 — Owner/action enforcement

Every emitted maintenance alert shall contain an owner, evidence, action and severity.

**Acceptance:** Schema validation rejects actionless or unowned maintenance alerts.

### FR-021 — Deduplication

Related observations shall be grouped into stable incident episodes.

**Acceptance:** Replaying a session or repeatedly detecting the same ongoing fault does not create a new ticket each time.

### FR-022 — Evidence explanations

Each attributed alert shall contain supporting and contradicting evidence.

**Acceptance:** The incident drilldown answers "Why this owner instead of the alternatives?"

### FR-023 — Human feedback

The system shall support acknowledgement, investigation and resolution outcomes.

**Acceptance:** Feedback persists without silently altering historical prediction records.

### FR-024 — Evaluation

The system shall evaluate detection, attribution, abstention and operational alert burden independently.

**Acceptance:** Metrics are produced from held-out benchmark labels and exported to machine-readable artifacts.

### FR-025 — Reproducible replay

The system shall support deterministic end-to-end processing from a fixed seed and configuration.

**Acceptance:** Two clean runs produce equivalent session, feature, attribution and alert outputs.

### FR-026 — Operator interface

The system shall provide an alert inbox and evidence drilldown.

**Acceptance:** A reviewer can inspect all four owner categories and at least one insufficient-evidence case.

### FR-027 — Pipeline observability

The system shall expose counts of ingested, accepted, rejected, feature-eligible, scored and alerted sessions.

**Acceptance:** Processing failures cannot silently masquerade as healthy results.

## 5. Feature Registry Specification

Each alertable feature shall declare:

```yaml
feature_id: string
version: integer
owner_category: enum
operational_question: string
required_signals: [string]
valid_phases: [string]
formula_reference: string
unit: string
comparison_context: [string]
baseline_population: string
minimum_evidence: object
known_confounders: [string]
positive_test: string
negative_control_test: string
action: [string]
severity_policy: string
```

The registry shall be validated at application startup.

## 6. Required Feature Families

The following eight features define the target feature portfolio. Features without valid source measurements must be disabled rather than faked.

| ID | Feature | Evidence / calculation | Owner | Recommended action |
|---|---|---|---|---|
| F-D01 | Dock current-control residual | Delivered versus commanded CC current across independent packs | CHARGER_DOCK | Inspect charger control/power delivery |
| F-D02 | Dock contact-path resistance excess | Synchronized charger–pack voltage difference divided by current, under validated measurement geometry | CHARGER_DOCK | Inspect connector/cable/contact path |
| F-P01 | Pack thermal residual | Observed versus context-expected pack temperature rise under comparable load | PACK | Inspect pack thermal hardware and sensors |
| F-P02 | Pack electrical-response/resistance anomaly | Controlled current-step voltage response or validated matched-state polarization proxy across docks | PACK | Run pack electrical/BMS diagnostics |
| F-C01 | Cell voltage divergence | Cell-to-peer voltage dispersion at comparable charge state | CELL_CHEMISTRY | Inspect suspect cells and validate sensor readings |
| F-C02 | Chemistry/cohort curve drift | Charging-curve fingerprint deviation relative to comparable chemistry/age cohort | CELL_CHEMISTRY | Conduct battery engineering diagnostics |
| F-E01 | Site-wide thermal derating | Shared performance residual correlated with measured site thermal conditions | ENVIRONMENT | Inspect site cooling/ventilation |
| F-E02 | Upstream supply sag | Measured AC supply excursions associated with multi-dock power loss | ENVIRONMENT | Inspect station electrical supply |

### Scientific guardrails

**F-D01:** Legitimate BMS current limits must not be mistaken for charger failure.

**F-D02:** Voltage taps must refer to known electrical boundaries, timestamps must be aligned, and current must be sufficiently nonzero. Otherwise do not compute a resistance estimate.

**F-P01:** Temperature rise must be conditioned on current, starting temperature, ambient and duration. A hot pack is not automatically defective.

**F-P02:** Do not infer true DC internal resistance from arbitrary differences in unrelated charging-curve samples.

**F-C01:** Cell-voltage spread may result from imbalance, sensor offset, cell variation or aging. Route to cell engineering; do not claim proven chemistry failure.

**F-C02:** Curve-based chemistry signatures require valid sampling, protocol and comparison cohorts. They are diagnostic indicators, not definitive mechanism labels.

**F-E01:** Site-wide effects can also originate from shared infrastructure. Require supporting thermal evidence; otherwise abstain.

**F-E02:** Without AC input telemetry, do not claim a grid-sag diagnosis.

## 7. Baseline and Attribution Design

### 7.1 Context normalization

For each feature \(x_s\), estimate:

\[
\hat{x}_s=f(c_s)
\]

where \(c_s\) contains valid operating context.

Then:

\[
r_s=x_s-\hat{x}_s
\]

A robust standardized residual may be:

\[
z_s=0.6745\frac{r_s-\operatorname{median}(r_{\mathrm{reference}})}
{MAD(r_{\mathrm{reference}})+\epsilon}
\]

Reference statistics must come from eligible historical training observations, not from the evaluation future.

### 7.2 Attribution hypothesis

For an eligible session:

\[
r_s=\alpha_{pack(s)}+\beta_{dock(s)}
+\gamma_{cohort(s)}+h(site,time,environment)+\epsilon_s
\]

This is a conceptual decomposition, not proof that all effects are separately identifiable.

The implementation may use robust peer contrasts first, followed by regularized crossed effects if the data support them.

### 7.3 Dock evidence

A dock hypothesis gains support when:

- Multiple independent packs exhibit a similar abnormality at the same dock.
- Those packs exhibit normal behavior on other docks.
- Comparable sibling docks do not show the same anomaly.
- BMS limits, temperature and protocol do not explain the deviation.

### 7.4 Pack evidence

A pack hypothesis gains support when:

- The same pack exhibits an abnormality across independent docks.
- Those docks serve other packs normally.
- The effect persists under comparable charging conditions.
- Known charger or site explanations are unsupported.

### 7.5 Cell/chemistry evidence

A cell/chemistry hypothesis gains support when:

- Valid cell-level or electrochemical-curve measurements show divergence.
- The deviation persists under compatible protocol and thermal conditions.
- Relevant pack/dock control effects do not explain the signature.
- Chemistry/cohort comparisons are available where a cohort claim is made.

### 7.6 Environment evidence

An environmental hypothesis gains support when:

- Multiple independent packs and docks exhibit a concurrent deviation.
- A measured shared environmental variable explains the timing/direction.
- Asset-specific effects alone do not adequately explain the pattern.
- Shared upstream hardware faults are considered as competing hypotheses.

### 7.7 Abstention

The system must abstain when:

- A pack/dock relationship lacks independent crossing.
- Required sensors are unavailable.
- Reference cohorts are too small.
- Context is outside baseline coverage.
- Competing hypotheses have similar evidence.
- Measurements are corrupted.
- An observed site-wide effect cannot be localized to environment versus shared equipment.

**Confidence policy:** Initially use evidence-based HIGH / MEDIUM / LOW / INSUFFICIENT rather than uncalibrated percentages. Numerical probabilities are allowed only after explicit calibration evaluation.

## 8. Benchmark Specification

### 8.1 Dataset strategy

Use:

1. Public battery charge trajectories, with original provenance retained.
2. Explicitly synthetic pack/dock/station identities and rotation schedules.
3. Seeded fault injections with documented mechanisms.
4. Independent ground-truth labels reserved for evaluation.

Recommended public-data candidate: NASA PCoE lithium-ion battery aging data. Additional external validation may use CALCE or published EV charging datasets, subject to verified access and usage terms.

The benchmark shall never be described as a real Gogoro dataset.

### 8.2 Default local scale

Proposed development profile:

```text
4 stations
16 docks
80 packs
2 chemistry/cohort groups
14 simulated days
~2,000 sessions
30-second nominal sample interval
```

Exact generated counts must be reported, not assumed.

Provide a separate larger stress profile only after the standard demo is reliable.

### 8.3 Required fault scenarios

```text
S01  Dock current clipping
S02  Dock contact degradation
S03  Pack self-heating increase
S04  Pack electrical-response change
S05  Cell voltage divergence
S06  Chemistry/cohort curve drift
S07  Site cooling/thermal event
S08  Upstream supply voltage sag
```

Required challenging scenarios:

```text
N01  Healthy long charge caused by low starting SOC
N02  Legitimate temperature-based charging derating
N03  Healthy old pack with stable age-adjusted behavior
N04  One isolated sensor spike
N05  Pack/dock graph with inadequate crossing
N06  Concurrent pack and dock fault
N07  Site-wide common-mode anomaly with missing cause sensor
N08  Missing cell or AC telemetry
N09  Out-of-order and duplicate events
N10  Previously faulty assets contaminating baseline candidates
```

Injected faults must obey plausible physical and measurement relationships. If voltage/current are altered, derived energy, temperature or other dependent measurements must be treated consistently or explicitly identified as independently simulated.

### 8.4 Evaluation split

Mandatory:

- Chronological training/validation/test split.
- Fault-onset separation.
- Group-held-out pack or dock generalization test.
- No use of injected ground-truth labels as model features.
- No baseline fitting on future test observations.
- No randomized telemetry-row split.

Ablation:

```text
A0  Static global threshold
A1  Contextual residual detector
A2  Contextual residual + persistence
A3  Contextual residual + persistence + crossed attribution
```

Report detection and attribution separately. A0/A1 may detect anomalies without being capable of owner localization.

## 9. Nonfunctional Requirements

| ID | Requirement | Acceptance target |
|---|---|---|
| NFR-01 | Determinism | Same seed/config/input gives equivalent logical outputs |
| NFR-02 | Reproducibility | Fresh checkout follows documented setup and run commands |
| NFR-03 | Performance | Proposed target: standard benchmark completes in ≤5 minutes on a documented 4-core/16-GB reference machine; report measured result |
| NFR-04 | Memory | Standard profile operates within 8 GB RSS target; report measured result |
| NFR-05 | Quality | All automated tests and required lint/type checks pass |
| NFR-06 | Traceability | Every alert links to features, sessions, baseline and source provenance |
| NFR-07 | Privacy | No rider identity, personal contact data or location history required |
| NFR-08 | Reliability | Invalid records are quarantined without silent data loss |
| NFR-09 | Configuration | Thresholds, cohorts and policies are externalized and versioned |
| NFR-10 | Security | No embedded credentials; input validation and dependency hygiene |
| NFR-11 | Portability | Linux/macOS local setup and Docker run path documented |
| NFR-12 | Observability | Structured logs, stage counts, runtime and quality metrics |
| NFR-13 | Auditability | Human alert transitions and pipeline versions are recorded |
| NFR-14 | Safety | No automatic physical charger/pack intervention |
| NFR-15 | Honest provenance | Synthetic and inferred values are visibly labeled |

Performance targets are engineering objectives, not claims of achieved results.

## 10. Storage and Processing Rules

Use a lightweight three-stage data layout:

```text
data/raw/         Immutable source and manifests
data/validated/   Validated, canonical session/event tables
data/derived/     Features, baselines, attribution and alerts
```

Large generated datasets should not be committed to Git.

Persist manifests containing:

```text
run_id
seed
git_commit
configuration_hash
schema_version
feature_versions
baseline_version
source_manifest
start_time
end_time
row_counts
quality_counts
```

### Batch semantics

- Use deterministic event IDs.
- Normalize timestamps to UTC.
- Preserve event time and ingestion time separately.
- Apply a documented late-arrival/finalization policy.
- Recompute affected sessions when corrected data arrive.
- Upsert derived records using stable logical keys.
- Never silently mutate historical alert evidence.

## 11. Repository Structure

```text
swaptrace/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── uv.lock
├── Makefile
├── Dockerfile
├── .github/workflows/ci.yml
├── configs/
│   ├── pipeline.yaml
│   ├── features.yaml
│   ├── alerts.yaml
│   └── benchmark.yaml
├── src/swaptrace/
│   ├── cli.py
│   ├── contracts/
│   ├── ingestion/
│   ├── quality/
│   ├── sessions/
│   ├── physics/
│   ├── features/
│   ├── baselines/
│   ├── attribution/
│   ├── detection/
│   ├── alerts/
│   ├── evaluation/
│   ├── storage/
│   └── observability/
├── benchmark/
│   ├── generator.py
│   ├── fault_injection.py
│   └── scenarios/
├── app/
│   └── dashboard.py
├── tests/
│   ├── unit/
│   ├── property/
│   ├── integration/
│   ├── scenarios/
│   └── fixtures/
├── docs/
│   ├── PRD.md
│   ├── SRS.md
│   ├── FEATURE_CATALOG.md
│   ├── ARCHITECTURE.md
│   ├── DATA_PROVENANCE.md
│   ├── EVALUATION.md
│   ├── RUNBOOK.md
│   ├── LIMITATIONS.md
│   └── DOD.md
└── artifacts/
    ├── evaluation/
    ├── alerts/
    └── screenshots/
```

## 12. Required Developer Commands

```bash
uv sync --locked
make lint
make typecheck
make test
make demo
make eval
make dashboard
```

Expected behavior:

**`make demo`** creates or loads demo data, validates it, computes sessions/features/baselines, attributes faults and persists alert episodes.

**`make eval`** runs held-out benchmark scenarios and writes real metric outputs, confusion matrices and scenario pass/fail results.

**`make dashboard`** launches the operator interface against persisted artifacts.

Every command must have clear error messages and exit nonzero on failure.

## 13. Production Migration Design

The local modular monolith is the implemented product.

A production architecture may later introduce:

```text
Event broker
  → Stateful session processing
  → Object storage / lakehouse
  → Versioned feature store
  → Model/attribution service
  → Incident service
  → Ops UI / ticketing
  → Human feedback and retraining
```

Production migration requirements include:

- Partitioning by session/asset identity.
- Watermarks and late-event correction.
- Exactly-once logical effects through idempotent writes.
- Schema evolution and compatibility.
- Baseline/model rollout and rollback.
- Alert-rate monitoring and drift detection.
- Tenant isolation and access control.
- Historical replay and incident auditability.
- Human-approved safety workflows.

Do not claim that the take-home monolith is already a deployed, highly available production system.

## 14. System-Level Acceptance

The SRS is satisfied when:

1. Required contracts validate actual generated records.
2. Every P0 pipeline stage runs end to end.
3. Each ownership category has at least one working, tested diagnostic.
4. Attribution demonstrates independent pack/dock evidence.
5. Missing evidence causes explicit abstention.
6. Data corruption is separated from equipment diagnosis.
7. The alert queue contains only schema-valid, actionable incidents.
8. Evaluation is reproducible and leakage-controlled.
9. A reviewer can run and inspect the system without editing source code.
10. Implemented functionality, unimplemented extensions and scientific limitations are accurately documented.
