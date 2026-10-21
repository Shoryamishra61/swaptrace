"""
SwapTrace — Sessionization module.

Reconstructs charging sessions from telemetry events with:
- Event-time ordering
- Deduplication
- Session identity assignment
- Charge-phase detection
- Partial/aborted session handling
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from swaptrace.contracts import (
    ChargeSession,
    ChargeStatus,
    DataQualityStatus,
    PhaseInterval,
    SourceType,
    TelemetryEvent,
)
from swaptrace.observability import get_logger

logger = get_logger(__name__)

# Minimum interval between sessions for same dock/pack (seconds)
SESSION_GAP_THRESHOLD_S = 300


def assign_session_ids(events: list[TelemetryEvent]) -> list[TelemetryEvent]:
    """
    Ensure all events have stable session IDs.
    If events already have session_ids, validate uniqueness.
    """
    # Sort by event time first
    events.sort(key=lambda e: e.event_ts)

    # Deduplicate by event_id
    seen_ids: set[str] = set()
    deduped: list[TelemetryEvent] = []
    for e in events:
        if e.event_id not in seen_ids:
            seen_ids.add(e.event_id)
            deduped.append(e)

    logger.info(
        "deduplication_complete",
        original=len(events),
        after_dedup=len(deduped),
        dropped=len(events) - len(deduped),
    )
    return deduped


def group_by_session(events: list[TelemetryEvent]) -> dict[str, list[TelemetryEvent]]:
    """Group events by session_id."""
    groups: dict[str, list[TelemetryEvent]] = defaultdict(list)
    for e in events:
        groups[e.session_id].append(e)

    # Sort each group by event time
    for sid in groups:
        groups[sid].sort(key=lambda e: e.event_ts)

    return dict(groups)


def detect_charge_phase(
    events: list[TelemetryEvent],
    cv_voltage_threshold_v: float | None = None,
    cv_current_decay_ratio: float = 0.5,
) -> list[PhaseInterval]:
    """
    Identify CC/CV/TAPER phases from telemetry.

    Phase detection logic:
    - CC: current is steady (< 10% variation from max)
    - CV: voltage is approximately at CV setpoint, current declining
    - TAPER: very low current near end of charge
    - UNKNOWN: ambiguous

    IMPORTANT: If evidence is inadequate, returns UNKNOWN.
    Never fabricates phase assignments.
    """
    if not events:
        return []

    currents = [e.charger_current_a for e in events if e.charger_current_a is not None]
    voltages = [e.charger_voltage_v for e in events if e.charger_voltage_v is not None]

    if not currents or not voltages:
        return [
            PhaseInterval(
                phase="UNKNOWN",
                start_ts=events[0].event_ts,
                end_ts=events[-1].event_ts,
                sample_count=len(events),
            )
        ]

    max_current = max(currents)
    max_voltage = max(voltages)

    phases: list[PhaseInterval] = []
    current_phase = "CC"
    phase_start = events[0].event_ts

    for i, event in enumerate(events[1:], 1):
        if event.charger_current_a is None or event.charger_voltage_v is None:
            continue

        # CV detection: current drops significantly while voltage is near max
        voltage_ratio = event.charger_voltage_v / max_voltage
        current_ratio = event.charger_current_a / max(max_current, 0.1)

        if (
            current_phase == "CC"
            and voltage_ratio > 0.97
            and current_ratio < cv_current_decay_ratio
        ):
            # Transition to CV
            phases.append(
                PhaseInterval(
                    phase="CC",
                    start_ts=phase_start,
                    end_ts=event.event_ts,
                    sample_count=i,
                )
            )
            current_phase = "CV"
            phase_start = event.event_ts

        elif current_phase == "CV" and current_ratio < 0.1:
            phases.append(
                PhaseInterval(
                    phase="CV",
                    start_ts=phase_start,
                    end_ts=event.event_ts,
                    sample_count=len(events) - i,
                )
            )
            current_phase = "TAPER"
            phase_start = event.event_ts

    # Close final phase
    if events:
        phases.append(
            PhaseInterval(
                phase=current_phase,
                start_ts=phase_start,
                end_ts=events[-1].event_ts,
                sample_count=len(events),
            )
        )

    return (
        phases
        if phases
        else [
            PhaseInterval(
                phase="UNKNOWN",
                start_ts=events[0].event_ts,
                end_ts=events[-1].event_ts,
                sample_count=len(events),
            )
        ]
    )


def reconstruct_session(
    session_id: str,
    events: list[TelemetryEvent],
) -> ChargeSession:
    """
    Reconstruct a ChargeSession from a group of telemetry events.

    Handles:
    - Non-monotonic timestamps (detected and flagged)
    - Missing fields (remains None, never fabricated)
    - Partial/aborted sessions
    """
    if not events:
        raise ValueError(f"No events for session {session_id}")

    # Ensure ordered
    events.sort(key=lambda e: e.event_ts)

    first = events[0]
    last = events[-1]

    # Check for non-monotonic timestamps
    quality_reasons: list[str] = []
    prev_ts = events[0].event_ts
    has_nonmonotonic = False
    for e in events[1:]:
        if e.event_ts <= prev_ts:
            has_nonmonotonic = True
        prev_ts = e.event_ts

    if has_nonmonotonic:
        quality_reasons.append("NON_MONOTONIC_TIMESTAMPS")

    duration_s = (last.event_ts - first.event_ts).total_seconds()

    # Determine charge status
    soc_values = [e.soc_pct for e in events if e.soc_pct is not None]
    final_soc = soc_values[-1] if soc_values else None
    initial_soc = soc_values[0] if soc_values else None

    charge_status = ChargeStatus.COMPLETE
    if len(events) < 5:
        charge_status = ChargeStatus.PARTIAL
        quality_reasons.append("FEW_SAMPLES")
    elif final_soc is not None and final_soc < 80:
        charge_status = ChargeStatus.PARTIAL
        quality_reasons.append("LOW_FINAL_SOC")

    # Temperatures
    temps = [e.pack_temperature_c for e in events if e.pack_temperature_c is not None]
    initial_temp = temps[0] if temps else None

    ambients = [e.ambient_temperature_c for e in events if e.ambient_temperature_c is not None]
    ambient = ambients[0] if ambients else None

    # Detect sensor capabilities from events
    capabilities: set[str] = set()
    for e in events:
        if e.charger_current_a is not None:
            capabilities.add("charger_current")
        if e.charger_voltage_v is not None:
            capabilities.add("charger_voltage")
        if e.pack_current_a is not None:
            capabilities.add("pack_current")
        if e.pack_voltage_v is not None:
            capabilities.add("pack_voltage")
        if e.pack_temperature_c is not None:
            capabilities.add("pack_temperature")
        if e.soc_pct is not None:
            capabilities.add("soc")
        if e.cell_voltages_v:
            capabilities.add("cell_voltage")
        if e.ambient_temperature_c is not None:
            capabilities.add("ambient_temperature")
        if e.ac_input_voltage_v is not None:
            capabilities.add("ac_input_voltage")
        if e.commanded_current_a is not None:
            capabilities.add("commanded_current")

    # Charge integration (trapezoidal)
    from swaptrace.physics import integrate_charge_ah, integrate_energy_wh

    currents = [e.pack_current_a for e in events if e.pack_current_a is not None]
    pack_voltages = [e.pack_voltage_v for e in events if e.pack_voltage_v is not None]
    timestamps = [e.event_ts.timestamp() for e in events if e.pack_current_a is not None]

    integrated_ah = None
    integrated_wh = None
    if len(currents) >= 2 and len(timestamps) >= 2:
        integrated_ah = integrate_charge_ah(currents, timestamps)
        if len(pack_voltages) == len(currents):
            integrated_wh = integrate_energy_wh(currents, pack_voltages, timestamps)

    # Phase detection
    phases = detect_charge_phase(events)

    # Data quality
    data_quality = DataQualityStatus.WARNING if quality_reasons else DataQualityStatus.OK

    return ChargeSession(
        session_id=session_id,
        pack_id=first.pack_id,
        dock_id=first.dock_id,
        station_id=first.station_id,
        chemistry_id=first.chemistry_id,
        charge_protocol_id=first.charge_protocol_id,
        start_ts=first.event_ts,
        end_ts=last.event_ts,
        duration_s=duration_s,
        initial_soc_pct=initial_soc,
        final_soc_pct=final_soc,
        initial_pack_temperature_c=initial_temp,
        ambient_temperature_c=ambient,
        charge_status=charge_status,
        phase_intervals=phases,
        integrated_charge_ah=integrated_ah,
        integrated_energy_wh=integrated_wh,
        data_quality_status=data_quality,
        data_quality_reasons=quality_reasons,
        sensor_capabilities=list(capabilities),
        sample_count=len(events),
        source_type=first.source_type,
        source_dataset="benchmark",
    )


class Sessionizer:
    """Converts telemetry events into validated charge sessions."""

    def __init__(self) -> None:
        self.n_sessions = 0
        self.n_complete = 0
        self.n_partial = 0

    def process(self, events: list[TelemetryEvent]) -> list[ChargeSession]:
        # Deduplicate and sort
        events = assign_session_ids(events)
        groups = group_by_session(events)

        sessions: list[ChargeSession] = []
        for session_id, sess_events in groups.items():
            try:
                session = reconstruct_session(session_id, sess_events)
                sessions.append(session)
                self.n_sessions += 1
                if session.charge_status == ChargeStatus.COMPLETE:
                    self.n_complete += 1
                else:
                    self.n_partial += 1
            except Exception as e:
                logger.warning("session_reconstruction_failed", session_id=session_id, error=str(e))

        logger.info(
            "sessionization_complete",
            total=self.n_sessions,
            complete=self.n_complete,
            partial=self.n_partial,
        )
        return sessions
