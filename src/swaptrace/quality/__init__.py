"""
SwapTrace — Quality validation module.

Validates telemetry events and sessions. Quarantines invalid records
with machine-readable reasons. Does NOT silently fabricate values.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from swaptrace.contracts import (
    ChargeSession,
    DataQualityStatus,
    TelemetryEvent,
)
from swaptrace.observability import get_logger

logger = get_logger(__name__)

# Physical bounds for sensor validity
BOUNDS: dict[str, tuple[float, float]] = {
    "charger_current_a": (0.0, 250.0),
    "charger_voltage_v": (0.0, 120.0),  # 48V pack; charger up to ~60V
    "pack_current_a": (-10.0, 250.0),  # small negative allowed for BMS regen
    "pack_voltage_v": (30.0, 70.0),
    "pack_temperature_c": (-20.0, 80.0),
    "soc_pct": (0.0, 100.0),
    "ambient_temperature_c": (-30.0, 60.0),
    "ac_input_voltage_v": (80.0, 280.0),
    "commanded_current_a": (0.0, 250.0),
}


@dataclass
class ValidationResult:
    is_valid: bool
    reasons: list[str]
    quarantine_level: str  # "WARN" or "REJECT"


def validate_telemetry_event(event: TelemetryEvent) -> ValidationResult:
    """
    Validate a single telemetry event.
    Returns ValidationResult with reasons for any issues found.

    IMPORTANT: Invalid events are quarantined — not silently dropped or fixed.
    Data corruption must NOT be relabeled as equipment anomalies.
    """
    reasons: list[str] = []
    quarantine_level = "WARN"

    # Required identifiers
    for field_name in ["session_id", "station_id", "dock_id", "pack_id"]:
        val = getattr(event, field_name, None)
        if not val or not str(val).strip():
            reasons.append(f"MISSING_IDENTIFIER:{field_name}")
            quarantine_level = "REJECT"

    # Timestamp validation
    if event.event_ts is None:
        reasons.append("MISSING_TIMESTAMP:event_ts")
        quarantine_level = "REJECT"

    # Numeric range validation
    for field_name, (lo, hi) in BOUNDS.items():
        val = getattr(event, field_name, None)
        if val is not None and not (lo <= val <= hi):
            reasons.append(f"OUT_OF_RANGE:{field_name}={val:.3f},[{lo},{hi}]")
            if field_name in ("pack_temperature_c", "soc_pct"):
                quarantine_level = "REJECT"
            else:
                quarantine_level = max(
                    quarantine_level, "WARN", key=lambda x: {"WARN": 0, "REJECT": 1}.get(x, 0)
                )

    # Physical consistency: if pack_voltage < cutoff → suspect
    if event.pack_voltage_v is not None and event.pack_voltage_v < 30.0:
        reasons.append(f"PHYSICS_VIOLATION:pack_voltage_below_cutoff={event.pack_voltage_v:.2f}V")
        quarantine_level = "REJECT"

    # Cell voltage array bounds
    if event.cell_voltages_v is not None:
        for i, cv in enumerate(event.cell_voltages_v):
            if not (2.0 <= cv <= 4.5):
                reasons.append(f"OUT_OF_RANGE:cell_voltage[{i}]={cv:.3f}")

    return ValidationResult(
        is_valid=quarantine_level != "REJECT",
        reasons=reasons,
        quarantine_level=quarantine_level,
    )


def validate_session(session: ChargeSession) -> ValidationResult:
    """Validate a reconstructed charge session for feature eligibility."""
    reasons: list[str] = []
    quarantine_level = "WARN"

    if session.charge_status.value in ("ABORTED", "QUALITY_REJECTED"):
        reasons.append(f"SESSION_STATUS:{session.charge_status.value}")
        quarantine_level = "REJECT"

    if session.sample_count < 5:
        reasons.append(f"INSUFFICIENT_SAMPLES:{session.sample_count}")
        quarantine_level = "REJECT"

    if session.duration_s < 60:
        reasons.append(f"SESSION_TOO_SHORT:{session.duration_s:.0f}s")
        quarantine_level = "REJECT"

    if session.integrated_charge_ah is not None and session.integrated_charge_ah < 0:
        reasons.append(f"NEGATIVE_INTEGRATED_CHARGE:{session.integrated_charge_ah:.3f}Ah")
        quarantine_level = "REJECT"

    # SOC sanity
    if (
        session.initial_soc_pct is not None
        and session.final_soc_pct is not None
        and session.final_soc_pct < session.initial_soc_pct - 5.0
    ):  # allow small measurement noise
            reasons.append(
                f"SOC_REGRESSION:init={session.initial_soc_pct:.1f}%,final={session.final_soc_pct:.1f}%"
            )

    return ValidationResult(
        is_valid=quarantine_level != "REJECT",
        reasons=reasons,
        quarantine_level=quarantine_level,
    )


def check_sensor_capability(session: ChargeSession, required: list[str]) -> tuple[bool, list[str]]:
    """
    Check if a session has all required sensor capabilities.
    Returns (available, missing_sensors).

    Missing required sensors → NOT_COMPUTABLE, not fabricated zero.
    """
    available = set(session.sensor_capabilities)
    missing = [s for s in required if s not in available]
    return len(missing) == 0, missing


class QualityPipeline:
    """Runs all validation steps and tracks counts."""

    def __init__(self) -> None:
        self.n_events_in = 0
        self.n_events_ok = 0
        self.n_events_warn = 0
        self.n_events_reject = 0
        self.quarantine_log: list[dict[str, Any]] = []

    def process_events(self, events: list[TelemetryEvent]) -> list[TelemetryEvent]:
        """Validate events; return only valid/warning events. Reject quarantined."""
        valid_events: list[TelemetryEvent] = []
        for event in events:
            self.n_events_in += 1
            result = validate_telemetry_event(event)
            if result.quarantine_level == "REJECT":
                self.n_events_reject += 1
                self.quarantine_log.append(
                    {
                        "event_id": event.event_id,
                        "session_id": event.session_id,
                        "reasons": result.reasons,
                        "level": "REJECT",
                    }
                )
            elif result.reasons:
                self.n_events_warn += 1
                valid_events.append(event)
            else:
                self.n_events_ok += 1
                valid_events.append(event)

        logger.info(
            "event_validation_complete",
            total=self.n_events_in,
            ok=self.n_events_ok,
            warn=self.n_events_warn,
            reject=self.n_events_reject,
        )
        return valid_events

    def process_sessions(self, sessions: list[ChargeSession]) -> list[ChargeSession]:
        """Validate sessions; mark rejected but return all for audit."""
        eligible: list[ChargeSession] = []
        for session in sessions:
            result = validate_session(session)
            if not result.is_valid:
                session.data_quality_status = DataQualityStatus.REJECTED
                session.data_quality_reasons.extend(result.reasons)
            elif result.reasons:
                session.data_quality_status = DataQualityStatus.WARNING
                session.data_quality_reasons.extend(result.reasons)
                eligible.append(session)
            else:
                eligible.append(session)
        return eligible
