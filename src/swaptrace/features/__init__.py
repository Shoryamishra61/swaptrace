"""
SwapTrace — Feature computation pipeline.

Computes all 8 owner-specific diagnostic features from charge sessions.
Every feature:
- Checks required sensor capabilities before computing
- Returns NOT_COMPUTABLE (not zero) when sensors are missing
- Exposes operational question, owner, formula, units, confounders
- Is versioned and traceable to source sessions
"""

from __future__ import annotations

from typing import Any

import numpy as np

from swaptrace.contracts import (
    ChargeSession,
    FeatureRecord,
    FeatureValidityStatus,
    OwnerCategory,
    SensorCapability,
)
from swaptrace.observability import get_logger
from swaptrace.physics import (
    compute_cell_voltage_dispersion,
    compute_contact_resistance,
    compute_curve_drift_score,
    compute_dock_cc_current_residual,
    compute_grid_sag,
    compute_pack_electrical_response,
    compute_pack_thermal_residual,
    compute_site_thermal_deviation,
)
from swaptrace.quality import check_sensor_capability

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Feature Registry — metadata about each feature
# ---------------------------------------------------------------------------

FEATURE_REGISTRY: dict[str, dict[str, Any]] = {
    "dock_cc_current_control_residual": {
        "version": 1,
        "owner": OwnerCategory.CHARGER_DOCK,
        "operational_question": "Is the dock delivering the commanded CC current?",
        "required_sensors": [
            SensorCapability.CHARGER_CURRENT.value,
            SensorCapability.COMMANDED_CURRENT.value,
        ],
        "valid_phases": ["CC"],
        "unit": "A",
        "formula": "deficit_a = commanded_a - delivered_a",
        "confounders": ["bms_current_limit", "thermal_derating", "low_soc_startup"],
        "minimum_evidence": {"sessions": 2, "independent_packs": 2},
        "recommended_action": "Inspect charger control circuitry and power delivery hardware.",
        "severity_policy": "HIGH if delivery_ratio < 0.7 over 3+ sessions across 2+ packs",
    },
    "dock_contact_resistance_excess": {
        "version": 1,
        "owner": OwnerCategory.CHARGER_DOCK,
        "operational_question": "Is the dock contact path showing elevated resistance?",
        "required_sensors": [
            SensorCapability.CHARGER_VOLTAGE.value,
            SensorCapability.PACK_VOLTAGE.value,
            SensorCapability.CHARGER_CURRENT.value,
        ],
        "valid_phases": ["CC"],
        "unit": "mΩ",
        "formula": "R_contact = (V_charger - V_pack) / I_cc",
        "confounders": ["measurement_alignment", "sensor_offset", "cable_resistance"],
        "minimum_evidence": {"sessions": 2, "min_current_a": 2.0},
        "recommended_action": "Inspect dock connector, contact pins, and cable path.",
        "severity_policy": "HIGH if contact_r > 50 mΩ (baseline ~5 mΩ)",
    },
    "pack_self_heating_excess": {
        "version": 1,
        "owner": OwnerCategory.PACK,
        "operational_question": "Is this pack heating more than expected under comparable load?",
        "required_sensors": [
            SensorCapability.PACK_TEMPERATURE.value,
            SensorCapability.PACK_CURRENT.value,
            SensorCapability.AMBIENT_TEMPERATURE.value,
        ],
        "valid_phases": ["CC", "CV"],
        "unit": "°C",
        "formula": "residual_c = measured_temp_rise - expected_temp_rise(I, T_ambient, duration)",
        "confounders": ["ambient_temperature", "initial_pack_temperature", "session_duration"],
        "minimum_evidence": {"sessions": 2, "independent_docks": 2},
        "recommended_action": "Inspect pack thermal hardware, BMS, and internal resistance.",
        "severity_policy": "HIGH if residual > 15°C on 2+ independent docks",
    },
    "pack_electrical_response_anomaly": {
        "version": 1,
        "owner": OwnerCategory.PACK,
        "operational_question": "Is this pack showing elevated polarization during CC charging?",
        "required_sensors": [
            SensorCapability.PACK_VOLTAGE.value,
            SensorCapability.PACK_CURRENT.value,
        ],
        "valid_phases": ["CC"],
        "unit": "V",
        "formula": "polarization_v = V_terminal - OCV (proxy, not true DCIR)",
        "confounders": ["soc_hysteresis", "temperature", "aging"],
        "minimum_evidence": {"sessions": 2, "independent_docks": 2},
        "recommended_action": "Run pack electrical diagnostics and BMS health check.",
        "severity_policy": "MEDIUM if polarization anomaly on 2+ independent docks",
    },
    "cell_voltage_dispersion_excess": {
        "version": 1,
        "owner": OwnerCategory.CELL_CHEMISTRY,
        "operational_question": "Are individual cells showing abnormal voltage spread?",
        "required_sensors": [SensorCapability.CELL_VOLTAGE.value],
        "valid_phases": ["CC"],
        "unit": "V",
        "formula": "spread_v = max(cells) - min(cells)",
        "confounders": ["sensor_offset", "imbalance", "soc_nonuniformity"],
        "minimum_evidence": {"sessions": 1, "min_cells": 6},
        "recommended_action": "Inspect suspect cells and validate cell voltage sensors. Route to battery engineering.",
        "severity_policy": "MEDIUM if spread > 0.1V; HIGH if spread > 0.3V",
    },
    "chemistry_charge_curve_drift": {
        "version": 1,
        "owner": OwnerCategory.CELL_CHEMISTRY,
        "operational_question": "Is this pack's charge curve deviating from its chemistry cohort?",
        "required_sensors": [SensorCapability.PACK_VOLTAGE.value, SensorCapability.SOC.value],
        "valid_phases": ["CC"],
        "unit": "V (MAD)",
        "formula": "curve_mad_v = mean(|V_session(soc) - V_reference(soc)|) over common SOC range",
        "confounders": ["protocol_mismatch", "temperature_difference", "age_bracket"],
        "minimum_evidence": {"sessions": 3, "reference_sessions": 5},
        "recommended_action": "Battery engineering investigation of chemistry/aging signature.",
        "severity_policy": "MEDIUM if curve_mad > 0.05V",
    },
    "env_sitewide_heat_derate": {
        "version": 1,
        "owner": OwnerCategory.ENVIRONMENT,
        "operational_question": "Is a site-wide thermal condition causing performance reduction?",
        "required_sensors": [
            SensorCapability.AMBIENT_TEMPERATURE.value,
            SensorCapability.PACK_TEMPERATURE.value,
        ],
        "valid_phases": ["CC", "CV"],
        "unit": "°C (thermal excess)",
        "formula": "thermal_excess_c = ambient_c - baseline_ambient_c",
        "confounders": ["shared_pdu_fault", "hvac_failure", "seasonal_variation"],
        "minimum_evidence": {"affected_packs": 3, "affected_docks": 2, "shared_station": True},
        "recommended_action": "Inspect site cooling, ventilation, and shared thermal infrastructure.",
        "severity_policy": "HIGH if multiple independent packs/docks affected at same station",
    },
    "env_grid_sag_power_loss": {
        "version": 1,
        "owner": OwnerCategory.ENVIRONMENT,
        "operational_question": "Is an upstream supply voltage sag reducing charging power?",
        "required_sensors": [SensorCapability.AC_INPUT_VOLTAGE.value],
        "valid_phases": ["CC"],
        "unit": "V (sag from nominal)",
        "formula": "sag_v = V_nominal - V_measured; sag_pct = sag_v / V_nominal * 100",
        "confounders": ["local_load_variation", "meter_calibration"],
        "minimum_evidence": {"affected_docks": 2, "station_level": True},
        "recommended_action": "Inspect station electrical supply and upstream distribution.",
        "severity_policy": "HIGH if sag > 10% on multiple docks",
    },
}


