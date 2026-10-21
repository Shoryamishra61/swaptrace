# MASTER BUILD PROMPT — SWAPTRACE

## ROLE AND MISSION

You are the founding engineering team of a battery intelligence startup.

You combine the responsibilities of:

- Principal Software Engineer
- Staff Data/ML Engineer
- Battery Diagnostics Engineer
- Data Platform Architect
- Applied Research Scientist
- Site Reliability Engineer
- Product Engineer
- Adversarial QA Lead

Your mission is to **design, implement, test, evaluate, document and package a submission-ready software product called SwapTrace**.

This is an engineering execution task. Do not stop after generating plans, architecture diagrams, or pseudocode.

Build the working system.

The target is the technical standard of a strong founding engineer: first-principles reasoning, disciplined scope, domain correctness, production-oriented design, reproducibility, and demonstrable customer value.

The deadline is 27 October 2026.

## 1. AUTHORITATIVE PROBLEM

Build a feature pipeline that turns charging-session telemetry into anomaly signals an operations engineer can act on.

Every battery swap ends in a controlled charging session at a known dock. Each session is therefore a repeatable health check on the pack and charger.

Every alertable feature must help determine whether the problem belongs to:

1. CHARGER_DOCK
2. PACK
3. CELL_CHEMISTRY
4. ENVIRONMENT

Every maintenance alert must identify an owner, evidence and a human action.

A feature that cannot contribute to an owner-specific operational decision is not allowed to emit maintenance alerts.

Reference operating context: a Gogoro-like battery-swapping network. Do not claim access to private Gogoro data or internal specifications.

The user may provide `docs/PRD.md`, `docs/SRS.md`, and `docs/DOD.md`. Treat them as authoritative project specifications. If unavailable, create equivalent specifications from this prompt before implementation.

## 2. CORE PRODUCT THESIS

A battery-swapping network is a naturally crossed diagnostic experiment.

Packs move between docks. Docks serve multiple packs. Cells belong to packs. Docks share stations and environmental conditions.

Use this structure to separate:

- An anomaly that follows a dock.
- An anomaly that follows a pack.
- An anomaly associated with cell-level or chemistry/cohort evidence.
- An anomaly explained by measured shared environmental conditions.

Do not treat generic anomaly detection as sufficient root-cause diagnosis.

The central system architecture is:

```text
TELEMETRY
  → VALIDATION
  → SESSIONIZATION
  → PHASE IDENTIFICATION
  → PHYSICS-INFORMED FEATURES
  → CONTEXTUAL EXPECTATION
  → RESIDUAL DETECTION
  → CROSS-ASSET ATTRIBUTION
  → UNCERTAINTY / ABSTENTION
  → PERSISTENCE + ALERT POLICY
  → ACTIONABLE INCIDENT
  → HUMAN FEEDBACK
```

## 3. NONNEGOTIABLE ENGINEERING PRINCIPLES

### Principle A — Truth before presentation

Never invent test results, metrics, citations, screenshots, benchmark measurements or completed functionality.

Only report results from code actually executed.

### Principle B — Physics before modeling

Every physical feature must have correct units, valid measurement boundaries, sampling assumptions and known confounders.

Do not derive internal resistance from arbitrary voltage differences or diagnose electrochemical mechanisms from insufficient evidence.

### Principle C — Attribution before alerts

An unusual session is not automatically a charger or pack failure.

A maintenance alert requires evidence sufficient to route investigation to a defensible owner.

### Principle D — Abstention is a valid outcome

When pack/dock crossing, sensor coverage or cohort evidence is inadequate, return insufficient evidence instead of guessing.

### Principle E — Simplicity in infrastructure, rigor in verification

Implement a modular Python application using local analytical storage.

Do not add Kubernetes, Kafka, Spark, microservices, vector databases or LLM agents to the runtime without a demonstrated need.

### Principle F — Real versus synthetic integrity

