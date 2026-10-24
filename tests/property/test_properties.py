"""
Property-based tests (Hypothesis) for the Swaptrace pipeline.

Each test asserts an invariant that must hold for ANY valid input,
not just the hand-picked fixtures used in unit/integration tests.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from swaptrace.attribution import PackDockGraph, attribute_session
from swaptrace.contracts import (
    AttributionResult,
    AttributionStatus,
    FeatureRecord,
    OwnerCategory,
)
from swaptrace.detection import PersistenceTracker, score_anomalies
from swaptrace.physics import compute_dock_cc_current_residual, integrate_charge_ah

# ─────────────────────────────────────────────────────────────────────────────
# Physics invariants
# ─────────────────────────────────────────────────────────────────────────────

positive_reals = st.floats(min_value=0.0, max_value=50.0, allow_nan=False)


@settings(max_examples=200, deadline=None)
@given(
    current=positive_reals,
    duration_s=st.floats(min_value=1.0, max_value=7200.0, allow_nan=False),
    n_points=st.integers(min_value=2, max_value=50),
)
def test_constant_current_integration_is_exact(current: float, duration_s: float, n_points: int):
    """Constant current integrated over any sampling density yields I*t exactly."""
    ts = [i * duration_s / (n_points - 1) for i in range(n_points)]
    currents = [current] * n_points
    assert integrate_charge_ah(currents, ts) == pytest.approx(current * duration_s / 3600.0)


@settings(max_examples=200, deadline=None)
@given(
    currents=st.lists(positive_reals, min_size=2, max_size=40),
    st_scale=st.floats(min_value=1.0, max_value=100.0, allow_nan=False),
)
def test_integration_is_scale_invariant_in_time(currents: list[float], st_scale: float):
    """Stretching the time axis by k stretches the integral by k."""
    n = len(currents)
    ts1 = [i * 1.0 for i in range(n)]
    ts2 = [i * st_scale for i in range(n)]
    q1 = integrate_charge_ah(currents, ts1)
    q2 = integrate_charge_ah(currents, ts2)
    assert q2 == pytest.approx(q1 * st_scale, rel=1e-9, abs=1e-12)


@settings(max_examples=200, deadline=None)
@given(
    commanded=st.floats(min_value=0.1, max_value=100.0, allow_nan=False),
    delivered=st.floats(min_value=0.0, max_value=150.0, allow_nan=False),
)
def test_cc_residual_delivery_ratio_bounded(commanded: float, delivered: float):
    """Delivery ratio is always in [0, max(delivered/commanded, ...)] and deficit consistent."""
    r = compute_dock_cc_current_residual(commanded, delivered)
    assert r["valid"]
    assert r["deficit_a"] == pytest.approx(commanded - delivered)
    assert r["delivery_ratio"] == pytest.approx(delivered / commanded)
    assert not r["bms_limited"]


# ─────────────────────────────────────────────────────────────────────────────
# Detection invariants
#─────────────────────────────────────────────────────────────────────────────

feature_ids = st.sampled_from(
    [
        "dock_cc_current_control_residual",
        "dock_contact_resistance_excess",
        "pack_self_heating_excess",
        "cell_voltage_dispersion_excess",
    ]
)


@settings(max_examples=100, deadline=None)
@given(
    scores=st.lists(
        st.one_of(st.none(), st.floats(min_value=-10.0, max_value=20.0, allow_nan=False)),
        min_size=1,
        max_size=60,
    ),
    feature_id=feature_ids,
)
def test_score_anomalies_never_flags_null_scores(scores: list, feature_id: str):
    """A feature with a null normalized_score is never anomalous, whatever the threshold."""
    records = [
        FeatureRecord(
            feature_id=feature_id,
            session_id=f"S-{i}",
            entity_type="pack",
            entity_id="E-1",
            value=1.0,
            unit="A",
            normalized_score=s,
        )
        for i, s in enumerate(scores)
    ]
    for threshold in (0.0, 3.0, 100.0):
        flagged = [a for a in score_anomalies(records, z_threshold=threshold) if a.is_anomaly]
        assert all(a.feature_record.normalized_score is not None for a in flagged)
        assert all(
            a.feature_record.normalized_score > threshold for a in flagged  # type: ignore[operator]
        )


def test_persistence_tracker_counts_match_records():
    """Persistence count equals exactly the number of recorded observations."""
    tracker = PersistenceTracker(min_occurrences=2)
    base = datetime(2026, 1, 1, tzinfo=UTC)
    for i in range(5):
        tracker.record("E-1", "f1", f"S-{i}", base + timedelta(minutes=i), float(i))
    assert tracker.get_count("E-1", "f1") == 5
    assert tracker.get_sessions("E-1", "f1") == [f"S-{i}" for i in range(5)]
    assert tracker.is_persistent("E-1", "f1")
    tracker.clear("E-1", "f1")
    assert tracker.get_count("E-1", "f1") == 0
    assert not tracker.is_persistent("E-1", "f1")


# ─────────────────────────────────────────────────────────────────────────────
# Attribution invariants
#─────────────────────────────────────────────────────────────────────────────

def _attributed_result(owner: OwnerCategory, session_id: str) -> AttributionResult:
    return AttributionResult(
        session_id=session_id,
        attribution_status=AttributionStatus.ATTRIBUTED,
        selected_owner=owner,
        explanation="test",
    )


def _fr(feature_id: str, session_id: str, entity_type: str, entity_id: str, z: float) -> FeatureRecord:
    return FeatureRecord(
        feature_id=feature_id,
        session_id=session_id,
        entity_type=entity_type,
        entity_id=entity_id,
        value=1.0,
        unit="A",
        normalized_score=z,
    )


@settings(max_examples=50, deadline=None)
@given(n_packs_seen=st.integers(min_value=1, max_value=10))
def test_dock_attribution_requires_min_crossing(n_packs_seen: int):
    """A dock observed by fewer than MIN_INDEPENDENT_PACKS_FOR_DOCK packs can never
    be attributed to CHARGER_DOCK, no matter how strong the feature score is."""
    from swaptrace.attribution import MIN_INDEPENDENT_PACKS_FOR_DOCK

    graph = PackDockGraph()
    pack_id = "PCK-001"
    # The pack visits MIN cross-docks so it never fails the 'normal elsewhere' check
    for d in range(MIN_INDEPENDENT_PACKS_FOR_DOCK):
        graph.add_session(f"PS-{d}", pack_id, f"D-OTHER-{d}", "STA-0")
    for p in range(n_packs_seen):
        graph.add_session(f"OS-{p}", f"PCK-{p:03d}", "D-TARGET", "STA-0")

    result = attribute_session(
        session_id="S-0",
        pack_id=pack_id,
        dock_id="D-TARGET",
        station_id="STA-0",
        anomalous_features=[_fr("dock_contact_resistance_excess", "S-0", "dock", "D-TARGET", 6.0)],
        graph=graph,
    )
    if n_packs_seen < MIN_INDEPENDENT_PACKS_FOR_DOCK:
        assert result.selected_owner is None
        assert result.attribution_status == AttributionStatus.INSUFFICIENT_EVIDENCE
    else:
        assert result.selected_owner == OwnerCategory.CHARGER_DOCK


@settings(max_examples=50, deadline=None)
@given(n_docks_seen=st.integers(min_value=1, max_value=10))
def test_pack_attribution_requires_min_crossing(n_docks_seen: int):
    """A pack observed on fewer than MIN_INDEPENDENT_DOCKS_FOR_PACK docks can never
    be attributed to PACK."""
    from swaptrace.attribution import MIN_INDEPENDENT_DOCKS_FOR_PACK

    graph = PackDockGraph()
    pack_id = "PCK-042"
    for d in range(n_docks_seen):
        graph.add_session(f"PS-{d}", pack_id, f"D-{d}", "STA-0")
    # Other packs at those docks stay clean so the dock hypotheses never win
    for d in range(n_docks_seen):
        graph.add_session("CLEAN-0", "PCK-000", f"D-{d}", "STA-0")

    result = attribute_session(
        session_id="S-0",
        pack_id=pack_id,
        dock_id=f"D-{n_docks_seen - 1}",
        station_id="STA-0",
        anomalous_features=[_fr("pack_self_heating_excess", "S-0", "pack", pack_id, 6.0)],
        graph=graph,
    )
    if n_docks_seen < MIN_INDEPENDENT_DOCKS_FOR_PACK:
        assert result.selected_owner is None
        assert result.attribution_status == AttributionStatus.INSUFFICIENT_EVIDENCE
    else:
        assert result.selected_owner == OwnerCategory.PACK