# ---------------------------------------------------------------------------
# Feature computation for a single session
# ---------------------------------------------------------------------------


def _not_computable(
    feature_id: str,
    session: ChargeSession,
    entity_type: str,
    entity_id: str,
    reason: str,
    missing_sensors: list[str] | None = None,
) -> FeatureRecord:
    status = (
        FeatureValidityStatus.SENSOR_MISSING
        if missing_sensors
        else FeatureValidityStatus.NOT_COMPUTABLE
    )
    return FeatureRecord(
        feature_id=feature_id,
        feature_version=FEATURE_REGISTRY.get(feature_id, {}).get("version", 1),
        session_id=session.session_id,
        entity_type=entity_type,
        entity_id=entity_id,
        unit=FEATURE_REGISTRY.get(feature_id, {}).get("unit", "?"),
        validity_status=status,
        invalidity_reason=reason,
    )


def compute_dock_cc_current_residual_feature(
    session: ChargeSession,
    telemetry_summary: dict[str, Any],
) -> FeatureRecord:
    """F-D01: Dock current control residual."""
    fid = "dock_cc_current_control_residual"
    required = FEATURE_REGISTRY[fid]["required_sensors"]
    ok, missing = check_sensor_capability(session, required)
    if not ok:
        return _not_computable(
            fid, session, "dock", session.dock_id, f"missing_sensors:{missing}", missing
        )

    commanded = telemetry_summary.get("cc_commanded_current_a")
    delivered = telemetry_summary.get("cc_mean_charger_current_a")
    bms_limit = telemetry_summary.get("bms_limit_reason")

    if commanded is None or delivered is None:
        return _not_computable(fid, session, "dock", session.dock_id, "no_cc_phase_data")

    result = compute_dock_cc_current_residual(commanded, delivered, bms_limit)
    if not result["valid"]:
        return _not_computable(
            fid, session, "dock", session.dock_id, result.get("reason", "invalid")
        )

    deficit = result["deficit_a"]
    ratio = result["delivery_ratio"]

    return FeatureRecord(
        feature_id=fid,
        feature_version=1,
        session_id=session.session_id,
        entity_type="dock",
        entity_id=session.dock_id,
        value=deficit,
        unit="A",
        expected_value=0.0,
        residual=deficit,
        normalized_score=max(0, 1.0 - ratio),
        context_signature={
            "commanded_a": commanded,
            "delivered_a": delivered,
            "bms_limited": bool(result.get("bms_limited")),
            "bms_limit_reason": bms_limit if result.get("bms_limited") else None,
            "delivery_ratio": ratio,
        },
        validity_status=FeatureValidityStatus.VALID,
        sample_count=telemetry_summary.get("cc_sample_count", 0),
    )


