"""
SwapTrace — Physics module.

Implements physically valid feature calculations with:
- Correct units
- Valid measurement boundaries
- Sampling-rate-aware integration
- Known confounder documentation

NEVER fabricates values when sensors are unavailable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Charge integration (trapezoidal rule)
# ---------------------------------------------------------------------------


def integrate_charge_ah(
    currents_a: list[float],
    timestamps_s: list[float],
) -> float:
    """
    Compute charge throughput using trapezoidal integration.

    Q_Ah = (1/3600) * Σ (I_i + I_{i+1})/2 * Δt_i

    Units: A * s → Ah (divide by 3600)
    Sign convention: positive current = charging.
    Handles irregular sampling correctly.

    Args:
        currents_a: Measured current in amperes (positive = charging).
        timestamps_s: Measurement timestamps as POSIX seconds (monotonic, UTC).

    Returns:
        Integrated charge in Ah.
    """
    if len(currents_a) < 2 or len(timestamps_s) < 2:
        return 0.0
    if len(currents_a) != len(timestamps_s):
        raise ValueError("currents_a and timestamps_s must be same length")

    total_as = 0.0
    for i in range(len(currents_a) - 1):
        dt = timestamps_s[i + 1] - timestamps_s[i]
        if dt <= 0:
            continue  # skip non-monotonic gaps
        avg_current = (currents_a[i] + currents_a[i + 1]) / 2.0
        total_as += avg_current * dt

    return total_as / 3600.0  # A·s → Ah


def integrate_energy_wh(
    currents_a: list[float],
    voltages_v: list[float],
    timestamps_s: list[float],
) -> float:
    """
    Compute energy throughput using trapezoidal integration.

    E_Wh = (1/3600) * Σ P_i_avg * Δt_i
    where P_i_avg = (P_i + P_{i+1})/2

    Units: W * s → Wh (divide by 3600)
    """
    if len(currents_a) < 2:
        return 0.0
    if not (len(currents_a) == len(voltages_v) == len(timestamps_s)):
        raise ValueError("All input arrays must be same length")

    powers_w = [c * v for c, v in zip(currents_a, voltages_v)]
    total_ws = 0.0
    for i in range(len(powers_w) - 1):
        dt = timestamps_s[i + 1] - timestamps_s[i]
        if dt <= 0:
            continue
        avg_power = (powers_w[i] + powers_w[i + 1]) / 2.0
        total_ws += avg_power * dt

    return total_ws / 3600.0  # W·s → Wh


# ---------------------------------------------------------------------------
# F-D01: Dock current-control residual
# ---------------------------------------------------------------------------


def compute_dock_cc_current_residual(
    commanded_current_a: float,
    delivered_current_a: float,
    bms_limit_reason: str | None = None,
) -> dict[str, Any]:
    """
    Compute residual between commanded and delivered CC current.

    Owner: CHARGER_DOCK
    Unit: A (absolute deficit) and ratio (dimensionless)

    IMPORTANT: If bms_limit_reason is set, the reduced current may be
    a legitimate BMS limit — NOT a dock failure. This must be flagged
    as a confounder, not suppressed.

    Args:
        commanded_current_a: Target CC current from protocol.
        delivered_current_a: Measured delivered current.
        bms_limit_reason: BMS-reported limit code, if any.

    Returns:
        dict with deficit_a, ratio, bms_limited flag.
    """
    if commanded_current_a <= 0:
        return {"valid": False, "reason": "commanded_current_zero_or_negative"}

    deficit_a = commanded_current_a - delivered_current_a
    ratio = delivered_current_a / commanded_current_a

    bms_limited = bms_limit_reason is not None and bms_limit_reason.strip() != ""

    return {
        "valid": True,
        "deficit_a": deficit_a,
        "delivery_ratio": ratio,
        "bms_limited": bms_limited,
        "bms_limit_reason": bms_limit_reason,
        "confounders": ["bms_current_limit", "low_soc_startup", "temperature_derating"],
    }


# ---------------------------------------------------------------------------
# F-D02: Dock contact resistance excess
# ---------------------------------------------------------------------------


def compute_contact_resistance(
    charger_voltage_v: float,
    pack_voltage_v: float,
    current_a: float,
    min_current_threshold_a: float = 2.0,
) -> dict[str, Any]:
    """
    Estimate contact-path resistance from synchronized voltage difference.

    R_contact = (V_charger - V_pack) / I

    IMPORTANT constraints:
    - Both voltages must refer to known electrical boundaries.
    - Timestamps must be aligned (same sample).
    - Current must be sufficiently nonzero (> min_current_threshold_a).
    - This is a proxy for the contact path — cannot distinguish
      cable, connector, or BMS sense error without additional evidence.

    Owner: CHARGER_DOCK
    Unit: Ohms (typically expect 1–50 mΩ range)

    Returns NOT_COMPUTABLE if current is too low (division by zero risk).
    """
    if current_a < min_current_threshold_a:
        return {
            "valid": False,
            "reason": f"current_too_low:{current_a:.2f}A < threshold:{min_current_threshold_a}A",
        }

    v_diff = charger_voltage_v - pack_voltage_v
    if v_diff < 0:
        # Pack voltage above charger — measurement artifact or regeneration
        return {
            "valid": False,
            "reason": f"negative_voltage_differential:{v_diff:.3f}V",
        }

    r_ohm = v_diff / current_a
    r_mohm = r_ohm * 1000.0

    return {
        "valid": True,
        "resistance_ohm": r_ohm,
        "resistance_mohm": r_mohm,
        "v_diff_v": v_diff,
        "current_a": current_a,
        "confounders": [
            "measurement_alignment",
            "sensor_offset",
            "cable_resistance",
            "bms_internal_resistance",
        ],
    }


# ---------------------------------------------------------------------------
# F-P01: Pack thermal residual
# ---------------------------------------------------------------------------


def compute_pack_thermal_residual(
    measured_temp_rise_c: float,
    expected_temp_rise_c: float,
) -> dict[str, Any]:
    """
    Compute residual between measured and expected temperature rise.

    Expected rise must be conditioned on:
    - Charge current (I²R heating)
    - Initial temperature
    - Ambient temperature
    - Charge duration
    - Chemistry / thermal mass

    Owner: PACK
    Unit: °C

    IMPORTANT: A hot pack is NOT automatically defective.
    Confounders: ambient temperature, initial temp, high current charging,
    BMS derate creating longer session, seasonal variation.
    """
    residual_c = measured_temp_rise_c - expected_temp_rise_c
    return {
        "valid": True,
        "residual_c": residual_c,
        "measured_temp_rise_c": measured_temp_rise_c,
        "expected_temp_rise_c": expected_temp_rise_c,
        "confounders": [
            "ambient_temperature",
            "initial_pack_temperature",
            "charge_current",
            "session_duration",
            "thermal_mass",
        ],
    }


# ---------------------------------------------------------------------------
# F-P02: Pack electrical response / polarization proxy
# ---------------------------------------------------------------------------


def compute_pack_electrical_response(
    pack_voltage_v: float,
    open_circuit_voltage_v: float,
    current_a: float,
) -> dict[str, Any]:
    """
    Estimate pack polarization (IR drop proxy) from voltage response.

    polarization_v = OCV - V_pack (during charging: should be V_pack > OCV due to overvoltage)
    During CC charging: V_terminal = OCV + I * R_int (charger side)

    IMPORTANT: This is a proxy — NOT true DC internal resistance measurement.
    True DCIR requires a controlled current step with aligned measurements.
    Do NOT report this as confirmed internal resistance without that protocol.

    Owner: PACK
    Unit: V (polarization), implied Ω (ratio)
    """
    if current_a < 0.5:
        return {"valid": False, "reason": "current_too_low_for_polarization_proxy"}

    # During charging: terminal > OCV
    polarization_v = pack_voltage_v - open_circuit_voltage_v
    r_proxy_ohm = polarization_v / current_a if current_a > 0 else None

    return {
        "valid": True,
        "polarization_v": polarization_v,
        "r_proxy_ohm": r_proxy_ohm,
        "current_a": current_a,
        "note": "Proxy measure — not true DCIR. Requires controlled excitation for confirmation.",
        "confounders": ["soc_hysteresis", "temperature", "aging", "cell_balancing"],
    }


# ---------------------------------------------------------------------------
# F-C01: Cell voltage dispersion
# ---------------------------------------------------------------------------


def compute_cell_voltage_dispersion(
    cell_voltages_v: list[float],
    min_cells: int = 6,
) -> dict[str, Any]:
    """
    Compute cell-to-peer voltage dispersion (spread) at comparable SOC.

    dispersion_v = max(cells) - min(cells) [range]
    also: std_dev for distribution shape

    Owner: CELL_CHEMISTRY
    Unit: V

    IMPORTANT: Dispersion can result from:
    - Imbalance (normal aging pattern)
    - Sensor offset or failure
    - Cell variation (manufacturing)
    - Electrochemical degradation

    Route to cell engineering; do NOT claim proven chemistry failure.
    Requires cell voltage sensor — NOT_COMPUTABLE otherwise.
    """
    if len(cell_voltages_v) < min_cells:
        return {
            "valid": False,
            "reason": f"insufficient_cells:{len(cell_voltages_v)}<{min_cells}",
        }

    arr = np.array(cell_voltages_v)
    spread_v = float(np.max(arr) - np.min(arr))
    std_v = float(np.std(arr))
    iqr_v = float(np.percentile(arr, 75) - np.percentile(arr, 25))

    return {
        "valid": True,
        "spread_v": spread_v,
        "std_v": std_v,
        "iqr_v": iqr_v,
        "n_cells": len(cell_voltages_v),
        "min_cell_v": float(np.min(arr)),
        "max_cell_v": float(np.max(arr)),
        "confounders": ["sensor_offset", "imbalance", "soc_nonuniformity", "temperature_gradient"],
    }


# ---------------------------------------------------------------------------
# F-C02: Chemistry/cohort charge curve drift
# ---------------------------------------------------------------------------


def compute_curve_drift_score(
    session_soc_sequence: list[float],
    session_voltage_sequence: list[float],
    reference_soc_sequence: list[float],
    reference_voltage_sequence: list[float],
    interp_points: int = 20,
) -> dict[str, Any]:
    """
    Compute charge curve drift against cohort reference.

    Interpolates both curves onto common SOC grid and computes
    mean absolute deviation in voltage space.

    Owner: CELL_CHEMISTRY
    Unit: V (MAD on interpolated voltage)

    IMPORTANT: Requires compatible protocol (same chemistry, same CC current).
    Different protocols invalidate the comparison. Reference cohort must
    be from same chemistry_id and comparable age bracket.
    """
    if len(session_soc_sequence) < 5 or len(reference_soc_sequence) < 5:
        return {"valid": False, "reason": "insufficient_curve_points"}

    # Common SOC grid in overlapping range
    soc_lo = max(min(session_soc_sequence), min(reference_soc_sequence))
    soc_hi = min(max(session_soc_sequence), max(reference_soc_sequence))

    if soc_hi - soc_lo < 10:
        return {"valid": False, "reason": f"insufficient_soc_overlap:{soc_hi - soc_lo:.1f}%"}

    soc_grid = np.linspace(soc_lo, soc_hi, interp_points)

    # Interpolate session curve
    try:
        sess_v_interp = np.interp(soc_grid, session_soc_sequence, session_voltage_sequence)
        ref_v_interp = np.interp(soc_grid, reference_soc_sequence, reference_voltage_sequence)
    except Exception as e:
        return {"valid": False, "reason": f"interpolation_failed:{e}"}

    diff = sess_v_interp - ref_v_interp
    mad_v = float(np.mean(np.abs(diff)))
    max_dev_v = float(np.max(np.abs(diff)))

    return {
        "valid": True,
        "curve_mad_v": mad_v,
        "curve_max_deviation_v": max_dev_v,
        "soc_coverage_pct": soc_hi - soc_lo,
        "n_interp_points": interp_points,
        "confounders": [
            "charging_protocol_mismatch",
            "temperature_difference",
            "age_bracket_mismatch",
            "sampling_rate",
        ],
    }


# ---------------------------------------------------------------------------
# F-E01: Site-wide thermal derating
# ---------------------------------------------------------------------------


def compute_site_thermal_deviation(
    ambient_temperature_c: float,
    baseline_ambient_c: float,
    observed_charge_reduction_factor: float,
    expected_reduction_at_temp: float,
) -> dict[str, Any]:
    """
    Assess whether a site-wide performance reduction is consistent with
    measured thermal conditions.

    Owner: ENVIRONMENT
    Unit: dimensionless (reduction factor)

    IMPORTANT: Cannot attribute to ENVIRONMENT without measured ambient.
    A shared upstream hardware fault (e.g., PDU failure) can produce
    identical symptoms — abstain if no thermal sensor supports the hypothesis.
    """
    thermal_excess_c = ambient_temperature_c - baseline_ambient_c
    reduction_excess = observed_charge_reduction_factor - expected_reduction_at_temp

    return {
        "valid": True,
        "thermal_excess_c": thermal_excess_c,
        "observed_reduction_factor": observed_charge_reduction_factor,
        "expected_reduction_factor": expected_reduction_at_temp,
        "reduction_excess": reduction_excess,
        "confounders": ["shared_pdu_fault", "hvac_failure", "seasonal_ambient"],
    }


# ---------------------------------------------------------------------------
# F-E02: Upstream supply sag
# ---------------------------------------------------------------------------


def compute_grid_sag(
    ac_input_voltage_v: float,
    nominal_ac_voltage_v: float = 230.0,
    sag_threshold_pct: float = 10.0,
) -> dict[str, Any]:
    """
    Detect AC supply voltage sag below nominal threshold.

    Owner: ENVIRONMENT
    Unit: V, %

    IMPORTANT: Without AC input telemetry, do NOT claim grid-sag diagnosis.
    Requires ac_input_voltage sensor capability.
    """
    sag_v = nominal_ac_voltage_v - ac_input_voltage_v
    sag_pct = (sag_v / nominal_ac_voltage_v) * 100.0
    is_sagging = sag_pct >= sag_threshold_pct

    return {
        "valid": True,
        "sag_v": sag_v,
        "sag_pct": sag_pct,
        "is_sagging": is_sagging,
        "nominal_v": nominal_ac_voltage_v,
        "measured_v": ac_input_voltage_v,
        "confounders": ["local_load_variation", "meter_calibration", "phase_imbalance"],
    }
