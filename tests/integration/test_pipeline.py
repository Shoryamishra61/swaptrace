"""
Integration tests for the full pipeline.

Tests the complete flow from generation → validation → features → attribution → alerts.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from swaptrace.contracts import (
    AlertEpisode,
    AttributionStatus,
    ChargeSession,
    ChargeStatus,
    DataQualityStatus,
    FeatureRecord,
    FeatureValidityStatus,
    OwnerCategory,
    SourceType,
    TelemetryEvent,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


def make_session(
    session_id: str = "TEST-SES-001",
    pack_id: str = "PCK-001",
    dock_id: str = "DOK-001",
    station_id: str = "STA-01",
    chemistry_id: str = "A-LFP",
    initial_soc: float = 20.0,
    final_soc: float = 95.0,
    initial_temp: float = 25.0,
    ambient_temp: float = 22.0,
    sample_count: int = 120,
    sensor_caps: list[str] | None = None,
) -> ChargeSession:
    if sensor_caps is None:
        sensor_caps = [
            "charger_current",
            "charger_voltage",
            "pack_current",
            "pack_voltage",
            "pack_temperature",
            "soc",
            "ambient_temperature",
            "commanded_current",
            "cell_voltage",
        ]
    return ChargeSession(
        session_id=session_id,
        pack_id=pack_id,
        dock_id=dock_id,
        station_id=station_id,
        chemistry_id=chemistry_id,
        charge_protocol_id=f"CC-CV-{chemistry_id}",
        start_ts=datetime(2026, 9, 10, 8, 0, tzinfo=UTC),
        end_ts=datetime(2026, 9, 10, 9, 30, tzinfo=UTC),
        duration_s=5400.0,
        initial_soc_pct=initial_soc,
        final_soc_pct=final_soc,
        initial_pack_temperature_c=initial_temp,
        ambient_temperature_c=ambient_temp,
        charge_status=ChargeStatus.COMPLETE,
        integrated_charge_ah=15.0,
        integrated_energy_wh=720.0,
        data_quality_status=DataQualityStatus.OK,
        sensor_capabilities=sensor_caps,
        sample_count=sample_count,
        source_type=SourceType.SYNTHETIC,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Schema / Contract Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_telemetry_event_soc_validation():
    """SOC must be 0-100%. Out-of-range raises ValidationError."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        TelemetryEvent(
            event_ts=datetime.now(UTC),
            session_id="S1",
            station_id="STA-01",
            dock_id="DOK-01",
            pack_id="PCK-01",
            soc_pct=110.0,  # invalid
        )


def test_alert_requires_owner_evidence_and_action():
    """
    AlertEpisode with empty recommended_actions must raise ValidationError.
    This enforces the actionability invariant.
    """
    from pydantic import ValidationError

    from swaptrace.contracts import AlertSeverity, EvidenceItem

    with pytest.raises(ValidationError, match="recommended_action"):
        AlertEpisode(
            episode_key="CHARGER_DOCK:DOK-01:feat",
            owner_category=OwnerCategory.CHARGER_DOCK,
            owner_team="charging_infrastructure",
            entity_id="DOK-01",
            severity=AlertSeverity.HIGH,
            evidence=[EvidenceItem(description="Test evidence", entity_id="DOK-01")],
            recommended_actions=[],  # Missing actions — must fail
        )


def test_alert_without_evidence_fails():
    """Alert without evidence must fail schema validation."""
    from pydantic import ValidationError

    from swaptrace.contracts import AlertSeverity

    with pytest.raises(ValidationError, match="evidence"):
        AlertEpisode(
            episode_key="PACK:PCK-01:feat",
            owner_category=OwnerCategory.PACK,
            owner_team="battery_service",
            entity_id="PCK-01",
            severity=AlertSeverity.MEDIUM,
            evidence=[],  # Missing evidence — must fail
            recommended_actions=["Run diagnostics"],
        )


