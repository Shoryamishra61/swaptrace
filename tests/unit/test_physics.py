"""
Unit tests for physics module.

Tests: charge integration, energy integration, feature physics formulas.
Principle: Verify physical correctness, not just that code runs.
"""

from __future__ import annotations

import pytest

from swaptrace.physics import (
    compute_cell_voltage_dispersion,
    compute_contact_resistance,
    compute_curve_drift_score,
    compute_dock_cc_current_residual,
    compute_grid_sag,
    compute_pack_electrical_response,
    compute_pack_thermal_residual,
    integrate_charge_ah,
    integrate_energy_wh,
)

# ─────────────────────────────────────────────────────────────────────────────
# Charge Integration Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_charge_integration_uses_correct_units():
    """10A for 3600s = 10 Ah. Verifies A·s → Ah division by 3600."""
    currents = [10.0, 10.0]
    timestamps = [0.0, 3600.0]
    result = integrate_charge_ah(currents, timestamps)
    assert abs(result - 10.0) < 0.01, f"Expected 10 Ah, got {result}"


def test_charge_integration_zero_for_single_sample():
    """Cannot integrate with fewer than 2 samples."""
    result = integrate_charge_ah([5.0], [0.0])
    assert result == 0.0


def test_irregular_sampling_integrates_correctly():
    """
    Non-uniform intervals should integrate correctly using trapezoidal rule.
    1A for 1800s + 2A for 1800s = 1×0.5Ah + 2×0.5Ah = 1.5Ah
    """
    # t=0: 1A, t=1800: 1A, t=3600: 2A (trapezoidal)
    currents = [1.0, 1.0, 2.0]
    timestamps = [0.0, 1800.0, 3600.0]
    result = integrate_charge_ah(currents, timestamps)
    # Trapezoidal: (1+1)/2 * 1800 + (1+2)/2 * 1800 = 1800 + 2700 = 4500 A·s = 1.25 Ah
    expected = 4500.0 / 3600.0
    assert abs(result - expected) < 0.001


def test_charge_integration_handles_nonmonotonic_timestamps():
    """Non-monotonic (dt<=0) intervals are skipped, not crash."""
    currents = [5.0, 5.0, 5.0]
    timestamps = [0.0, 100.0, 50.0]  # Non-monotonic at end
    # Should not raise; should just skip the bad interval
    result = integrate_charge_ah(currents, timestamps)
    assert result >= 0  # Should be 5A * 100s / 3600 ≈ 0.139 Ah


def test_energy_integration_uses_correct_units():
    """10A at 50V for 3600s = 500Wh."""
    currents = [10.0, 10.0]
    voltages = [50.0, 50.0]
    timestamps = [0.0, 3600.0]
    result = integrate_energy_wh(currents, voltages, timestamps)
    assert abs(result - 500.0) < 0.1


def test_energy_integration_mismatched_arrays_raises():
    """Arrays of different lengths should raise ValueError."""
    with pytest.raises(ValueError):
        integrate_energy_wh([1.0, 2.0], [50.0], [0.0, 1.0])


# ─────────────────────────────────────────────────────────────────────────────
# Feature Physics Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_dock_cc_current_residual_normal():
    """Zero deficit when delivered equals commanded."""
    result = compute_dock_cc_current_residual(15.0, 15.0)
    assert result["valid"] is True
    assert abs(result["deficit_a"]) < 0.001
    assert abs(result["delivery_ratio"] - 1.0) < 0.001


def test_dock_cc_current_residual_clipped():
    """Delivery 60% of commanded → 6A deficit."""
    result = compute_dock_cc_current_residual(15.0, 9.0)
    assert result["valid"] is True
    assert abs(result["deficit_a"] - 6.0) < 0.001
    assert abs(result["delivery_ratio"] - 0.6) < 0.001


def test_dock_cc_current_residual_bms_limited():
    """BMS limit reason is flagged but not suppressed — must be exposed as confounder."""
    result = compute_dock_cc_current_residual(15.0, 8.0, bms_limit_reason="TEMP_DERATE")
    assert result["valid"] is True
    assert result["bms_limited"] is True
    assert result["bms_limit_reason"] == "TEMP_DERATE"
    # Deficit is still reported — BMS limit must be considered by attribution, not hidden
    assert abs(result["deficit_a"] - 7.0) < 0.001


def test_dock_cc_current_residual_zero_commanded():
    """Zero commanded current → invalid (can't compute ratio)."""
    result = compute_dock_cc_current_residual(0.0, 0.0)
    assert result["valid"] is False