def compute_dock_contact_resistance_feature(
    session: ChargeSession,
    telemetry_summary: dict[str, Any],
) -> FeatureRecord:
    """F-D02: Dock contact resistance excess."""
    fid = "dock_contact_resistance_excess"
    required = FEATURE_REGISTRY[fid]["required_sensors"]
    ok, missing = check_sensor_capability(session, required)
    if not ok:
        return _not_computable(
            fid, session, "dock", session.dock_id, f"missing_sensors:{missing}", missing
        )

    charger_v = telemetry_summary.get("cc_mean_charger_voltage_v")
    pack_v = telemetry_summary.get("cc_mean_pack_voltage_v")
    current = telemetry_summary.get("cc_mean_charger_current_a")

    if any(x is None for x in [charger_v, pack_v, current]):
        return _not_computable(fid, session, "dock", session.dock_id, "no_cc_voltage_data")

    result = compute_contact_resistance(charger_v, pack_v, current)
    if not result["valid"]:
        return _not_computable(
            fid, session, "dock", session.dock_id, result.get("reason", "invalid")
        )

    r_mohm = result["resistance_mohm"]

    return FeatureRecord(
        feature_id=fid,
        feature_version=1,
        session_id=session.session_id,
        entity_type="dock",
        entity_id=session.dock_id,
        value=r_mohm,
        unit="mΩ",
        expected_value=5.0,  # ~5 mΩ baseline
        residual=r_mohm - 5.0,
        normalized_score=min(r_mohm / 50.0, 5.0),  # relative to 50 mΩ concern threshold
        context_signature={
            "charger_v": charger_v,
            "pack_v": pack_v,
            "current_a": current,
            "v_diff_v": result.get("v_diff_v"),
        },
        validity_status=FeatureValidityStatus.VALID,
        sample_count=telemetry_summary.get("cc_sample_count", 0),
    )