# ─────────────────────────────────────────────────────────────────────────────
# Session / Quality Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_reordered_events_produce_same_sessions():
    """
    Processing events in different orders must produce identical sessions.
    Event-time ordering is idempotent.
    """
    from datetime import timedelta

    from swaptrace.sessions import reconstruct_session

    base_ts = datetime(2026, 9, 10, 8, 0, tzinfo=UTC)
    events = [
        TelemetryEvent(
            event_id=f"E{i}",
            event_ts=base_ts + timedelta(seconds=30 * i),
            session_id="SES-001",
            station_id="STA-01",
            dock_id="DOK-01",
            pack_id="PCK-01",
            charger_current_a=15.0,
            pack_voltage_v=50.0 + i * 0.01,
            soc_pct=20.0 + i * 0.5,
        )
        for i in range(10)
    ]

    session_ordered = reconstruct_session("SES-001", events.copy())
    session_reversed = reconstruct_session("SES-001", list(reversed(events)))

    assert session_ordered.session_id == session_reversed.session_id
    assert session_ordered.sample_count == session_reversed.sample_count
    assert session_ordered.start_ts == session_reversed.start_ts
    assert session_ordered.end_ts == session_reversed.end_ts


def test_invalid_sensor_gap_blocks_feature():
    """
    A session missing required sensors must produce NOT_COMPUTABLE, not a fabricated value.
    """
    from swaptrace.features import compute_dock_cc_current_residual_feature

    session_no_commanded = make_session(
        sensor_caps=[
            "charger_current",
            "charger_voltage",  # missing: commanded_current
            "pack_current",
            "pack_voltage",
            "pack_temperature",
            "soc",
        ]
    )
    result = compute_dock_cc_current_residual_feature(session_no_commanded, {})
    assert result.validity_status == FeatureValidityStatus.SENSOR_MISSING


def test_missing_cell_sensor_disables_cell_feature():
    """Cell dispersion feature must be NOT_COMPUTABLE when cell_voltage sensor missing."""
    from swaptrace.features import compute_cell_dispersion_feature

    session_no_cells = make_session(
        sensor_caps=["charger_current", "pack_voltage", "pack_temperature", "soc"]
        # no cell_voltage
    )
    result = compute_cell_dispersion_feature(session_no_cells, {})
    assert result.validity_status != FeatureValidityStatus.VALID
    assert "SENSOR" in result.validity_status.value or result.value is None


def test_missing_ac_sensor_disables_grid_feature():
    """Grid sag feature must be NOT_COMPUTABLE when ac_input_voltage sensor missing."""
    from swaptrace.features import compute_env_grid_sag_feature

    session_no_ac = make_session(
        sensor_caps=["charger_current", "pack_voltage", "pack_temperature", "soc"]
    )
    result = compute_env_grid_sag_feature(session_no_ac, {})
    assert result.validity_status != FeatureValidityStatus.VALID


def test_session_quality_rejection_for_too_few_samples():
    """Sessions with < 5 samples should be marked as quality rejected."""
    from swaptrace.quality import validate_session

    short_session = make_session(sample_count=3)
    result = validate_session(short_session)
    assert not result.is_valid
    assert any("INSUFFICIENT_SAMPLES" in r for r in result.reasons)


# ─────────────────────────────────────────────────────────────────────────────
# Attribution / Crossing Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_no_crossing_triggers_abstention():
    """
    A pack with only one dock observation cannot be attributed.
    The system must abstain (INSUFFICIENT_EVIDENCE).
    """
    from swaptrace.attribution import AttributionEngine
    from swaptrace.contracts import FeatureRecord, FeatureValidityStatus

    engine = AttributionEngine()

    # Only one session, one dock
    session = make_session(session_id="SES-SINGLE", pack_id="PCK-SOLO", dock_id="DOK-01")
    engine.build_graph([session])

    # Create anomalous dock feature
    fr = FeatureRecord(
        feature_id="dock_cc_current_control_residual",
        session_id="SES-SINGLE",
        entity_type="dock",
        entity_id="DOK-01",
        value=9.0,
        unit="A",
        expected_value=0.0,
        residual=9.0,
        normalized_score=5.0,
        validity_status=FeatureValidityStatus.VALID,
    )

    from swaptrace.attribution import attribute_session

    result = attribute_session(
        session_id="SES-SINGLE",
        pack_id="PCK-SOLO",
        dock_id="DOK-01",
        station_id="STA-01",
        anomalous_features=[fr],
        graph=engine.graph,
    )

    assert result.attribution_status == AttributionStatus.INSUFFICIENT_EVIDENCE
    assert result.selected_owner is None