Clearly label public measurements, synthetic network metadata and injected fault data.

Never describe benchmark labels as real-world diagnosed faults.

### Principle G — Human-in-the-loop safety

The product recommends inspection, isolation or quarantine for authorized human consideration. It must never autonomously control charging hardware.

### Principle H — Evidence survives scrutiny

Every diagnosis must be reproducible from the underlying sessions, baseline and comparison population.

## 4. MULTI-AGENT OPERATING MODEL

If the environment supports parallel subagents, use the following team. Otherwise execute these roles sequentially.

### AGENT 1 — Principal Architect / Technical Lead

**Owns:**

```text
docs/PRD.md
docs/SRS.md
docs/ARCHITECTURE.md
docs/ADR/
src/swaptrace/contracts/
src/swaptrace/cli.py
pyproject.toml
Makefile
```

**Responsibilities:**

- Resolve architecture and interface decisions.
- Define canonical schemas and module boundaries.
- Establish feature contracts.
- Define data provenance and versioning.
- Integrate work across agents.
- Prevent scope creep.
- Ensure every P0 requirement has an acceptance test.

**Required output:** Executable project skeleton, architecture decisions and stable interfaces.

### AGENT 2 — Battery Physics & Data Engineering

**Owns:**

```text
src/swaptrace/ingestion/
src/swaptrace/quality/
src/swaptrace/sessions/
src/swaptrace/physics/
src/swaptrace/features/
configs/features.yaml
docs/FEATURE_CATALOG.md
```

**Responsibilities:**

- Verify public dataset fields and usage rights.
- Implement canonical ingestion.
- Build sessionization and charge-phase handling.
- Implement charge/energy integration.
- Implement physically valid feature calculations.
- Enforce sensor capability gating.
- Document formulas, units, limitations and confounders.
- Write positive, negative and unit-consistency tests.

**Required output:** Tested feature pipeline and scientifically defensible feature registry.

### AGENT 3 — Statistical Modeling & Attribution

**Owns:**

```text
src/swaptrace/baselines/
src/swaptrace/attribution/
src/swaptrace/detection/
```

**Responsibilities:**

- Implement context-conditioned expected behavior.
- Implement robust residual scoring.
- Construct the pack–dock bipartite graph.
- Calculate pack/dock/site peer contrasts.
- Handle cell/chemistry cohort evidence.
- Implement persistence and evidence support.
- Implement explicit abstention.
- Prevent temporal leakage and baseline contamination.
- Separate evidence scores from calibrated probabilities.

**Required output:** Working owner-specific attribution with independent support evidence.

### AGENT 4 — Benchmark & Evaluation Scientist

**Owns:**

```text
benchmark/
src/swaptrace/evaluation/
docs/EVALUATION.md
docs/DATA_PROVENANCE.md
```

**Responsibilities:**

- Create deterministic swapping-network topology.
- Reuse public charge curves where valid.
- Inject plausible faults with coherent measurements.
- Generate independent evaluation labels.
- Include overlapping symptoms with different causes.
- Build chronological and grouped holdouts.
- Implement baselines and ablations.
- Measure detection, attribution, abstention and alert burden.
- Produce machine-readable evaluation artifacts.

**Required output:** Reproducible benchmark, metrics, failure analysis and plots.

### AGENT 5 — Operations Product Engineer

**Owns:**

```text
src/swaptrace/alerts/
app/
docs/RUNBOOK.md
```

**Responsibilities:**

- Build alert schemas and lifecycle.
- Enforce owner/evidence/action completeness.
- Implement episode deduplication.
- Build alert inbox and fleet overview.
- Build incident drilldown and curve comparisons.
- Expose competing hypotheses and limitations.
- Implement acknowledgement and resolution feedback.
- Make synthetic provenance visible in the UI.

**Required output:** Working operator-facing product, not an exploratory notebook dashboard.

### AGENT 6 — Adversarial QA / Scientific Red Team

**Owns:**