def compute_pack_thermal_feature(
    session: ChargeSession,
    telemetry_summary: dict[str, Any],
    expected_temp_rise_c: float,
) -> FeatureRecord:
    """F-P01: Pack self-heating excess."""
    fid = "pack_self_heating_excess"
    required = FEATURE_REGISTRY[fid]["required_sensors"]
    ok, missing = check_sensor_capability(session, required)
    if not ok:
        return _not_computable(
            fid, session, "pack", session.pack_id, f"missing_sensors:{missing}", missing
        )

    initial_temp = session.initial_pack_temperature_c
    final_temp = telemetry_summary.get("final_pack_temperature_c")

    if initial_temp is None or final_temp is None:
        return _not_computable(fid, session, "pack", session.pack_id, "missing_temperature_data")

    measured_rise = final_temp - initial_temp
    result = compute_pack_thermal_residual(measured_rise, expected_temp_rise_c)

    residual_c = result["residual_c"]

    return FeatureRecord(
        feature_id=fid,
        feature_version=1,
        session_id=session.session_id,
        entity_type="pack",
        entity_id=session.pack_id,
        value=measured_rise,
        unit="°C",
        expected_value=expected_temp_rise_c,
        residual=residual_c,
        normalized_score=abs(residual_c) / max(expected_temp_rise_c, 1.0),
        context_signature={
            "initial_temp_c": initial_temp,
            "final_temp_c": final_temp,
            "ambient_c": session.ambient_temperature_c,
            "expected_rise_c": expected_temp_rise_c,
            "chemistry": session.chemistry_id,
        },
        validity_status=FeatureValidityStatus.VALID,
        sample_count=telemetry_summary.get("total_sample_count", 0),
    )


def compute_pack_electrical_feature(
    session: ChargeSession,
    telemetry_summary: dict[str, Any],
    expected_polarization_v: float,
) -> FeatureRecord:
    """F-P02: Pack electrical response anomaly."""
    fid = "pack_electrical_response_anomaly"
    required = FEATURE_REGISTRY[fid]["required_sensors"]
    ok, missing = check_sensor_capability(session, required)
    if not ok:
        return _not_computable(
            fid, session, "pack", session.pack_id, f"missing_sensors:{missing}", missing
        )

    pack_v = telemetry_summary.get("cc_mean_pack_voltage_v")
    current = telemetry_summary.get("cc_mean_charger_current_a")
    ocv_estimate = telemetry_summary.get("ocv_estimate_v")

    if any(x is None for x in [pack_v, current, ocv_estimate]):
        return _not_computable(fid, session, "pack", session.pack_id, "missing_cc_data")

    result = compute_pack_electrical_response(pack_v, ocv_estimate, current)
    if not result["valid"]:
        return _not_computable(
            fid, session, "pack", session.pack_id, result.get("reason", "invalid")
        )

    pol_v = result["polarization_v"]
    residual = pol_v - expected_polarization_v

    return FeatureRecord(
        feature_id=fid,
        feature_version=1,
        session_id=session.session_id,
        entity_type="pack",
        entity_id=session.pack_id,
        value=pol_v,
        unit="V",
        expected_value=expected_polarization_v,
        residual=residual,
        normalized_score=abs(residual) / max(expected_polarization_v, 0.1),
        context_signature={
            "pack_v": pack_v,
            "current_a": current,
            "ocv_estimate_v": ocv_estimate,
            "chemistry": session.chemistry_id,
        },
        validity_status=FeatureValidityStatus.VALID,
        sample_count=telemetry_summary.get("cc_sample_count", 0),
    )