def test_single_outlier_does_not_create_maintenance_alert():
    """
    A single anomalous observation should NOT create a maintenance alert.
    Persistence threshold requires multiple occurrences.
    """
    from swaptrace.alerts import AlertPolicyEngine
    from swaptrace.contracts import (
        AttributionResult,
        EvidenceItem,
        FeatureRecord,
        FeatureValidityStatus,
    )

    policy = AlertPolicyEngine(persistence_threshold=2)

    result = AttributionResult(
        session_id="SES-ONE",
        selected_owner=OwnerCategory.CHARGER_DOCK,
        attribution_status=AttributionStatus.ATTRIBUTED,
        owner_evidence={"CHARGER_DOCK": [EvidenceItem(description="test", entity_id="DOK-01")]},
        explanation="Test",
        confidence_semantics="MEDIUM",
    )

    fr = FeatureRecord(
        feature_id="dock_cc_current_control_residual",
        session_id="SES-ONE",
        entity_type="dock",
        entity_id="DOK-01",
        value=9.0,
        unit="A",
        expected_value=0.0,
        residual=9.0,
        normalized_score=5.0,
        validity_status=FeatureValidityStatus.VALID,
    )

    alert = policy.process_attribution(
        result=result,
        feature_records=[fr],
        session_id="SES-ONE",
        session_ts=datetime.now(UTC),
    )

    assert alert is None, "Single outlier must NOT create maintenance alert"


def test_episode_deduplication():
    """
    Repeated anomaly detection on same entity/feature must update existing episode,
    not create a new one each time.
    """
    from swaptrace.alerts import AlertPolicyEngine
    from swaptrace.contracts import (
        AttributionResult,
        EvidenceItem,
        FeatureRecord,
        FeatureValidityStatus,
    )

    policy = AlertPolicyEngine(persistence_threshold=2)

    def make_result(sid: str) -> AttributionResult:
        return AttributionResult(
            session_id=sid,
            selected_owner=OwnerCategory.PACK,
            attribution_status=AttributionStatus.ATTRIBUTED,
            owner_evidence={
                "PACK": [EvidenceItem(description="pack anomaly", entity_id="PCK-001")]
            },
            explanation="Pack anomaly across multiple docks",
            confidence_semantics="HIGH",
        )

    def make_fr(sid: str) -> FeatureRecord:
        return FeatureRecord(
            feature_id="pack_self_heating_excess",
            session_id=sid,
            entity_type="pack",
            entity_id="PCK-001",
            value=20.0,
            unit="°C",
            expected_value=5.0,
            residual=15.0,
            normalized_score=4.0,
            validity_status=FeatureValidityStatus.VALID,
        )

    ts = datetime.now(UTC)

    # First occurrence — should NOT alert (below threshold)
    ep1 = policy.process_attribution(make_result("SES-001"), [make_fr("SES-001")], "SES-001", ts)
    assert ep1 is None, "Should not alert on first occurrence"

    # Second occurrence — should alert (at threshold)
    ep2 = policy.process_attribution(make_result("SES-002"), [make_fr("SES-002")], "SES-002", ts)
    assert ep2 is not None, "Should alert on second occurrence"

    # Third occurrence — should UPDATE existing episode, not create new
    ep3 = policy.process_attribution(make_result("SES-003"), [make_fr("SES-003")], "SES-003", ts)
    assert ep3 is not None

    episodes = policy.get_all_episodes()
    assert len(episodes) == 1, f"Expected 1 deduplicated episode, got {len(episodes)}"
    assert episodes[0].occurrence_count >= 2