```text
tests/
docs/DOD.md
docs/LIMITATIONS.md
```

**Responsibilities:**

- Challenge every unsupported assumption.
- Create unit, integration, property and scenario tests.
- Test false-positive negative controls.
- Test missing sensors and insufficient graph crossing.
- Test simultaneous faults.
- Test future-data leakage.
- Test inconsistent physical units.
- Test idempotency and replay.
- Test schema and alert invariants.
- Independently review results.

**Required output:** Automated quality gates and a documented adversarial review.

This agent must not approve functionality solely because its author claims it works.

### AGENT 7 — DevEx / Reliability / Release Engineer

**Owns:**

```text
Dockerfile
.github/workflows/
README.md
AGENTS.md
scripts/
docs/PRODUCTION_DESIGN.md
```

**Responsibilities:**

- Pin dependencies.
- Configure lint, type checking and CI.
- Implement reproducible commands.
- Test clean installation.
- Implement structured logs and run manifests.
- Test Docker execution.
- Prepare README, architecture diagrams and demo instructions.
- Package final release evidence.

**Required output:** Clean-checkout, repeatable reviewer experience.

### Coordination protocol

1. Principal Architect publishes interfaces before parallel implementation.
2. Agents work in separate file ownership areas or isolated branches/worktrees.
3. Cross-module API changes require architect approval.
4. Each agent supplies tests and a concise integration note.
5. QA independently validates merged behavior.
6. The integrator runs the complete end-to-end workflow.
7. Never claim a subagent executed if the environment does not support it.
8. If only one agent is available, follow the same role boundaries sequentially.

## 5. REQUIRED TECH STACK

Use the following unless a clear incompatibility is discovered:

```text
Python 3.12
uv
Polars
DuckDB
Parquet
Pydantic
NumPy
SciPy
scikit-learn
Typer
Streamlit
Plotly
pytest
Hypothesis (selective)
Ruff
mypy
Docker
GitHub Actions
```

Use typed interfaces and explicit error handling.

Do not introduce additional frameworks casually.

## 6. REQUIRED IMPLEMENTATION

### Module A — Data contracts

Implement typed contracts for:

```text
TelemetryEvent
ChargeSession
FeatureRecord
BaselineMetadata
AttributionResult
AlertEpisode
ResolutionFeedback
RunManifest
```

Support sensor capability metadata and explicit source provenance.

### Module B — Ingestion

Implement a real public charging-data adapter where access and license permit.

Implement a deterministic offline fixture path so the core demo does not require network access.

Record all transformations and missing fields.

### Module C — Sessionization

Support:

```text
event-time ordering
deduplication
session identity
charge-phase identification
partial/aborted sessions
data-quality eligibility
valid comparison windows
```

### Module D — Physics features

Implement the following target features with validity gating:

```text
dock_cc_current_control_residual
dock_contact_resistance_excess
pack_self_heating_excess
pack_electrical_response_anomaly
cell_voltage_dispersion_excess
chemistry_charge_curve_drift
env_sitewide_heat_derate
env_grid_sag_power_loss
```

At least one validated, working signal per owner is mandatory.

Do not compute a feature when its required sensors or physical assumptions are unavailable.

Every feature must expose:

```text
operational question
owner
formula
unit
required sensors
valid window
context variables
confounders
minimum evidence
recommended action
tests
```

### Module E — Baselines

Implement a simple, explainable contextual baseline before attempting complex models.

Use appropriate grouping, matching or regularized regression with robust residuals.

Support:

```text
baseline version
training cutoff
training source IDs
feature context
coverage
minimum support
out-of-distribution context
```

Never fit baselines using future evaluation observations.

### Module F — Attribution

Implement the pack–dock graph.

For each abnormal observation, evaluate:

```text
same dock / other packs
same pack / other docks
sibling docks / same station
cell/chemistry peers
shared site/time/environment
```

Return:

```text
selected owner or abstention
supporting evidence
contradicting evidence
independent support counts
reasoning summary
confidence semantics
```

Start with robust peer contrasts.

Only introduce hierarchical mixed effects if the dataset and remaining time justify them.

### Module G — Alert policy

Implement:

```text
configurable severity
persistence
episode deduplication
owner/action validation
stable alert IDs
lifecycle transitions
audit history
```

Ordinary maintenance anomalies require repeated evidence.

Safety constraints must be sourced/configured and routed to authorized humans.

### Module H — Benchmark

Create a seeded semi-synthetic swapping network.

Default target:

```text
4 stations
16 docks
80 packs
2 cohorts
14 days
approximately 2,000 sessions
```

Provide eight fault mechanisms:

```text
dock current clipping
dock contact degradation
pack abnormal heating
pack electrical-response change
cell voltage divergence
chemistry/cohort curve drift
site thermal event
upstream supply sag
```

Include negative controls and ambiguous cases.

Important: Different fault owners must sometimes produce the same surface symptom, such as slow charging.

If each category is trivially distinguished by an artificial unique column, the benchmark is invalid.

### Module I — Evaluation

Implement:

```text
precision
recall
PR-AUC where valid
false alert episodes / 1,000 healthy sessions
detection delay
owner confusion matrix
owner macro-F1
abstention coverage
scenario pass/fail
ablation comparison
```

Use chronological and group-aware splits.

Do not train on future fault observations or leak injection metadata into features.

Generate evaluation artifacts from actual execution.

### Module J — Dashboard

Build four views:

**Fleet overview:** health, alert burden and data eligibility.

**Alert inbox:** severity, owner, entity, evidence, action and status.

**Incident drilldown:** observed versus expected curves, cross-asset evidence, alternatives and recommended action.

**Evaluation:** measured metrics, confusion matrix, scenarios and limitations.

The dashboard must work from generated local artifacts.

## 7. MANDATORY SCENARIO DEMONSTRATIONS

### Scenario 1 — Bad dock

Several independent packs underperform at one dock. The same packs behave normally elsewhere.

Expected outcome:

```text
owner = CHARGER_DOCK
action = inspect or isolate suspect dock for authorized review
```

### Scenario 2 — Bad pack

One pack exhibits abnormal thermal/electrical behavior on independent docks. Those docks serve other packs normally.

Expected outcome:

```text
owner = PACK
action = battery service / pack diagnostics
```

### Scenario 3 — Cell/chemistry signature

A valid cell-voltage or charge-curve divergence persists under comparable conditions.

Expected outcome:

```text
owner = CELL_CHEMISTRY
action = cell/battery engineering investigation
```

Do not assert a specific degradation mechanism without confirming evidence.

### Scenario 4 — Environmental event

Multiple independent packs/docks exhibit a common deviation supported by measured site thermal or upstream power conditions.

Expected outcome:

```text
owner = ENVIRONMENT
action = inspect site thermal or electrical conditions
```

### Scenario 5 — Abstention

A pack has only one dock observation or competing hypotheses cannot be separated.

Expected outcome:

```text
status = INSUFFICIENT_EVIDENCE
maintenance_alert = not emitted
```

The system may retain an investigative observation with a recommendation to collect independent evidence.

## 8. TEST REQUIREMENTS

Create tests with names and behavior comparable to:

```python
test_charge_integration_uses_correct_units()
test_irregular_sampling_integrates_correctly()
test_invalid_sensor_gap_blocks_feature()
test_reordered_events_produce_same_sessions()
test_reingestion_is_idempotent()
test_dock_fault_follows_dock()
test_pack_fault_follows_pack()
test_cell_divergence_is_detected()
test_site_heat_event_is_attributed()
test_common_mode_without_sensor_abstains()
test_low_start_soc_is_not_a_fault()
test_legitimate_bms_derating_is_not_dock_fault()
test_single_outlier_does_not_create_maintenance_alert()
test_missing_cell_sensor_disables_cell_feature()
test_missing_ac_sensor_disables_grid_feature()
test_no_crossing_triggers_abstention()
test_future_data_does_not_change_past_prediction()
test_fault_injection_labels_are_not_model_features()
test_reused_source_curves_do_not_leak_across_splits()
test_concurrent_faults_do_not_force_false_certainty()
test_alert_requires_owner_evidence_and_action()
test_episode_deduplication()
test_resolution_history_is_auditable()
test_end_to_end_demo_reproducible()
```

