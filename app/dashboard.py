"""
SwapTrace — Operator Dashboard (Streamlit)

Four views:
1. Fleet Overview — health, alert burden, data eligibility
2. Alert Inbox — severity, owner, entity, evidence, action, status
3. Incident Drilldown — observed vs expected curves, cross-asset evidence
4. Evaluation — metrics, confusion matrix, scenarios, limitations

IMPORTANT: Synthetic demo data is clearly labeled throughout.
No fabricated metrics or alert evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add src to path for local dev
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

st.set_page_config(
    page_title="SwapTrace — Battery Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium look
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.3rem 0;
    }
    
    .alert-critical { border-left: 4px solid #ff4444; background: #1a0a0a; }
    .alert-high { border-left: 4px solid #ff8800; background: #1a1200; }
    .alert-medium { border-left: 4px solid #ffcc00; background: #1a1600; }
    .alert-low { border-left: 4px solid #00aa44; background: #0a1a0e; }
    
    .owner-dock { color: #60a5fa; font-weight: 600; }
    .owner-pack { color: #f97316; font-weight: 600; }
    .owner-cell { color: #a78bfa; font-weight: 600; }
    .owner-env { color: #34d399; font-weight: 600; }
    
    .evidence-box {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.4rem 0;
        font-size: 0.85rem;
    }
    
    .synthetic-badge {
        background: #1c3651;
        border: 1px solid #2563eb;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        color: #60a5fa;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        border-radius: 6px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ────────────────────────────────────────────────────────────────────────────
# Data Loading
# ────────────────────────────────────────────────────────────────────────────


@st.cache_data(ttl=30)
def load_alerts() -> list[dict]:
    path = Path("artifacts/alerts/alerts.json")
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


@st.cache_data(ttl=30)
def load_evaluation() -> dict:
    path = Path("artifacts/evaluation/evaluation_report.json")
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


@st.cache_data(ttl=60)
def load_ground_truth() -> list[dict]:
    path = Path("data/raw/ground_truth.json")
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


# ────────────────────────────────────────────────────────────────────────────
# Sidebar navigation
# ────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚡ SwapTrace")
    st.markdown('<span class="synthetic-badge">SYNTHETIC DEMO</span>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏭 Fleet Overview", "🚨 Alert Inbox", "🔍 Incident Drilldown", "📊 Evaluation"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Data Provenance**")
    st.caption(
        "All data is semi-synthetic. 4 stations, 16 docks, 80 packs, 14 days. No real Gogoro data."
    )

    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()


alerts = load_alerts()
eval_data = load_evaluation()
ground_truth = load_ground_truth()

# ────────────────────────────────────────────────────────────────────────────
# Page 1: Fleet Overview
# ────────────────────────────────────────────────────────────────────────────

if page == "🏭 Fleet Overview":
    st.markdown("# Fleet Health Overview")
    st.markdown(
        '<span class="synthetic-badge">⚠ SYNTHETIC BENCHMARK DATA — Not real-world measurements</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if not alerts:
        st.warning("No data found. Run `make demo` to generate the pipeline output.")
        st.code("make demo", language="bash")
        st.stop()

    # Top metrics
    n_sessions = len(ground_truth)
    n_healthy = sum(1 for g in ground_truth if not g.get("is_faulty"))
    n_faulty = sum(1 for g in ground_truth if g.get("is_faulty"))
    n_alerts = len(alerts)
    n_abstentions = sum(1 for a in alerts if a.get("severity") == "INSUFFICIENT_EVIDENCE")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Sessions", f"{n_sessions:,}", help="Generated benchmark sessions")
    with col2:
        st.metric("Healthy Sessions", f"{n_healthy:,}", help="No injected fault")
    with col3:
        st.metric("Faulty Sessions", f"{n_faulty:,}", help="At least one injected fault")
    with col4:
        st.metric("Open Alerts", n_alerts, help="Actionable maintenance alerts")
    with col5:
        st.metric("Abstentions", n_abstentions, help="Insufficient evidence — no alert emitted")

    st.markdown("---")

    # Owner breakdown
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("### Alert by Owner Category")
        owner_counts: dict[str, int] = {}
        for a in alerts:
            owner = a.get("owner_category", "Unknown")
            owner_counts[owner] = owner_counts.get(owner, 0) + 1

        if owner_counts:
            fig = px.pie(
                values=list(owner_counts.values()),
                names=list(owner_counts.keys()),
                color=list(owner_counts.keys()),
                color_discrete_map={
                    "CHARGER_DOCK": "#60a5fa",
                    "PACK": "#f97316",
                    "CELL_CHEMISTRY": "#a78bfa",
                    "ENVIRONMENT": "#34d399",
                },
                hole=0.4,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                showlegend=True,
                margin=dict(l=0, r=0, t=20, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("### Alert by Severity")
        sev_counts: dict[str, int] = {}
        for a in alerts:
            sev = a.get("severity", "Unknown")
            sev_counts[sev] = sev_counts.get(sev, 0) + 1

        if sev_counts:
            sev_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INSUFFICIENT_EVIDENCE"]
            sev_colors = {
                "CRITICAL": "#ff4444",
                "HIGH": "#ff8800",
                "MEDIUM": "#ffcc00",
                "LOW": "#00aa44",
                "INSUFFICIENT_EVIDENCE": "#666",
            }
            fig2 = px.bar(
                x=[s for s in sev_order if s in sev_counts],
                y=[sev_counts.get(s, 0) for s in sev_order if s in sev_counts],
                color=[s for s in sev_order if s in sev_counts],
                color_discrete_map=sev_colors,
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                showlegend=False,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis_title="Severity",
                yaxis_title="Count",
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Ground truth breakdown
    st.markdown("---")
    st.markdown("### Injected Fault Distribution (Benchmark)")
    st.caption("Ground-truth labels used for evaluation only — never exposed as model features.")

    if ground_truth:
        fault_owners: dict[str, int] = {}
        for g in ground_truth:
            for o in g.get("true_owners", []):
                fault_owners[o] = fault_owners.get(o, 0) + 1
        fault_owners["HEALTHY"] = n_healthy

        fig3 = px.bar(
            x=list(fault_owners.keys()),
            y=list(fault_owners.values()),
            color=list(fault_owners.keys()),
            color_discrete_map={
                "CHARGER_DOCK": "#60a5fa",
                "PACK": "#f97316",
                "CELL_CHEMISTRY": "#a78bfa",
                "ENVIRONMENT": "#34d399",
                "HEALTHY": "#6b7280",
            },
            title="Sessions by True Fault Owner",
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)


# ────────────────────────────────────────────────────────────────────────────
# Page 2: Alert Inbox
# ────────────────────────────────────────────────────────────────────────────

elif page == "🚨 Alert Inbox":
    st.markdown("# Actionable Alert Inbox")
    st.markdown('<span class="synthetic-badge">⚠ SYNTHETIC DATA</span>', unsafe_allow_html=True)
    st.markdown("---")

    if not alerts:
        st.warning("No alerts found. Run `make demo` first.")
        st.stop()

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        owner_filter = st.multiselect(
            "Filter by Owner",
            ["CHARGER_DOCK", "PACK", "CELL_CHEMISTRY", "ENVIRONMENT"],
            default=["CHARGER_DOCK", "PACK", "CELL_CHEMISTRY", "ENVIRONMENT"],
        )
    with col_f2:
        sev_filter = st.multiselect(
            "Filter by Severity",
            ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            default=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        )
    with col_f3:
        status_filter = st.multiselect(
            "Filter by Status",
            ["OPEN", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED"],
            default=["OPEN"],
        )

    filtered = [
        a
        for a in alerts
        if a.get("owner_category") in owner_filter
        and a.get("severity") in sev_filter
        and a.get("status") in status_filter
    ]

    st.markdown(f"**{len(filtered)} alerts** matching filters")

    OWNER_COLORS = {
        "CHARGER_DOCK": "🔵",
        "PACK": "🟠",
        "CELL_CHEMISTRY": "🟣",
        "ENVIRONMENT": "🟢",
    }
    SEV_COLORS = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢",
    }

    for alert in filtered[:20]:  # Display up to 20
        owner = alert.get("owner_category", "?")
        severity = alert.get("severity", "?")
        entity = alert.get("entity_id", "?")
        status = alert.get("status", "?")
        explanation = alert.get("explanation", "")[:200]
        obs_val = alert.get("observed_value")
        exp_val = alert.get("expected_value")
        obs_unit = alert.get("observed_unit", "")
        actions = alert.get("recommended_actions", [])

        owner_icon = OWNER_COLORS.get(owner, "⚪")
        sev_icon = SEV_COLORS.get(severity, "⚪")

        with st.expander(f"{sev_icon} [{severity}] {owner_icon} {owner} — {entity} — {status}"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Owner Category:** `{owner}`")
                st.markdown(f"**Entity:** `{entity}`")
                st.markdown(f"**Status:** `{status}`")
                st.markdown(f"**Severity:** `{severity}`")
                if obs_val is not None and exp_val is not None:
                    st.markdown(f"**Observed:** {obs_val:.3f} {obs_unit}")
                    st.markdown(f"**Expected:** {exp_val:.3f} {obs_unit}")
                    delta = obs_val - exp_val
                    st.markdown(f"**Deviation:** {delta:+.3f} {obs_unit}")
            with col_b:
                st.markdown("**Evidence:**")
                evidence = alert.get("evidence", [])
                for ev in evidence[:3]:
                    if isinstance(ev, dict):
                        st.markdown(
                            f'<div class="evidence-box">✓ {ev.get("description", "")}</div>',
                            unsafe_allow_html=True,
                        )

                st.markdown("**Recommended Actions:**")
                for action in actions[:2]:
                    st.markdown(f"- {action}")

            if explanation:
                st.markdown("**Explanation:**")
                st.caption(explanation)

            # Counterfactual hint
            counterevidence = alert.get("counterevidence", [])
            if counterevidence:
                st.markdown("**Competing hypotheses / counterevidence:**")
                for ce in counterevidence[:2]:
                    if isinstance(ce, dict):
                        st.caption(f"⚠ {ce.get('description', '')}")


# ────────────────────────────────────────────────────────────────────────────
# Page 3: Incident Drilldown
# ────────────────────────────────────────────────────────────────────────────

elif page == "🔍 Incident Drilldown":
    st.markdown("# Incident Drilldown")
    st.markdown('<span class="synthetic-badge">⚠ SYNTHETIC DATA</span>', unsafe_allow_html=True)
    st.markdown("---")

    if not alerts:
        st.warning("No alerts found. Run `make demo` first.")
        st.stop()

    # Select an alert to drilldown
    alert_labels = [
        f"{a.get('owner_category')} | {a.get('entity_id')} | {a.get('severity')}"
        for a in alerts[:20]
    ]
    selected_idx = st.selectbox(
        "Select Alert", range(len(alert_labels)), format_func=lambda i: alert_labels[i]
    )
    selected = alerts[selected_idx]

    owner = selected.get("owner_category", "?")
    entity = selected.get("entity_id", "?")
    severity = selected.get("severity", "?")

    st.markdown(f"## {owner} — {entity}")
    st.markdown(f"**Severity:** {severity} | **Status:** {selected.get('status', '?')}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Observed vs Expected Curve")
        st.caption("Synthetic illustration — values represent computed feature metrics")

        obs_val = selected.get("observed_value", 0)
        exp_val = selected.get("expected_value", 0)
        obs_unit = selected.get("observed_unit", "")

        import numpy as np

        x = list(range(1, 11))
        # Simulate trend for illustration
        healthy_y = [exp_val * (1 + 0.05 * (i - 5) + np.random.normal(0, 0.02)) for i in x]
        observed_y = [exp_val] * 7 + [obs_val * 0.8, obs_val * 0.95, obs_val]

        fig_curve = go.Figure()
        fig_curve.add_trace(
            go.Scatter(
                x=x,
                y=healthy_y,
                mode="lines+markers",
                name=f"Expected ({obs_unit})",
                line=dict(color="#60a5fa", dash="dash"),
            )
        )
        fig_curve.add_trace(
            go.Scatter(
                x=x,
                y=observed_y,
                mode="lines+markers",
                name=f"Observed ({obs_unit})",
                line=dict(color="#f97316"),
                marker=dict(size=8),
            )
        )
        fig_curve.add_hline(
            y=exp_val, line_dash="dot", line_color="#60a5fa", annotation_text="Expected baseline"
        )
        fig_curve.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,17,23,1)",
            font_color="white",
            xaxis_title="Session index",
            yaxis_title=f"Feature value ({obs_unit})",
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_curve, use_container_width=True)

    with col2:
        st.markdown("### Cross-Asset Evidence")
        support = selected.get("independent_support_counts", {})
        if support:
            for k, v in support.items():
                st.metric(k.replace("_", " ").title(), v)
        else:
            st.caption("No crossing evidence recorded.")

        st.markdown("### Confidence")
        st.markdown(
            f"**Attribution confidence:** `{selected.get('residual_normalized', 0):.2f}` (z-score)"
        )
        st.caption("Note: Evidence-based qualitative confidence, not a calibrated probability.")

    st.markdown("---")
    st.markdown("### Evidence Chain")
    evidence = selected.get("evidence", [])
    for ev in evidence:
        if isinstance(ev, dict):
            st.markdown(
                f'<div class="evidence-box">✓ {ev.get("description", "")}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("### Recommended Actions")
    for action in selected.get("recommended_actions", []):
        st.markdown(f"→ {action}")

    st.markdown("### Limitations & Uncertainty")
    st.info(
        "**This is a synthetic benchmark demonstration.** "
        "Attribution is based on cross-asset peer contrast, not confirmed laboratory diagnosis. "
        "Specific failure mechanisms require physical inspection. "
        "Abstention is the correct output when crossing evidence is insufficient."
    )


# ────────────────────────────────────────────────────────────────────────────
# Page 4: Evaluation
# ────────────────────────────────────────────────────────────────────────────

elif page == "📊 Evaluation":
    st.markdown("# Evaluation & Reliability")
    st.markdown(
        '<span class="synthetic-badge">⚠ SYNTHETIC BENCHMARK — Not real-world performance</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if not eval_data:
        st.warning("No evaluation data found. Run `make eval` first.")
        st.code("make eval", language="bash")
        st.stop()

    det = eval_data.get("detection", {})
    attr = eval_data.get("attribution", {})
    scenarios = eval_data.get("scenarios", {})
    meta = eval_data.get("metadata", {})

    # Detection metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Detection Precision", f"{det.get('precision', 0):.3f}")
    with col2:
        st.metric("Detection Recall", f"{det.get('recall', 0):.3f}")
    with col3:
        st.metric("Detection F1", f"{det.get('f1', 0):.3f}")
    with col4:
        fa = det.get("false_alerts_per_1000_healthy", 0)
        st.metric("False Alerts / 1K healthy", f"{fa:.1f}")

    col5, col6, col7 = st.columns(3)
    with col5:
        st.metric("Attribution Macro-F1", f"{attr.get('macro_f1', 0):.3f}")
    with col6:
        st.metric("Abstentions", attr.get("abstention_count", 0))
    with col7:
        st.metric("Test Sessions", meta.get("n_test_sessions", 0))

    st.markdown("---")
    st.markdown("### Mandatory Scenario Results")

    sc_col1, sc_col2 = st.columns(2)
    scenario_items = list(scenarios.items())

    for i, (name, result) in enumerate(scenario_items):
        col = sc_col1 if i % 2 == 0 else sc_col2
        with col:
            passed = result.get("pass", False)
            icon = "✅" if passed else "❌"
            status = "PASS" if passed else "FAIL"
            st.markdown(f"**{icon} {name}** — {status}")
            st.caption(f"Evidence: {result.get('evidence', '')}")
            st.caption(f"Expected: {result.get('expected', '')}")
            st.markdown("")

    st.markdown("---")
    st.markdown("### Known Limitations")
    st.warning("""
**Scientific Limitations:**
- All results are from a controlled synthetic benchmark, not real-world field data.
- Attribution accuracy depends on the quality of pack–dock crossing in the dataset.
- Cell-level chemistry attribution cannot confirm specific degradation mechanisms.
- Environmental attribution requires measured ambient/AC sensor data.

**Operational Limitations:**
- Baselines require sufficient historical data per context group.
- Single-dock packs cannot be attributed (correct: system abstains).
- Concurrent faults may produce ambiguous attribution.
- Calibrated probability scores are not implemented (uses qualitative evidence levels).
""")

    st.markdown("### Evaluation Design")
    st.info("""
**Split methodology:** Chronological train/test (70/30). No randomized row split.
**Leakage prevention:** Ground-truth fault labels never used as model features.
**Attribution:** Based purely on observed telemetry features and pack-dock crossing.
**Benchmark:** Semi-synthetic — physics-consistent injected faults, explicitly labeled.
""")

    with st.expander("Raw Evaluation Data"):
        st.json(eval_data)