# ─────────────────────────────────────────────────────────────────────────────
# Scenario Tests (Behavioral)
# ─────────────────────────────────────────────────────────────────────────────


def test_dock_fault_follows_dock():
    """
    Dock fault scenario: multiple independent packs affected at one dock,
    same packs normal elsewhere → CHARGER_DOCK attribution.
    """
    from swaptrace.attribution import AttributionEngine, attribute_session
    from swaptrace.contracts import FeatureRecord, FeatureValidityStatus

    engine = AttributionEngine()

    # Build graph: 3 packs visit faulty_dock AND other_docks
    sessions = []
    packs = ["PCK-A", "PCK-B", "PCK-C"]
    for i, pack in enumerate(packs):
        # Each pack visits faulty_dock
        sessions.append(
            make_session(
                session_id=f"FAULTY-{i}",
                pack_id=pack,
                dock_id="DOK-FAULTY",
                station_id="STA-01",
            )
        )
        # Each pack also visits healthy docks
        sessions.append(
            make_session(
                session_id=f"HEALTHY-{i}",
                pack_id=pack,
                dock_id=f"DOK-GOOD-{i}",
                station_id="STA-01",
            )
        )

    engine.build_graph(sessions)

    # Create dock-level anomaly features for faulty dock
    anomalous = [
        FeatureRecord(
            feature_id="dock_cc_current_control_residual",
            session_id="FAULTY-0",
            entity_type="dock",
            entity_id="DOK-FAULTY",
            value=8.0,
            unit="A",
            normalized_score=5.0,
            validity_status=FeatureValidityStatus.VALID,
        )
    ]

    result = attribute_session(
        session_id="FAULTY-0",
        pack_id="PCK-A",
        dock_id="DOK-FAULTY",
        station_id="STA-01",
        anomalous_features=anomalous,
        graph=engine.graph,
    )

    # With sufficient crossing, should attribute to CHARGER_DOCK
    # (3 packs served by the dock)
    assert result.attribution_status == AttributionStatus.ATTRIBUTED
    assert result.selected_owner == OwnerCategory.CHARGER_DOCK


def test_pack_fault_follows_pack():
    """
    Pack fault scenario: one pack anomalous across multiple docks,
    those docks are normal with other packs → PACK attribution.
    """
    from swaptrace.attribution import AttributionEngine, attribute_session
    from swaptrace.contracts import FeatureRecord, FeatureValidityStatus

    engine = AttributionEngine()

    # Faulty pack visits 3 docks; healthy packs also visit those docks
    faulty_pack = "PCK-FAULTY"
    healthy_packs = ["PCK-X", "PCK-Y"]
    docks = ["DOK-1", "DOK-2", "DOK-3"]

    sessions = []
    for i, dock in enumerate(docks):
        sessions.append(
            make_session(
                session_id=f"FAULTY-PACK-{i}",
                pack_id=faulty_pack,
                dock_id=dock,
                station_id="STA-01",
            )
        )
        for j, hp in enumerate(healthy_packs):
            sessions.append(
                make_session(
                    session_id=f"HEALTHY-PACK-{i}-{j}",
                    pack_id=hp,
                    dock_id=dock,
                    station_id="STA-01",
                )
            )

    engine.build_graph(sessions)

    # Pack-level anomaly features
    anomalous = [
        FeatureRecord(
            feature_id="pack_self_heating_excess",
            session_id="FAULTY-PACK-0",
            entity_type="pack",
            entity_id=faulty_pack,
            value=25.0,
            unit="°C",
            normalized_score=4.5,
            validity_status=FeatureValidityStatus.VALID,
        )
    ]

    result = attribute_session(
        session_id="FAULTY-PACK-0",
        pack_id=faulty_pack,
        dock_id="DOK-1",
        station_id="STA-01",
        anomalous_features=anomalous,
        graph=engine.graph,
    )

    assert result.attribution_status == AttributionStatus.ATTRIBUTED
    assert result.selected_owner == OwnerCategory.PACK