def compute_cell_dispersion_feature(
    session: ChargeSession,
    telemetry_summary: dict[str, Any],
    expected_spread_v: float = 0.01,
) -> FeatureRecord:
    """F-C01: Cell voltage dispersion excess."""
    fid = "cell_voltage_dispersion_excess"
    required = FEATURE_REGISTRY[fid]["required_sensors"]
    ok, missing = check_sensor_capability(session, required)
    if not ok:
        return _not_computable(
            fid, session, "pack", session.pack_id, f"missing_sensors:{missing}", missing
        )

    cell_voltages = telemetry_summary.get("cc_mean_cell_voltages_v")
    if not cell_voltages:
        return _not_computable(fid, session, "pack", session.pack_id, "no_cell_voltage_data")

    result = compute_cell_voltage_dispersion(cell_voltages)
    if not result["valid"]:
        return _not_computable(
            fid, session, "pack", session.pack_id, result.get("reason", "invalid")
        )

    spread = result["spread_v"]
    residual = spread - expected_spread_v

    return FeatureRecord(
        feature_id=fid,
        feature_version=1,
        session_id=session.session_id,
        entity_type="pack",
        entity_id=session.pack_id,
        value=spread,
        unit="V",
        expected_value=expected_spread_v,
        residual=residual,
        normalized_score=spread / 0.1,  # normalize to 100 mV threshold
        context_signature={
            "n_cells": result.get("n_cells"),
            "min_cell_v": result.get("min_cell_v"),
            "max_cell_v": result.get("max_cell_v"),
            "std_v": result.get("std_v"),
        },
        validity_status=FeatureValidityStatus.VALID,
        sample_count=telemetry_summary.get("cc_sample_count", 0),
    )


def compute_curve_drift_feature(
    session: ChargeSession,
    telemetry_summary: dict[str, Any],
    reference_soc: list[float],
    reference_voltage: list[float],
) -> FeatureRecord:
    """F-C02: Chemistry/cohort charge curve drift."""
    fid = "chemistry_charge_curve_drift"
    required = FEATURE_REGISTRY[fid]["required_sensors"]
    ok, missing = check_sensor_capability(session, required)
    if not ok:
        return _not_computable(
            fid, session, "pack", session.pack_id, f"missing_sensors:{missing}", missing
        )

    sess_soc = telemetry_summary.get("cc_soc_sequence")
    sess_v = telemetry_summary.get("cc_voltage_sequence")

    if not sess_soc or not sess_v or len(sess_soc) < 5:
        return _not_computable(fid, session, "pack", session.pack_id, "insufficient_curve_data")

    result = compute_curve_drift_score(sess_soc, sess_v, reference_soc, reference_voltage)
    if not result["valid"]:
        return _not_computable(
            fid, session, "pack", session.pack_id, result.get("reason", "invalid")
        )

    mad_v = result["curve_mad_v"]

    return FeatureRecord(
        feature_id=fid,
        feature_version=1,
        session_id=session.session_id,
        entity_type="pack",
        entity_id=session.pack_id,
        value=mad_v,
        unit="V",
        expected_value=0.01,  # <10 mV expected for healthy cohort match
        residual=mad_v - 0.01,
        normalized_score=mad_v / 0.05,
        context_signature={
            "soc_coverage_pct": result.get("soc_coverage_pct"),
            "chemistry": session.chemistry_id,
            "max_dev_v": result.get("curve_max_deviation_v"),
        },
        validity_status=FeatureValidityStatus.VALID,
        sample_count=telemetry_summary.get("cc_sample_count", 0),
    )


