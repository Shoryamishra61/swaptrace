# SwapTrace

**Battery Charging-Session Telemetry Anomaly Detection & Cross-Asset Fault Attribution**

[![CI Quality Gates](https://github.com/Shoryamishra61/swaptrace/actions/workflows/ci.yml/badge.svg)](https://github.com/Shoryamishra61/swaptrace/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![Vercel Deployment](https://img.shields.io/badge/Vercel-Live_Console-black?logo=vercel)](https://swaptrace.vercel.app)

> **Submission for Coulomb AI · Founding Engineer Challenge**  
> Reference Client Context: [Gogoro Network](https://www.gogoro.com/gogoro-network/) — Two-Wheeler Battery Swapping Operator

---

## 1. Executive Summary & Authoritative Problem

SwapTrace is a production-oriented diagnostic feature pipeline and decision-support system that converts battery charging-session telemetry into **actionable, owner-specific maintenance signals** for fleet operations engineers.

In an electric two-wheeler swapping network (such as the Gogoro Network), every battery swap ends in a **controlled charging session at a known station dock**. Each charging session represents a repeatable, instrumented health check on both the battery pack and the charging infrastructure.

### The Central Diagnostic Problem

When a charging session exhibits a symptom—such as a current deficit, slow charging, or elevated temperature—generic anomaly detection is worse than useless: **it flags that something is weird without identifying who must act.**

A current delivery deficit can be caused by:
1. A degraded dock PWM controller or burnt terminal pin &rarr; **`CHARGER_DOCK`** (Field technician dispatches to station)
2. Excessive internal resistance ($R_{int}$) in the pack &rarr; **`PACK`** (Battery warehouse quarantines pack at next swap)
3. Premature cell-voltage cutoff from severe cell imbalance &rarr; **`CELL_CHEMISTRY`** (Cell engineering investigates lot cohort)
4. Extreme ambient temperature triggering legitimate thermal derate &rarr; **`ENVIRONMENT`** (Facilities inspects HVAC ventilation)

```
        ┌─────────────────────────────────────────────────────────────┐
        │                  OBSERVED SYMPTOM                           │
        │       "Charging session delivered only 8.0A vs 15.0A"       │
        └──────────────────────────────┬──────────────────────────────┘
                                       │
                BIPARTITE CROSS-ASSET ATTRIBUTION GRAPH
                                       │
        ┌───────────────┬──────────────┴────────────────┬───────────────┐
        ▼               ▼                               ▼               ▼
  [CHARGER_DOCK]     [PACK]                     [CELL_CHEMISTRY]  [ENVIRONMENT]
  Follows dock    Follows battery              Cell dispersion     All assets at
  across 4 packs  across 3 docks                ΔV_cell > 100mV    station derated
```

### The Invariant Contract: Attribution Before Alerts
> **"A feature that cannot contribute to an owner-specific operational decision is not allowed to emit maintenance alerts."**

Every emitted alert in SwapTrace is guaranteed to contain:
- **Exact Owner Category:** `CHARGER_DOCK`, `PACK`, `CELL_CHEMISTRY`, or `ENVIRONMENT`.
- **Responsible Team:** Infrastructure Tech, Battery Service, Cell Engineering, or Facilities.
- **Physical Evidence:** Measured residuals, baseline comparisons, unit-correct formulas.
- **Counterfactual Cross-Asset Proof:** Peer behavior across independent swapping sessions.
- **Mandatory Human Next Action:** Exact physical inspection steps.
- **First-Class Abstention:** If asset crossing is insufficient (e.g. pack only seen on 1 dock), SwapTrace **abstains** (`INSUFFICIENT_EVIDENCE`) rather than making an unverified dispatch.

---

## 2. Core Product Thesis: The Naturally Crossed Experiment

A battery-swapping network forms a **naturally crossed diagnostic bipartite graph** $G = (D, P, E)$, where docks $D$ and battery packs $P$ are vertices connected by charging sessions $E$:
* Packs move dynamically across docks and stations throughout their lifecycle.
* Docks charge dozens of independent battery packs each week.
* Docks share station-level environmental conditions and grid transformers.

SwapTrace exploits this topology through **robust peer contrasts**:

$$\text{Dock Effect} = \text{Median}\left(\{r_{d, p} \mid p \in \text{Packs}(d)\}\right) - \text{Median}\left(\{r_{d', p} \mid d' \neq d\}\right)$$

$$\text{Pack Effect} = \text{Median}\left(\{r_{d, p} \mid d \in \text{Docks}(p)\}\right) - \text{Median}\left(\{r_{d, p'} \mid p' \neq p\}\right)$$

```
 CASE A: DOCK FAULT ISOLATION              CASE B: PACK FAULT ISOLATION
 ────────────────────────────              ────────────────────────────
 Docks           Packs                     Docks           Packs
 [DOK-01] ──X──> [PCK-001]                 [DOK-01] ──X──> [PCK-017]
 [DOK-01] ──X──> [PCK-017]                 [DOK-02] ──X──> [PCK-017]
 [DOK-01] ──X──> [PCK-042]                 [DOK-04] ──X──> [PCK-017]
 [DOK-01] ──X──> [PCK-078]                 
                                           (Counterfactuals: DOK-01, 02, 04
 (Counterfactuals: PCK-001, 042 on          charge other packs normally)
  other docks are completely NORMAL)       
                                           ==> ATTRIBUTED TO PACK
 ==> ATTRIBUTED TO CHARGER_DOCK
```

---

## 3. System Architecture & End-to-End Pipeline

```
┌─────────────────┐     ┌──────────────────────┐
│  PUBLIC SOURCE  │     │ SEEDED SWAP BENCHMARK│
│ (Real CC/CV fit)│     │  (1,937 sessions)    │
└────────┬────────┘     └──────────┬───────────┘
         │                         │
         └───────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │     RAW INGESTION         │ TelemetryEvent schema validation
       └─────────────┬─────────────┘ Sensor capability detection
                     ▼
       ┌───────────────────────────┐
       │  QUALITY & QUARANTINE     │ Range bounds, non-monotonic time rejection,
       └─────────────┬─────────────┘ Missing sensor detection
                     ▼
       ┌───────────────────────────┐
       │      SESSIONIZATION       │ Event clustering, CC/CV phase detection,
       └─────────────┬─────────────┘ Trajectory integration (Ah, Wh)
                     ▼
       ┌───────────────────────────┐
       │   PHYSICS-INFORMED        │ 8 target physical features with
       │      FEATURES             │ strict sensor validity gating
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │   CONTEXTUAL BASELINES    │ Grouped robust medians (Protocol × Temp × SOC)
       └─────────────┬─────────────┘ Point-in-time safe (no future leakage)
                     ▼
       ┌───────────────────────────┐
       │   NORMALIZED RESIDUALS    │ Robust z-scoring via MAD
       └─────────────┬─────────────┘ Outlier isolation (z > 3.0σ)
                     ▼
       ┌───────────────────────────┐
       │  BIPARTITE ATTRIBUTION    │ Pack–dock graph peer contrasts,
       │          GRAPH            │ Confounder filtering, safe abstention
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │    ALERT POLICY ENGINE    │ Episode persistence (count ≥ 2),
       └─────────────┬─────────────┘ Deduplication, Actionable tickets
                     ▼
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ STREAMLIT / WEB  │    │ REPRODUCIBLE     │
│   OPS CONSOLE    │    │ EVALUATION SUITE │
└──────────────────┘    └──────────────────┘
```

---

## 4. Physics-Informed Feature Catalog

SwapTrace implements 8 domain-rigorous diagnostic features. No feature is computed when its required physical sensors or assumptions are violated:

| Feature Identifier | Target Owner | Operational Formula | Required Sensors | Confounders / Exclusions |
|:---|:---:|:---|:---|:---|
| `dock_cc_current_control_residual` | `CHARGER_DOCK` | $\Delta I = I_{cmd} - \bar{I}_{charger}$ | `charger_current` | BMS thermal derate, CC taper entry |
| `dock_contact_resistance_excess` | `CHARGER_DOCK` | $R_{contact} = \frac{\bar{V}_{dock} - \bar{V}_{pack}}{\bar{I}_{pack}}$ | `charger_v`, `pack_v`, `charger_i` | Cable voltage drop, low current ($<3\text{A}$) |
| `pack_self_heating_excess` | `PACK` | $\Delta T = T_{final} - T_{expected}(E_{wh}, T_{amb})$ | `pack_temp`, `ambient_temp` | Solar loading, station HVAC airflow |
| `pack_electrical_response_anomaly` | `PACK` | $R_{eff} = \frac{\Delta V_{step}}{\Delta I_{step}}$ | `pack_v`, `pack_i` | Sub-zero pack temperature, low SOC |
| `cell_voltage_dispersion_excess` | `CELL_CHEMISTRY` | $\Delta V_{cell} = \max_i(V_i) - \min_i(V_i)$ | `cell_voltages_v` | Extreme SOC ($>95\%$ or $<5\%$) |
| `chemistry_charge_curve_drift` | `CELL_CHEMISTRY` | $\text{MAD}(V_{session}(\text{SOC}) - V_{ref}(\text{SOC}))$ | `pack_v`, `soc` | Aging cohort bracket mismatch |
| `env_sitewide_heat_derate` | `ENVIRONMENT` | $T_{ambient} > 35^\circ\text{C} \land \ge 3\text{ packs}$ | `ambient_temp`, `pack_temp` | Station PDU breaker trip |
| `env_grid_sag_power_loss` | `ENVIRONMENT` | $V_{ac, nominal} - V_{ac, measured} > 15\text{V}$ | `ac_input_voltage` | In-station transformer saturation |

---

## 5. Measured Evaluation & Scenario Verification

Evaluated strictly on held-out test partitions ($N=582$ test sessions, 5 alert episodes, 47 abstentions) generated from the deterministic benchmark:

### Quantitative Performance Ledger

| Evaluation Metric | Measured Result | Operational Interpretation |
|:---|:---:|:---|
| **Detection Precision** | **95.4%** | 83 of 87 alerted sessions correspond to genuine injected faults |
| **Detection Recall** | **22.6%** | High threshold intentional to prevent technician alert fatigue |
| **False Alert Burden** | **18.6** | Only 18.6 false alert episodes per 1,000 healthy sessions |
| **Safe Abstentions** | **47 Sessions** | Safely withheld from dispatch due to low asset crossing ($<2$) |
| **Attribution Macro-F1**| **0.164** | Conservative multiclass attribution across 4 operational owners |

### Mandatory Scenario Demonstrations

All 5 mandatory scenario verification gates pass with automated integration proofs:

| Scenario | Injected Condition | Attributed Owner | Verified Concrete Evidence | Gate Status |
|:---|:---|:---:|:---|:---:|
| **S01: Bad Dock** | Dock STA-04-DOK-01 clips at 8A | `CHARGER_DOCK` | 2 persistent episodes emitted across 4 independent packs | **PASS &check;** |
| **S02: Bad Pack** | Pack STA-04-PCK-017 runs +14°C hot | `PACK` | Anomaly follows pack across 3 independent docks | **PASS &check;** |
| **S03: Cell Chemistry** | Pack PCK-017 has 142mV cell spread | `CELL_CHEMISTRY` | 3 episodes: cell dispersion + cohort charge curve drift | **PASS &check;** |
| **S04: Environment** | Station STA-04 ambient 38.5°C heat | `ENVIRONMENT` | Station-wide derate affecting 8 packs across 4 docks | **PASS &check;** |
| **S05: Abstention** | Pack PCK-088 seen on only 1 dock | `ABSTAIN` | 47 sessions classified as `INSUFFICIENT_EVIDENCE` | **PASS &check;** |

### Ablation Study (each variant actually re-run and scored)

Every variant below is executed over the same 4,656 feature records and scored against the same
held-out ground truth — no placeholder numbers:

| Variant | Detection F1 | False alerts / 1000 healthy | Attribution Macro-F1 |
|:---|:---:|:---:|:---:|
| **A0** Static global threshold (one fixed cut, z > 5) | 0.790 | 907.0 | 0.0 |
| **A1** Contextual residual (context-bucketed z > 3) | 0.790 | 907.0 | 0.0 |
| **A2** A1 + persistence (entity+feature must repeat) | 0.765 | 786.0 | 0.0 |
| **A3** Full pipeline (persistence + attribution + abstention) | **0.366** | **18.6** | **0.164** |

**Reading:** A3 deliberately trades raw detection F1 for a **48x reduction in false alert
episodes** (18.6 vs 907 per 1,000 healthy sessions) — the pipeline optimizes technician alert
burden, not raw recall, per the problem statement's "actionable signal" requirement. A0 and A1
coincide at session granularity because every session containing a 3–5σ feature also contains a
>5σ feature; the contextual-baseline benefit appears in the score quality, not the session sets.
A0–A2 have attribution F1 = 0.0 by construction: they produce no attribution layer.

---

## 6. Web Operations Console

The repository ships a React + Lucide **Industrial Operations Console** (Apple HIG light-mode design system) that renders the real pipeline artifacts — alerts with evidence and counterevidence, attribution scenario proofs, waveform studio, and a reviewer-defense view. Its data module (`src/data/telemetryData.js`) is regenerated from `artifacts/` by `scripts/export_web_data.py`, so the UI can never silently diverge from pipeline output.

* **Live Deployment:** [swaptrace.vercel.app](https://swaptrace.vercel.app)
* **Local Run:** `npm install && npx vite` (dev) or `npx vite build` (production bundle to `dist/`)
* **Data Refresh:** `uv run python scripts/export_web_data.py` after any pipeline re-run
* **Deployment:** static `dist/` on Vercel free tier (`vercel.json` sets the Vite framework and output directory)

---

## 7. Quickstart & Reviewer CLI Guide

### Requirements
* **Python 3.12+**
* **uv** package manager (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

```bash
# 1. Clone repository
git clone https://github.com/Shoryamishra61/swaptrace.git
cd swaptrace

# 2. Lock & sync dependencies
uv sync --extra dev

# 3. Run full test suite (55 tests: unit + integration + property, passing in ~10s)
uv run pytest

# 4. Run end-to-end demo pipeline
# Generates 1,937 sessions, extracts 12,850 features, fits baselines, emits alerts
uv run python -m swaptrace.cli demo

# 5. Run formal evaluation and scenario validation
uv run python -m swaptrace.cli eval

# 6. Launch Streamlit operations dashboard
uv run streamlit run app/dashboard.py
```

---

## 8. Repository Structure

```
swaptrace/
├── src/swaptrace/                   # Modular Python 3.12 Core Package
│   ├── contracts/                   # Canonical Pydantic schemas (all modules import here)
│   ├── ingestion/                   # Telemetry adapters and synthetic generator
│   ├── quality/                     # Sensor capability gating & range checks
│   ├── sessions/                    # Sessionization, deduplication, CC/CV phase detection
│   ├── physics/                     # Charge/energy integration, physical formulas
│   ├── features/                    # Feature catalog & computation pipeline
│   ├── baselines/                   # Contextual expected-value models (point-in-time safe)
│   ├── attribution/                 # Bipartite pack-dock graph peer contrast engine
│   ├── detection/                   # Residual scoring & anomaly persistence
│   ├── alerts/                      # Alert policy, episode deduplication & actions
│   ├── evaluation/                  # Scenario pass/fail & metric calculations
│   ├── storage/                     # DuckDB + Parquet local persistence layer
│   └── observability/               # Structured logging & run manifests
├── src/App.jsx + src/views/         # React operations console (Vite + Lucide)
│   ├── views/FleetOverviewView.jsx  #   Fleet KPIs & station health
│   ├── views/AttributionEngineView.jsx #   Physics feature catalog & metrics
│   ├── views/ReviewerDefenseView.jsx   #   Adversarial reviewer defense proofs
│   └── data/telemetryData.js        #   Auto-generated from artifacts/ (do not hand-edit)
├── scripts/export_web_data.py       # Regenerates console data from artifacts
├── benchmark/                       # Seeded swapping network topology generator
├── app/                             # Streamlit Python dashboard (alternative local UI)
├── tests/                           # 55 unit, integration & property tests (100% passing)
│   ├── unit/test_physics.py         # Unit tests on physical integration & residuals
│   ├── integration/test_pipeline.py # End-to-end integration & scenario tests
│   └── property/test_properties.py  # Hypothesis invariant tests
├── docs/                            # Formal specifications (PRD, SRS, DOD, Architecture)
├── artifacts/                       # Machine-readable output (alerts.json, attribution_results.json, evaluation_report.json)
├── vercel.json                      # Vercel deployment configuration
├── Makefile                         # Unified developer commands
└── pyproject.toml                   # Project metadata & locked dependencies
```

---

## 9. Scientific Integrity & Disclosures

1. **Synthetic Data Disclosure:** Telemetry events and network topology are generated from a controlled, seeded physical simulation ($N=1,937$ sessions) capturing real battery physics (Ohm's law, Arrhenius thermal dissipation, Butler-Volmer polarization). They do not represent proprietary or confidential data from Gogoro Inc.
2. **Deterministic Reproducibility:** Every scenario, feature calculation, baseline model, and evaluation metric is fully reproducible from fixed seed `42`.
3. **Conservative Safety Principles:** SwapTrace acts exclusively as decision support for authorized human engineers. It never executes autonomous physical power adjustments or equipment shutdowns.

---

## 10. License

Licensed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE) for details.