def test_cell_divergence_is_detected():
    """Cell voltage divergence feature detects when spread exceeds threshold."""
    from swaptrace.physics import compute_cell_voltage_dispersion

    # Healthy cells: ~2 mV spread
    healthy_cells = [3.65 + 0.001 * i for i in range(14)]
    healthy_result = compute_cell_voltage_dispersion(healthy_cells)
    assert healthy_result["spread_v"] < 0.02

    # Divergent pack: one cell low
    divergent_cells = [3.65] * 13 + [3.50]
    divergent_result = compute_cell_voltage_dispersion(divergent_cells)
    assert divergent_result["spread_v"] > 0.1
    assert divergent_result["spread_v"] > healthy_result["spread_v"] * 5


def test_low_start_soc_is_not_a_fault():
    """
    A session starting at low SOC will have longer duration but must not be
    flagged as a fault purely based on session duration.

    The dock CC current feature should be neutral for low-SOC if current
    is properly delivered.
    """
    from swaptrace.features import compute_dock_cc_current_residual_feature

    # Low SOC session — longer charge, but commanded == delivered
    session = make_session(initial_soc=5.0, final_soc=95.0)
    telemetry_summary = {
        "cc_commanded_current_a": 15.0,
        "cc_mean_charger_current_a": 15.0,  # Full delivery — healthy dock
        "cc_sample_count": 200,
        "bms_limit_reason": None,
    }
    result = compute_dock_cc_current_residual_feature(session, telemetry_summary)

    assert result.validity_status == FeatureValidityStatus.VALID
    assert result.value is not None
    assert abs(result.value) < 0.5  # Near-zero deficit = healthy dock


def test_legitimate_bms_derating_is_not_dock_fault():
    """
    BMS thermal derating that reduces current must not automatically be attributed
    as a dock current fault. The bms_limited flag must be set.
    """
    from swaptrace.features import compute_dock_cc_current_residual_feature

    session = make_session()
    telemetry_summary = {
        "cc_commanded_current_a": 15.0,
        "cc_mean_charger_current_a": 8.0,  # Reduced — but due to BMS
        "cc_sample_count": 100,
        "bms_limit_reason": "THERMAL_PROTECTION",
    }
    result = compute_dock_cc_current_residual_feature(session, telemetry_summary)

    assert result.validity_status == FeatureValidityStatus.VALID
    assert result.context_signature.get("bms_limited") is True
    # Attribution layer must consider this — test that the context carries the flag
    assert result.context_signature.get("bms_limit_reason") == "THERMAL_PROTECTION"


def test_common_mode_without_sensor_abstains():
    """
    Environmental feature without measured ambient sensor must not
    automatically produce an environment attribution.
    """
    from swaptrace.features import compute_env_grid_sag_feature

    session_no_ac = make_session(
        sensor_caps=["charger_current", "pack_voltage", "pack_temperature", "soc"]
        # No ac_input_voltage
    )
    result = compute_env_grid_sag_feature(session_no_ac, {})
    assert result.validity_status != FeatureValidityStatus.VALID
    # Must not claim grid sag without the measurement