def compute_env_thermal_feature(
    session: ChargeSession,
    telemetry_summary: dict[str, Any],
    baseline_ambient_c: float,
) -> FeatureRecord:
    """F-E01: Site-wide thermal derating."""
    fid = "env_sitewide_heat_derate"
    required = FEATURE_REGISTRY[fid]["required_sensors"]
    ok, missing = check_sensor_capability(session, required)
    if not ok:
        return _not_computable(
            fid, session, "station", session.station_id, f"missing_sensors:{missing}", missing
        )

    ambient = session.ambient_temperature_c
    if ambient is None:
        return _not_computable(fid, session, "station", session.station_id, "no_ambient_temp")

    delivery_ratio = telemetry_summary.get("delivery_ratio", 1.0)
    # Expected reduction per °C above baseline (0.5% per degree as heuristic)
    temp_excess = ambient - baseline_ambient_c
    expected_reduction = max(0, temp_excess * 0.005)

    result = compute_site_thermal_deviation(
        ambient_temperature_c=ambient,
        baseline_ambient_c=baseline_ambient_c,
        observed_charge_reduction_factor=1.0 - delivery_ratio,
        expected_reduction_at_temp=expected_reduction,
    )

    thermal_excess = result["thermal_excess_c"]

    return FeatureRecord(
        feature_id=fid,
        feature_version=1,
        session_id=session.session_id,
        entity_type="station",
        entity_id=session.station_id,
        value=thermal_excess,
        unit="°C",
        expected_value=0.0,
        residual=thermal_excess,
        normalized_score=abs(thermal_excess) / 10.0,
        context_signature={
            "ambient_c": ambient,
            "baseline_ambient_c": baseline_ambient_c,
            "station_id": session.station_id,
        },
        validity_status=FeatureValidityStatus.VALID,
        sample_count=telemetry_summary.get("total_sample_count", 0),
    )


def compute_env_grid_sag_feature(
    session: ChargeSession,
    telemetry_summary: dict[str, Any],
    nominal_voltage_v: float = 230.0,
) -> FeatureRecord:
    """F-E02: Upstream supply sag."""
    fid = "env_grid_sag_power_loss"
    required = FEATURE_REGISTRY[fid]["required_sensors"]
    ok, missing = check_sensor_capability(session, required)
    if not ok:
        return _not_computable(
            fid, session, "station", session.station_id, f"missing_sensors:{missing}", missing
        )

    ac_v = telemetry_summary.get("mean_ac_input_voltage_v")
    if ac_v is None:
        return _not_computable(fid, session, "station", session.station_id, "no_ac_voltage_data")

    result = compute_grid_sag(ac_v, nominal_voltage_v)

    return FeatureRecord(
        feature_id=fid,
        feature_version=1,
        session_id=session.session_id,
        entity_type="station",
        entity_id=session.station_id,
        value=result["sag_v"],
        unit="V",
        expected_value=0.0,
        residual=result["sag_v"],
        normalized_score=result["sag_pct"] / 10.0,
        context_signature={
            "measured_v": ac_v,
            "nominal_v": nominal_voltage_v,
            "sag_pct": result.get("sag_pct"),
            "is_sagging": result.get("is_sagging"),
            "station_id": session.station_id,
        },
        validity_status=FeatureValidityStatus.VALID,
        sample_count=telemetry_summary.get("total_sample_count", 0),
    )


# ---------------------------------------------------------------------------
# Telemetry summary extractor
# ---------------------------------------------------------------------------


