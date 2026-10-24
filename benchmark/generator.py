"""
SwapTrace — Benchmark data generator.

Creates a deterministic semi-synthetic battery-swapping network with:
- 4 stations, 16 docks, 80 packs, 2 chemistry cohorts, 14 days
- ~2,000 charging sessions
- Physically consistent current/voltage/temperature profiles
- 8 fault mechanisms + negative controls

ALL data here is SYNTHETIC. No real Gogoro or private EV data.
Source is clearly labeled SOURCE_TYPE = SYNTHETIC or INJECTED.
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np

from swaptrace.contracts import (
    ChargeSession,
    ChargeStatus,
    DataQualityStatus,
    PhaseInterval,
    SensorCapability,
    SourceType,
    TelemetryEvent,
)
from swaptrace.observability import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Network Topology
# ---------------------------------------------------------------------------

NUM_STATIONS = 4
DOCKS_PER_STATION = 4  # 16 total
PACKS_PER_STATION = 20  # 80 total
COHORTS = ["A-LFP", "B-NMC"]
SIM_DAYS = 14
SAMPLE_INTERVAL_S = 30
SEED = 42

# Chemistry parameters
CHEMISTRY_PARAMS: dict[str, dict[str, float]] = {
    "A-LFP": {
        "nominal_capacity_ah": 20.0,
        "nominal_voltage_v": 48.0,
        "cc_current_a": 15.0,  # 0.75C
        "cv_voltage_v": 54.6,
        "cutoff_voltage_v": 40.0,
        "max_temp_c": 45.0,
        "thermal_mass_j_per_k": 8000.0,
        "internal_resistance_ohm": 0.08,
    },
    "B-NMC": {
        "nominal_capacity_ah": 25.0,
        "nominal_voltage_v": 51.8,
        "cc_current_a": 18.0,  # ~0.72C
        "cv_voltage_v": 58.8,
        "cutoff_voltage_v": 42.0,
        "max_temp_c": 45.0,
        "thermal_mass_j_per_k": 10000.0,
        "internal_resistance_ohm": 0.06,
    },
}


@dataclass
class Pack:
    pack_id: str
    station_id: str
    chemistry_id: str
    equivalent_cycles: float
    rated_capacity_ah: float
    internal_resistance_scale: float = 1.0  # >1 = degraded
    is_faulty: bool = False
    fault_type: str | None = None
    fault_magnitude: float = 0.0


@dataclass
class Dock:
    dock_id: str
    station_id: str
    current_delivery_scale: float = 1.0  # <1 = clipping
    contact_resistance_mohm: float = 5.0  # baseline ~5 mΩ
    is_faulty: bool = False
    fault_type: str | None = None


@dataclass
class Station:
    station_id: str
    ambient_temperature_c: float = 25.0
    ac_voltage_nominal_v: float = 230.0
    thermal_fault_active: bool = False
    grid_sag_active: bool = False


# ---------------------------------------------------------------------------
# Generator class
# ---------------------------------------------------------------------------


class BenchmarkGenerator:
    """Deterministic semi-synthetic network generator."""

    def __init__(self, seed: int = SEED) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)

        # Build topology
        self.stations: dict[str, Station] = {}
        self.docks: dict[str, Dock] = {}
        self.packs: dict[str, Pack] = {}
        self._build_topology()

        # Fault injection state
        self.injected_faults: dict[str, dict[str, Any]] = {}
        self.ground_truth_labels: list[dict[str, Any]] = []

    def _build_topology(self) -> None:
        for s_idx in range(NUM_STATIONS):
            sid = f"STA-{s_idx + 1:02d}"
            self.stations[sid] = Station(
                station_id=sid,
                ambient_temperature_c=22.0 + self.rng.uniform(-3, 3),
                ac_voltage_nominal_v=230.0,
            )
            for d_idx in range(DOCKS_PER_STATION):
                did = f"{sid}-DOK-{d_idx + 1:02d}"
                self.docks[did] = Dock(dock_id=did, station_id=sid)

            for p_idx in range(PACKS_PER_STATION):
                pid = f"{sid}-PCK-{p_idx + 1:03d}"
                chem = COHORTS[p_idx % 2]
                params = CHEMISTRY_PARAMS[chem]
                self.packs[pid] = Pack(
                    pack_id=pid,
                    station_id=sid,
                    chemistry_id=chem,
                    equivalent_cycles=self.rng.uniform(50, 500),
                    rated_capacity_ah=params["nominal_capacity_ah"],
                )

    def inject_faults(self) -> None:
        """Inject the 8 required fault mechanisms."""
        pack_list = list(self.packs.values())
        dock_list = list(self.docks.values())

        # S01 — Dock current clipping (CHARGER_DOCK)
        faulty_dock = dock_list[2]  # deterministic
        faulty_dock.is_faulty = True
        faulty_dock.fault_type = "dock_current_clipping"
        faulty_dock.current_delivery_scale = 0.60  # delivers 60% of commanded
        self.injected_faults["dock_current_clip"] = {
            "entity_id": faulty_dock.dock_id,
            "owner": "CHARGER_DOCK",
            "fault_type": "dock_current_clipping",
            "onset_day": 3,
        }

        # S02 — Dock contact degradation (CHARGER_DOCK)
        faulty_dock2 = dock_list[7]
        faulty_dock2.is_faulty = True
        faulty_dock2.fault_type = "dock_contact_degradation"
        faulty_dock2.contact_resistance_mohm = 80.0  # ~16× normal
        self.injected_faults["dock_contact_deg"] = {
            "entity_id": faulty_dock2.dock_id,
            "owner": "CHARGER_DOCK",
            "fault_type": "dock_contact_degradation",
            "onset_day": 5,
        }

        # S03 — Pack self-heating increase (PACK)
        faulty_pack = pack_list[5]
        faulty_pack.is_faulty = True
        faulty_pack.fault_type = "pack_self_heating"
        faulty_pack.internal_resistance_scale = 2.5  # higher I²R heating
        faulty_pack.fault_magnitude = 2.5
        self.injected_faults["pack_heating"] = {
            "entity_id": faulty_pack.pack_id,
            "owner": "PACK",
            "fault_type": "pack_self_heating",
            "onset_day": 4,
        }

        # S04 — Pack electrical-response change (PACK)
        faulty_pack2 = pack_list[15]
        faulty_pack2.is_faulty = True
        faulty_pack2.fault_type = "pack_electrical_response"
        faulty_pack2.internal_resistance_scale = 3.0
        faulty_pack2.fault_magnitude = 3.0
        self.injected_faults["pack_electrical"] = {
            "entity_id": faulty_pack2.pack_id,
            "owner": "PACK",
            "fault_type": "pack_electrical_response",
            "onset_day": 6,
        }

        # S05 — Cell voltage divergence (CELL_CHEMISTRY)
        faulty_pack3 = pack_list[25]
        faulty_pack3.is_faulty = True
        faulty_pack3.fault_type = "cell_voltage_divergence"
        faulty_pack3.fault_magnitude = 0.15  # 150 mV spread
        self.injected_faults["cell_divergence"] = {
            "entity_id": faulty_pack3.pack_id,
            "owner": "CELL_CHEMISTRY",
            "fault_type": "cell_voltage_divergence",
            "onset_day": 2,
        }

        # S06 — Chemistry/cohort curve drift (CELL_CHEMISTRY)
        faulty_pack4 = pack_list[35]
        faulty_pack4.is_faulty = True
        faulty_pack4.fault_type = "chemistry_curve_drift"
        faulty_pack4.fault_magnitude = 0.12
        self.injected_faults["chem_drift"] = {
            "entity_id": faulty_pack4.pack_id,
            "owner": "CELL_CHEMISTRY",
            "fault_type": "chemistry_curve_drift",
            "onset_day": 7,
        }

        # S07 — Site thermal event (ENVIRONMENT) — affects STA-03
        sta = self.stations["STA-03"]
        sta.thermal_fault_active = True
        sta.ambient_temperature_c = 42.0  # severe heat
        self.injected_faults["site_thermal"] = {
            "entity_id": "STA-03",
            "owner": "ENVIRONMENT",
            "fault_type": "site_thermal_event",
            "onset_day": 8,
        }

        # S08 — Upstream supply sag (ENVIRONMENT) — affects STA-04
        sta2 = self.stations["STA-04"]
        sta2.grid_sag_active = True
        sta2.ac_voltage_nominal_v = 195.0  # sag from 230V
        self.injected_faults["grid_sag"] = {
            "entity_id": "STA-04",
            "owner": "ENVIRONMENT",
            "fault_type": "upstream_supply_sag",
            "onset_day": 10,
        }

        logger.info("fault_injection_complete", faults=list(self.injected_faults.keys()))

    def generate_sessions(self, sim_start: datetime | None = None) -> list[ChargeSession]:
        """Generate ~2,000 charging sessions over 14 days."""
        if sim_start is None:
            sim_start = datetime(2026, 9, 1, 0, 0, 0, tzinfo=UTC)

        sessions: list[ChargeSession] = []
        pack_list = list(self.packs.values())

        # Shuffle pack assignment so packs rotate across docks (crossed design)
        pack_idx = 0
        for day in range(SIM_DAYS):
            day_start = sim_start + timedelta(days=day)
            # Each dock gets ~9 sessions/day → 16 docks × 9 = 144/day × 14 = 2016
            for _, station in self.stations.items():
                sta_docks = [d for d in self.docks.values() if d.station_id == station.station_id]
                # Packs for this station rotate
                sta_packs = [p for p in pack_list if p.station_id == station.station_id]

                for dock in sta_docks:
                    sessions_this_dock = self.rng.randint(7, 10)
                    for sess_i in range(sessions_this_dock):
                        # Rotate packs across docks (the key crossing design)
                        pack = sta_packs[(pack_idx + sess_i * 3) % len(sta_packs)]
                        pack_idx += 1

                        hour_offset = self.rng.uniform(0, 20)
                        sess_start = day_start + timedelta(hours=hour_offset)

                        initial_soc = self.rng.uniform(15, 50)
                        session = self._generate_session(
                            pack=pack,
                            dock=dock,
                            station=station,
                            start_ts=sess_start,
                            initial_soc=initial_soc,
                            day=day,
                        )
                        sessions.append(session)

        logger.info("sessions_generated", count=len(sessions))
        return sessions

    def _generate_session(
        self,
        pack: Pack,
        dock: Dock,
        station: Station,
        start_ts: datetime,
        initial_soc: float,
        day: int,
    ) -> ChargeSession:
        """Generate one charging session with physics-consistent values."""
        params = CHEMISTRY_PARAMS[pack.chemistry_id]

        session_id = (
            f"SES-{start_ts.strftime('%Y%m%d%H%M%S')}-{pack.pack_id[-6:]}-{dock.dock_id[-4:]}"
        )

        # Determine if faults are active on this day
        fault_active_dock = dock.is_faulty and day >= self._fault_onset_day(dock.dock_id)
        fault_active_pack = pack.is_faulty and day >= self._fault_onset_day(pack.pack_id)
        fault_active_env = (
            station.thermal_fault_active or station.grid_sag_active
        ) and day >= self._fault_onset_day(station.station_id)

        # Ambient temperature with noise
        ambient_c = station.ambient_temperature_c + self.np_rng.normal(0, 1.5)

        # Effective CC current (may be clipped by dock fault or grid sag)
        commanded_current = params["cc_current_a"]
        effective_current = commanded_current

        if fault_active_dock and dock.fault_type == "dock_current_clipping":
            effective_current *= dock.current_delivery_scale

        if fault_active_env and station.grid_sag_active:
            # Grid sag reduces available power
            sag_factor = station.ac_voltage_nominal_v / 230.0
            effective_current *= sag_factor

        # Session duration based on SOC delta and effective current
        capacity_ah = pack.rated_capacity_ah
        soc_target = 95.0
        delta_soc = max(0, soc_target - initial_soc) / 100.0
        charge_needed_ah = delta_soc * capacity_ah

        cc_fraction = max(0.3, 1.0 - (soc_target - 80.0) / 100.0)  # rough CC/CV split
        cc_time_s = (charge_needed_ah * cc_fraction) / max(effective_current, 0.1) * 3600
        cv_time_s = charge_needed_ah * (1 - cc_fraction) / max(effective_current * 0.4, 0.01) * 3600
        total_duration_s = cc_time_s + cv_time_s + self.np_rng.normal(0, 60)
        total_duration_s = max(300, total_duration_s)

        end_ts = start_ts + timedelta(seconds=total_duration_s)

        initial_temp_c = ambient_c + self.np_rng.normal(2, 0.5)

        # Integrated charge/energy
        integrated_charge_ah = charge_needed_ah * self.np_rng.normal(1.0, 0.01)
        avg_voltage = (params["nominal_voltage_v"] + params["cv_voltage_v"]) / 2
        integrated_energy_wh = integrated_charge_ah * avg_voltage

        # Phase intervals
        cc_end = start_ts + timedelta(seconds=cc_time_s)
        phases = [
            PhaseInterval(
                phase="CC",
                start_ts=start_ts,
                end_ts=cc_end,
                sample_count=int(cc_time_s / SAMPLE_INTERVAL_S),
            ),
            PhaseInterval(
                phase="CV",
                start_ts=cc_end,
                end_ts=end_ts,
                sample_count=int(cv_time_s / SAMPLE_INTERVAL_S),
            ),
        ]

        # Determine sensor capabilities
        capabilities = [
            SensorCapability.CHARGER_CURRENT.value,
            SensorCapability.CHARGER_VOLTAGE.value,
            SensorCapability.PACK_CURRENT.value,
            SensorCapability.PACK_VOLTAGE.value,
            SensorCapability.PACK_TEMPERATURE.value,
            SensorCapability.SOC.value,
        ]
        # Cell voltage available for ~60% of packs (simulates sensor coverage)
        pack_num = int(pack.pack_id.split("-PCK-")[1])
        if pack_num % 5 != 0:  # 80% have cell voltage
            capabilities.append(SensorCapability.CELL_VOLTAGE.value)
        if station.grid_sag_active:
            capabilities.append(SensorCapability.AC_INPUT_VOLTAGE.value)
        capabilities.append(SensorCapability.AMBIENT_TEMPERATURE.value)

        # Build ground-truth label for evaluation
        self._record_ground_truth(
            session_id=session_id,
            pack=pack,
            dock=dock,
            station=station,
            day=day,
            fault_active_dock=fault_active_dock,
            fault_active_pack=fault_active_pack,
            fault_active_env=fault_active_env,
        )

        session = ChargeSession(
            session_id=session_id,
            pack_id=pack.pack_id,
            dock_id=dock.dock_id,
            station_id=station.station_id,
            chemistry_id=pack.chemistry_id,
            charge_protocol_id=f"CC-CV-{pack.chemistry_id}",
            start_ts=start_ts,
            end_ts=end_ts,
            duration_s=total_duration_s,
            initial_soc_pct=initial_soc,
            final_soc_pct=min(soc_target + self.np_rng.normal(0, 0.5), 100.0),
            initial_pack_temperature_c=initial_temp_c,
            ambient_temperature_c=ambient_c,
            charge_status=ChargeStatus.COMPLETE,
            phase_intervals=phases,
            integrated_charge_ah=integrated_charge_ah,
            integrated_energy_wh=integrated_energy_wh,
            data_quality_status=DataQualityStatus.OK,
            sensor_capabilities=capabilities,
            sample_count=int(total_duration_s / SAMPLE_INTERVAL_S),
            source_type=SourceType.SYNTHETIC,
            source_dataset="swaptrace-benchmark-v1",
        )
        return session

    def _fault_onset_day(self, entity_id: str) -> int:
        """Return the day a fault activates for a given entity."""
        for fault_info in self.injected_faults.values():
            if fault_info["entity_id"] == entity_id:
                return fault_info["onset_day"]
        return 999  # no fault

    def _record_ground_truth(
        self,
        session_id: str,
        pack: Pack,
        dock: Dock,
        station: Station,
        day: int,
        fault_active_dock: bool,
        fault_active_pack: bool,
        fault_active_env: bool,
    ) -> None:
        """Record evaluation ground-truth label — NEVER exposed to model."""
        owners = []
        fault_types = []

        if fault_active_dock:
            owners.append("CHARGER_DOCK")
            fault_types.append(dock.fault_type or "unknown_dock")

        if fault_active_pack:
            owners.append("PACK")
            fault_types.append(pack.fault_type or "unknown_pack")

        if fault_active_env:
            owners.append("ENVIRONMENT")
            if station.thermal_fault_active:
                fault_types.append("site_thermal_event")
            if station.grid_sag_active:
                fault_types.append("upstream_supply_sag")

        # Cell-level fault is stored on specific packs
        if pack.fault_type in ("cell_voltage_divergence", "chemistry_curve_drift"):
            if "CELL_CHEMISTRY" not in owners:
                owners.append("CELL_CHEMISTRY")
            fault_types.append(pack.fault_type)

        label = {
            "session_id": session_id,
            "pack_id": pack.pack_id,
            "dock_id": dock.dock_id,
            "station_id": station.station_id,
            "day": day,
            "is_faulty": len(owners) > 0,
            "true_owners": owners,
            "fault_types": list(set(fault_types)),
            "concurrent_faults": len(owners) > 1,
        }
        self.ground_truth_labels.append(label)

    def generate_telemetry_events(self, sessions: list[ChargeSession]) -> list[TelemetryEvent]:
        """Generate time-series telemetry events for each session."""
        events: list[TelemetryEvent] = []

        for session in sessions:
            pack = self.packs.get(session.pack_id)
            dock = self.docks.get(session.dock_id)
            station = self.stations.get(session.station_id)
            if not (pack and dock and station):
                continue

            params = CHEMISTRY_PARAMS[pack.chemistry_id]
            day = (session.start_ts - datetime(2026, 9, 1, tzinfo=UTC)).days

            fault_active_dock = dock.is_faulty and day >= self._fault_onset_day(dock.dock_id)
            fault_active_pack = pack.is_faulty and day >= self._fault_onset_day(pack.pack_id)
            fault_active_env = (
                station.thermal_fault_active or station.grid_sag_active
            ) and day >= self._fault_onset_day(station.station_id)

            current_ts = session.start_ts
            current_soc = session.initial_soc_pct or 20.0
            current_temp_c = session.initial_pack_temperature_c or 25.0

            commanded_current = params["cc_current_a"]
            effective_current = commanded_current

            if fault_active_dock and dock.fault_type == "dock_current_clipping":
                effective_current *= dock.current_delivery_scale
            if fault_active_env and station.grid_sag_active:
                effective_current *= station.ac_voltage_nominal_v / 230.0

            while current_ts < session.end_ts:
                dt_s = float(SAMPLE_INTERVAL_S)
                remaining_time = (session.end_ts - current_ts).total_seconds()
                if remaining_time < dt_s:
                    dt_s = remaining_time

                # SOC progress
                soc_progress = current_soc / 100.0
                in_cv = soc_progress > 0.80

                if in_cv:
                    actual_current = effective_current * max(0.05, (1.0 - soc_progress) * 5)
                else:
                    actual_current = effective_current + self.np_rng.normal(0, 0.2)

                # Voltage
                ir_scale = 1.0
                if fault_active_pack and pack.fault_type in (
                    "pack_self_heating",
                    "pack_electrical_response",
                ):
                    ir_scale = pack.internal_resistance_scale

                r_effective = params["internal_resistance_ohm"] * ir_scale
                open_circuit_v = (
                    params["cutoff_voltage_v"]
                    + (params["cv_voltage_v"] - params["cutoff_voltage_v"]) * soc_progress
                )
                pack_voltage = (
                    open_circuit_v + actual_current * r_effective + self.np_rng.normal(0, 0.05)
                )

                charger_voltage = pack_voltage
                if fault_active_dock and dock.fault_type == "dock_contact_degradation":
                    contact_drop = (dock.contact_resistance_mohm / 1000.0) * actual_current
                    charger_voltage = pack_voltage + contact_drop

                # Temperature
                heat_power_w = (actual_current**2) * r_effective
                temp_rise_dt = heat_power_w * dt_s / params["thermal_mass_j_per_k"]
                current_temp_c = min(current_temp_c + temp_rise_dt, params["max_temp_c"])

                # SOC update (trapezoidal)
                delta_soc_pct = (
                    (actual_current * dt_s / 3600.0) / params["nominal_capacity_ah"] * 100.0
                )
                current_soc = min(current_soc + delta_soc_pct, 100.0)

                # Cell voltages (when sensor available)
                cell_voltages = None
                if SensorCapability.CELL_VOLTAGE.value in session.sensor_capabilities:
                    n_cells = 14  # typical 48V pack
                    cell_v_nominal = pack_voltage / n_cells
                    spread = 0.002  # normal spread ~2 mV
                    if fault_active_pack and pack.fault_type == "cell_voltage_divergence":
                        spread = pack.fault_magnitude  # 150 mV spread
                    cell_voltages = [
                        cell_v_nominal + self.np_rng.normal(0, spread / 3) for _ in range(n_cells)
                    ]

                # AC voltage
                ac_voltage = None
                if SensorCapability.AC_INPUT_VOLTAGE.value in session.sensor_capabilities:
                    ac_voltage = station.ac_voltage_nominal_v + self.np_rng.normal(0, 2.0)

                event = TelemetryEvent(
                    event_id=str(uuid.uuid4()),
                    event_ts=current_ts,
                    session_id=session.session_id,
                    station_id=session.station_id,
                    dock_id=session.dock_id,
                    pack_id=session.pack_id,
                    charge_protocol_id=session.charge_protocol_id,
                    charger_current_a=float(actual_current),
                    charger_voltage_v=float(charger_voltage),
                    pack_current_a=float(actual_current),
                    pack_voltage_v=float(pack_voltage),
                    pack_temperature_c=float(current_temp_c),
                    soc_pct=float(current_soc),
                    commanded_current_a=float(commanded_current),
                    ambient_temperature_c=float(station.ambient_temperature_c),
                    cell_voltages_v=cell_voltages,
                    ac_input_voltage_v=ac_voltage,
                    chemistry_id=pack.chemistry_id,
                    equivalent_cycles=pack.equivalent_cycles,
                    source_type=SourceType.SYNTHETIC,
                    source_record_id=f"{session.session_id}|t={int(current_ts.timestamp())}",
                )
                events.append(event)

                current_ts += timedelta(seconds=SAMPLE_INTERVAL_S)
                if current_ts >= session.end_ts:
                    break

        logger.info("telemetry_events_generated", count=len(events))
        return events