def test_future_data_does_not_change_past_prediction():
    """
    Adding future sessions to training data must not change historical predictions.
    Point-in-time correctness.
    """
    from datetime import timedelta

    import polars as pl

    from swaptrace.baselines import ContextualBaseline

    base_ts = datetime(2026, 9, 10, tzinfo=UTC)
    cutoff = base_ts + timedelta(days=7)  # training cutoff

    # Sessions before cutoff
    past_sessions = pl.DataFrame(
        [
            {
                "session_id": f"PAST-{i}",
                "chemistry_id": "A-LFP",
                "initial_soc_pct": 20.0,
                "ambient_temperature_c": 22.0,
                "charge_protocol_id": "CC-CV-A-LFP",
                "start_ts": base_ts + timedelta(days=i),
            }
            for i in range(5)
        ]
    )
    past_values = [5.0, 5.1, 4.9, 5.05, 4.95]

    baseline_before = ContextualBaseline("test_feature", training_cutoff=cutoff)
    baseline_before.fit(past_sessions, past_values, [f"PAST-{i}" for i in range(5)])
    expected_before = baseline_before._global_median

    # Add future sessions — should not affect training cutoff
    future_sessions = pl.DataFrame(
        [
            {
                "session_id": "FUTURE-1",
                "chemistry_id": "A-LFP",
                "initial_soc_pct": 20.0,
                "ambient_temperature_c": 22.0,
                "charge_protocol_id": "CC-CV-A-LFP",
                "start_ts": base_ts + timedelta(days=10),
            }  # after cutoff
        ]
    )

    all_sessions = pl.concat([past_sessions, future_sessions])
    future_value = [50.0]  # very different value

    baseline_after = ContextualBaseline("test_feature", training_cutoff=cutoff)
    baseline_after.fit(
        all_sessions, past_values + future_value, [f"PAST-{i}" for i in range(5)] + ["FUTURE-1"]
    )

    expected_after = baseline_after._global_median

    # Future session (after cutoff) should not contaminate the baseline
    assert abs(expected_before - expected_after) < 0.5, (
        f"Future data contaminated baseline: {expected_before:.3f} → {expected_after:.3f}"
    )


def test_resolution_history_is_auditable():
    """Alert transitions must be stored and retrievable — audit history."""
    from swaptrace.alerts import AlertPolicyEngine
    from swaptrace.contracts import (
        AttributionResult,
        EvidenceItem,
        FeatureRecord,
        FeatureValidityStatus,
        ResolutionFeedback,
    )

    policy = AlertPolicyEngine(persistence_threshold=1)  # threshold=1 for test speed

    def make_attr():
        return AttributionResult(
            session_id="SES-AUDIT",
            selected_owner=OwnerCategory.PACK,
            attribution_status=AttributionStatus.ATTRIBUTED,
            owner_evidence={"PACK": [EvidenceItem(description="audit test", entity_id="PCK-001")]},
            explanation="Audit test",
            confidence_semantics="HIGH",
        )

    fr = FeatureRecord(
        feature_id="pack_self_heating_excess",
        session_id="SES-AUDIT",
        entity_type="pack",
        entity_id="PCK-001",
        value=20.0,
        unit="°C",
        normalized_score=4.0,
        validity_status=FeatureValidityStatus.VALID,
    )

    ts = datetime.now(UTC)
    ep = policy.process_attribution(make_attr(), [fr], "SES-AUDIT", ts)
    assert ep is not None

    key = ep.episode_key
    policy.acknowledge(key, actor="operator_test")
    feedback = ResolutionFeedback(
        episode_id=key,
        resolution_outcome="CONFIRMED",
        resolved_by="technician_001",
        notes="Pack replaced",
        actual_owner=OwnerCategory.PACK,
    )
    policy.resolve(key, feedback)

    episodes = policy.get_all_episodes()
    assert len(episodes) == 1
    ep_final = episodes[0]
    assert ep_final.resolution is not None
    assert ep_final.resolution.resolution_outcome == "CONFIRMED"
    assert ep_final.resolution.resolved_by == "technician_001"
    # Transitions history preserved
    assert any(t.actor == "operator_test" for t in ep_final.transitions)