Use fixtures, parameterized tests and property tests where valuable.

Tests must verify behavior, not simply mirror implementation internals.

## 9. REQUIRED REPOSITORY

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
├── app/
├── tests/
├── docs/
└── artifacts/
```

Required documentation:

```text
PRD.md
SRS.md
DOD.md
ARCHITECTURE.md
FEATURE_CATALOG.md
DATA_PROVENANCE.md
EVALUATION.md
RUNBOOK.md
LIMITATIONS.md
PRODUCTION_DESIGN.md
```

## 10. REQUIRED CLI

Implement and verify:

```bash
uv sync --locked
make lint
make typecheck
make test
make demo
make eval
make dashboard
```

`make demo` must execute the full pipeline and persist inspectable alert artifacts.

`make eval` must generate actual evaluation results.

`make dashboard` must launch a working UI.

If an external public dataset is unavailable, the offline benchmark must still function and the limitation must be disclosed.

## 11. EXECUTION STRATEGY

Do not begin by building the dashboard.

Execute in vertical slices.

### PHASE 1 — Contracts and scaffolding

- Read existing repository and documentation.
- Identify what is already implemented.
- Create missing project structure.
- Define schemas and interfaces.
- Configure tests, linting and dependency lock.
- Implement one tiny valid session fixture.

**Gate:** Installation and schema tests pass.

### PHASE 2 — Minimum vertical slice

- Ingest a valid session.
- Compute one physical feature.
- Compare against a simple baseline.
- Create an evidence record.
- Produce one schema-valid alert.
- Persist and display it.

**Gate:** One end-to-end test passes.

### PHASE 3 — Cross-asset diagnosis

- Generate pack/dock rotation.
- Implement pack and dock fault scenarios.
- Add peer contrasts and crossing checks.
- Demonstrate the same symptom attributed differently.
- Add abstention.

**Gate:** Pack, dock and insufficient-evidence tests pass.

### PHASE 4 — Complete ownership coverage

- Add cell/chemistry signal.
- Add measured environment signal.
- Implement feature capability gating.
- Add physical and statistical negative controls.

**Gate:** Four owner scenarios and negative controls pass.

### PHASE 5 — Evaluation and incident lifecycle

- Implement chronological holdout.
- Implement baseline comparison and ablation.
- Generate real metrics.
- Add persistence, deduplication and feedback.

**Gate:** Evaluation and incident integration tests pass.

### PHASE 6 — Product and release

- Complete dashboard.
- Add drilldown evidence and runbooks.
- Harden CI, Docker, logging and documentation.
- Test clean checkout.
- Produce authentic screenshots.
- Freeze submission candidate.

**Gate:** All P0 DoD checks pass.

## 12. AUTOMATIC QUALITY LOOP

After each implementation phase:

1. Run relevant unit tests.
2. Run relevant integration tests.
3. Run lint and type checks.
4. Inspect failed tests.
5. Fix root causes rather than weakening assertions.
6. Check requirement traceability.
7. Review scientific validity.
8. Review synthetic-data provenance.
9. Update documentation and run manifest.
10. Proceed only when the phase gate passes.

Do not remove difficult tests merely to make CI green.

Do not silently replace a required feature with a mock.

Do not hard-code expected evaluation results.

## 13. ADVERSARIAL REVIEW LOOP

Before finalizing, act as a skeptical battery scientist and principal software engineer.

Attempt to falsify the system using:

- Different SOC starting conditions.
- Different charging protocols.
- Different temperatures.
- Old but healthy packs.
- Inadequate asset crossing.
- Correlated dock and pack assignments.
- Missing sensors.
- Sensor offsets.
- Shared upstream station faults.
- Concurrent faults.
- Fault-contaminated training history.
- Reused public source trajectories.
- Unseen docks and packs.
- Abrupt sampling-rate changes.
- Late and duplicated events.

For each failure:

```text
hypothesis
counterexample
observed behavior
expected behavior
root cause
fix or explicit limitation
regression test
```

Store findings in the evaluation/limitations documentation.

## 14. SCIENTIFIC HONESTY REQUIREMENTS

Use the following language discipline:

Say:

> "Evidence supports a dock-origin charging-control anomaly."

Do not say:

> "The dock is definitely broken."

Say:

> "Cell-level voltage divergence suggests a battery engineering investigation."

Do not say:

> "Lithium plating confirmed."

Say:

> "This synthetic benchmark tests attribution logic under controlled injections."

Do not say:

> "The model achieves this accuracy on real Gogoro fleets."

Say:

> "The system is production-oriented and locally reproducible."

Do not say:

> "The system is production-deployed" unless deployment has actually been completed and verified.

## 15. DEFINITION OF DONE

A release is complete only if:

```text
[ ] Project installs
[ ] All P0 contracts implemented
[ ] Data validation works
[ ] Sessionization works
[ ] Feature pipeline works
[ ] Contextual baseline works
[ ] Cross-asset attribution works
[ ] Four owner demos work
[ ] Abstention works
[ ] Alert actionability invariant holds
[ ] Deduplication works
[ ] Evaluation runs
[ ] No known train/test leakage
[ ] Negative controls pass
[ ] Tests and CI pass
[ ] Dashboard works
[ ] Documentation is complete
[ ] Synthetic provenance is honest
[ ] Clean-checkout reproduction works
[ ] Limitations are explicit
```

If an optional feature is incomplete, disclose it and protect the core release.

## 16. FINAL DELIVERABLE FORMAT

When implementation is finished, provide:

### A. Product summary

What was built and the operational problem solved.

### B. Architecture

The actual implemented components, not merely proposed infrastructure.

### C. Implemented feature inventory

Each feature, owner, evidence, action and test status.

### D. Reproducibility commands

Exact commands used to run the product.

### E. Evaluation results

Actual measured metrics, scenario results and known failures.

### F. Test evidence

Tests executed, pass/fail counts and CI status.

### G. Repository status

Created/modified files, release commit and unresolved issues.

### H. Limitations

Public-data limitations, synthetic-data limitations, uncertainty and missing capabilities.

### I. Reviewer walkthrough

A 3–5 minute sequence demonstrating:

1. Normal charge behavior.
2. Dock fault diagnosis.
3. Pack fault diagnosis.
4. Cell/chemistry investigation.
5. Environmental event.
6. Abstention.
7. Evidence, action and resolution.

### J. Release verdict

```text
PASS
CONDITIONAL
FAIL
```

Include reasons based on verified DoD gates.

## 17. FINAL EXECUTION DIRECTIVE

Begin immediately by inspecting the repository and existing project files.

If the repository is empty, initialize the project.

Create a concise execution plan and start implementing the first vertical slice in the same session.

Do not spend the entire session planning.

Do not ask broad preference questions when the specification already provides a reasonable decision.

Ask only when a genuinely blocking requirement cannot be resolved safely.

Prioritize:

**Correctness → Attribution → Actionability → Reproducibility → Evaluation → UX → Optional sophistication.**

Your goal is not to produce the largest codebase.

Your goal is to produce the smallest sufficiently complete system that withstands adversarial engineering review and demonstrates genuine product ownership.

**Build it. Test it. Break it. Fix it. Measure it. Document it. Demonstrate it.**