def test_contact_resistance_normal_conditions():
    """Small voltage drop at reasonable current → reasonable resistance estimate."""
    # 0.1V drop at 10A = 0.01 Ohm = 10 mΩ
    result = compute_contact_resistance(50.1, 50.0, 10.0)
    assert result["valid"] is True
    assert abs(result["resistance_mohm"] - 10.0) < 0.1


def test_contact_resistance_current_too_low():
    """Current below threshold → NOT_COMPUTABLE (division by zero risk)."""
    result = compute_contact_resistance(50.1, 50.0, 1.0)  # 1A < 2A threshold
    assert result["valid"] is False
    assert "current_too_low" in result["reason"]


def test_contact_resistance_negative_differential():
    """Pack voltage above charger → measurement artifact, not valid."""
    result = compute_contact_resistance(50.0, 50.5, 10.0)
    assert result["valid"] is False
    assert "negative_voltage_differential" in result["reason"]


def test_pack_thermal_residual_normal():
    """Zero residual when measured matches expected."""
    result = compute_pack_thermal_residual(8.0, 8.0)
    assert abs(result["residual_c"]) < 0.001


def test_pack_thermal_residual_elevated():
    """High residual when pack heats more than expected."""
    result = compute_pack_thermal_residual(25.0, 8.0)
    assert result["residual_c"] > 0
    assert abs(result["residual_c"] - 17.0) < 0.001


def test_pack_electrical_response_normal():
    """Valid polarization when current is sufficient."""
    result = compute_pack_electrical_response(52.0, 50.0, 15.0)
    assert result["valid"] is True
    assert result["polarization_v"] > 0
    assert "not true DCIR" in result["note"]  # Honesty check


def test_pack_electrical_response_low_current():
    """Current too low for polarization proxy."""
    result = compute_pack_electrical_response(52.0, 50.0, 0.3)
    assert result["valid"] is False


def test_cell_voltage_dispersion_normal():
    """Tight cells → small spread."""
    cells = [3.65 + 0.001 * i for i in range(14)]
    result = compute_cell_voltage_dispersion(cells)
    assert result["valid"] is True
    assert result["spread_v"] < 0.05


def test_cell_voltage_dispersion_high():
    """Divergent cell → large spread."""
    cells = [3.65] * 13 + [3.30]  # one low cell
    result = compute_cell_voltage_dispersion(cells)
    assert result["valid"] is True
    assert result["spread_v"] > 0.3


def test_cell_voltage_dispersion_insufficient_cells():
    """Too few cells → NOT_COMPUTABLE."""
    result = compute_cell_voltage_dispersion([3.65, 3.64])
    assert result["valid"] is False
    assert "insufficient_cells" in result["reason"]


def test_curve_drift_score_no_drift():
    """Same curve → near-zero drift."""
    soc = list(range(20, 90, 5))
    voltage = [48.0 + i * 0.05 for i in range(len(soc))]
    result = compute_curve_drift_score(soc, voltage, soc, voltage)
    assert result["valid"] is True
    assert result["curve_mad_v"] < 0.001


def test_curve_drift_score_significant_drift():
    """Shifted curve → detectable drift."""
    soc = list(range(20, 90, 5))
    voltage_ref = [48.0 + i * 0.05 for i in range(len(soc))]
    voltage_shifted = [v + 0.3 for v in voltage_ref]  # 300 mV shift
    result = compute_curve_drift_score(soc, voltage_shifted, soc, voltage_ref)
    assert result["valid"] is True
    assert result["curve_mad_v"] > 0.1


def test_curve_drift_insufficient_soc_overlap():
    """No SOC overlap → NOT_COMPUTABLE."""
    soc_a = list(range(10, 40, 5))
    soc_b = list(range(60, 90, 5))
    voltage = [48.0] * len(soc_a)
    voltage_b = [50.0] * len(soc_b)
    result = compute_curve_drift_score(soc_a, voltage, soc_b, voltage_b)
    assert result["valid"] is False


def test_grid_sag_detected():
    """Supply below nominal → sag detected."""
    result = compute_grid_sag(205.0, nominal_ac_voltage_v=230.0)
    assert result["valid"] is True
    assert result["sag_pct"] > 10.0
    assert result["is_sagging"] is True


def test_grid_sag_normal():
    """Nominal voltage → no sag."""
    result = compute_grid_sag(230.0, nominal_ac_voltage_v=230.0)
    assert result["valid"] is True
    assert result["is_sagging"] is False
    assert result["sag_v"] < 1.0