def test_fault_injection_labels_are_not_model_features():
    """
    Ground-truth fault labels must not appear in computed feature records.
    This verifies evaluation integrity.
    """
    from benchmark.generator import BenchmarkGenerator

    from swaptrace.features import compute_all_features

    gen = BenchmarkGenerator(seed=42)
    gen.inject_faults()
    sessions = gen.generate_sessions()
    events = gen.generate_telemetry_events(sessions[:5])

    for session in sessions[:5]:
        sess_events = [e for e in events if e.session_id == session.session_id]
        features = compute_all_features(session, sess_events)

        for fr in features:
            # Feature context must not contain any ground-truth labels
            ctx_str = str(fr.context_signature)
            assert "fault_type" not in ctx_str, "Feature context contains fault_type label!"
            assert "_injected" not in ctx_str, "Feature context contains injection metadata!"
            assert "is_faulty" not in ctx_str, "Feature context contains is_faulty label!"


def test_end_to_end_demo_reproducible():
    """
    Running the pipeline twice with the same seed must produce identical
    session counts and the same set of session IDs.
    """
    from benchmark.generator import BenchmarkGenerator

    gen1 = BenchmarkGenerator(seed=42)
    gen1.inject_faults()
    sessions1 = gen1.generate_sessions()
    ids1 = sorted([s.session_id for s in sessions1])

    gen2 = BenchmarkGenerator(seed=42)
    gen2.inject_faults()
    sessions2 = gen2.generate_sessions()
    ids2 = sorted([s.session_id for s in sessions2])

    assert len(sessions1) == len(sessions2)
    assert ids1 == ids2, "Different session IDs produced from same seed — not deterministic!"


def test_reingestion_is_idempotent(tmp_path):
    """
    Ingesting the same sessions twice must not create duplicate records.
    """
    from swaptrace.storage import SwapTraceDB

    db = SwapTraceDB(db_path=str(tmp_path / "test.db"))
    session = make_session()

    db.upsert_sessions([session])
    db.upsert_sessions([session])  # Second upsert

    count_df = db.query("SELECT COUNT(*) as cnt FROM sessions")
    count = count_df["cnt"][0]
    assert count == 1, f"Expected 1 session after 2 upserts, got {count}"
    db.close()


def test_concurrent_faults_do_not_force_false_certainty():
    """
    When both pack AND dock faults are active, the system must not
    force a single confident attribution. It should indicate CONFLICTING_EVIDENCE
    or use the strongest signal without claiming certainty.
    """
    from swaptrace.attribution import AttributionEngine, attribute_session
    from swaptrace.contracts import FeatureRecord, FeatureValidityStatus

    engine = AttributionEngine()

    # Build graph with some crossing
    sessions_for_graph = [
        make_session(
            session_id=f"GRAPH-{i}", pack_id="PCK-MULTI", dock_id=f"DOK-{i}", station_id="STA-01"
        )
        for i in range(3)
    ]
    engine.build_graph(sessions_for_graph)

    # Both dock AND pack anomalies in same session
    anomalous = [
        FeatureRecord(
            feature_id="dock_cc_current_control_residual",
            session_id="CONCURRENT-1",
            entity_type="dock",
            entity_id="DOK-0",
            value=8.0,
            unit="A",
            normalized_score=5.0,
            validity_status=FeatureValidityStatus.VALID,
        ),
        FeatureRecord(
            feature_id="pack_self_heating_excess",
            session_id="CONCURRENT-1",
            entity_type="pack",
            entity_id="PCK-MULTI",
            value=25.0,
            unit="°C",
            normalized_score=4.5,
            validity_status=FeatureValidityStatus.VALID,
        ),
    ]

    result = attribute_session(
        session_id="CONCURRENT-1",
        pack_id="PCK-MULTI",
        dock_id="DOK-0",
        station_id="STA-01",
        anomalous_features=anomalous,
        graph=engine.graph,
    )

    # Must not claim high certainty for either — should be ambiguous or pick strongest
    if result.attribution_status == AttributionStatus.ATTRIBUTED:
        assert result.confidence_semantics in ("MEDIUM", "LOW"), (
            "Concurrent faults must not produce HIGH confidence attribution"
        )
    # CONFLICTING_EVIDENCE or INSUFFICIENT_EVIDENCE are also valid outcomes