def summarize_telemetry(events: list[Any], session: ChargeSession) -> dict[str, Any]:
    """
    Extract CC-phase statistics from telemetry events for feature computation.

    Returns summary dict with aggregated values needed by feature functions.
    """
    cc_events = [
        e for e in events if e.session_id == session.session_id and e.charger_current_a is not None
    ]

    if not cc_events:
        return {}

    # Use all events as proxy for CC (since we don't have explicit phase in events here)
    currents = [e.charger_current_a for e in cc_events if e.charger_current_a is not None]
    pack_voltages = [e.pack_voltage_v for e in cc_events if e.pack_voltage_v is not None]
    charger_voltages = [e.charger_voltage_v for e in cc_events if e.charger_voltage_v is not None]
    temps = [e.pack_temperature_c for e in cc_events if e.pack_temperature_c is not None]
    socs = [e.soc_pct for e in cc_events if e.soc_pct is not None]
    commanded = [e.commanded_current_a for e in cc_events if e.commanded_current_a is not None]
    ac_voltages = [e.ac_input_voltage_v for e in cc_events if e.ac_input_voltage_v is not None]

    # Cell voltages: use mean across each cell position
    cell_voltage_snapshots = [e.cell_voltages_v for e in cc_events if e.cell_voltages_v]
    mean_cell_voltages = None
    if cell_voltage_snapshots:
        n_cells = len(cell_voltage_snapshots[0])
        mean_cell_voltages = [
            float(np.mean([snap[i] for snap in cell_voltage_snapshots if len(snap) > i]))
            for i in range(n_cells)
        ]

    # OCV estimate: use initial pack voltage at start (low-current approximation)
    ocv_estimate = None
    if pack_voltages and socs:
        initial_idx = 0
        if currents and currents[initial_idx] < 0.5 * np.mean(currents):
            ocv_estimate = pack_voltages[initial_idx]
        else:
            # Use chemistry-based estimate: linear interpolation
            init_soc = socs[0] / 100.0
            if session.chemistry_id == "A-LFP":
                ocv_estimate = 40.0 + init_soc * (54.6 - 40.0)
            else:
                ocv_estimate = 42.0 + init_soc * (58.8 - 42.0)

    summary = {
        "cc_mean_charger_current_a": float(np.mean(currents)) if currents else None,
        "cc_mean_charger_voltage_v": float(np.mean(charger_voltages)) if charger_voltages else None,
        "cc_mean_pack_voltage_v": float(np.mean(pack_voltages)) if pack_voltages else None,
        "cc_commanded_current_a": float(np.mean(commanded)) if commanded else None,
        "final_pack_temperature_c": temps[-1] if temps else None,
        "cc_mean_cell_voltages_v": mean_cell_voltages,
        "mean_ac_input_voltage_v": float(np.mean(ac_voltages)) if ac_voltages else None,
        "ocv_estimate_v": ocv_estimate,
        "cc_sample_count": len(cc_events),
        "total_sample_count": len(cc_events),
        "delivery_ratio": (np.mean(currents) / np.mean(commanded))
        if currents and commanded
        else 1.0,
        "cc_soc_sequence": socs,
        "cc_voltage_sequence": pack_voltages,
        "bms_limit_reason": cc_events[-1].bms_limit_reason if cc_events else None,
    }
    return summary


# ---------------------------------------------------------------------------
# Full feature pipeline for a session
# ---------------------------------------------------------------------------


def compute_all_features(
    session: ChargeSession,
    events: list[Any],
    baselines: dict[str, Any] | None = None,
) -> list[FeatureRecord]:
    """
    Compute all applicable features for a session.
    Returns all records including NOT_COMPUTABLE ones for audit.
    """
    if baselines is None:
        baselines = {}

    summary = summarize_telemetry(events, session)

    features: list[FeatureRecord] = []

    # F-D01
    features.append(compute_dock_cc_current_residual_feature(session, summary))

    # F-D02
    features.append(compute_dock_contact_resistance_feature(session, summary))

    # F-P01
    expected_rise = baselines.get("expected_temp_rise_c", 5.0)
    features.append(compute_pack_thermal_feature(session, summary, expected_rise))

    # F-P02
    expected_pol = baselines.get("expected_polarization_v", 0.8)
    features.append(compute_pack_electrical_feature(session, summary, expected_pol))

    # F-C01
    features.append(compute_cell_dispersion_feature(session, summary))

    # F-C02
    ref_soc = baselines.get("reference_soc_curve", list(range(10, 90, 5)))
    if session.chemistry_id == "A-LFP":
        base_v = 48.0
        ref_v = [base_v + (0.067 * (s - 10)) for s in ref_soc]
    else:
        base_v = 51.8
        ref_v = [base_v + (0.085 * (s - 10)) for s in ref_soc]
    features.append(compute_curve_drift_feature(session, summary, ref_soc, ref_v))

    # F-E01
    baseline_ambient = baselines.get("baseline_ambient_c", 22.0)
    features.append(compute_env_thermal_feature(session, summary, baseline_ambient))

    # F-E02
    features.append(compute_env_grid_sag_feature(session, summary))

    valid_count = sum(1 for f in features if f.validity_status == FeatureValidityStatus.VALID)
    nc_count = sum(1 for f in features if f.validity_status != FeatureValidityStatus.VALID)
    logger.debug(
        "features_computed",
        session_id=session.session_id,
        valid=valid_count,
        not_computable=nc_count,
    )

    return features
