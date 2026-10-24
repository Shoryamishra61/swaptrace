"""
SwapTrace — Attribution module.

Pack–dock bipartite graph + cross-asset peer contrast attribution.

Determines whether an anomaly follows a DOCK, a PACK, cell/chemistry
evidence, or a measured environmental condition.

CRITICAL: Only emits an owner attribution when evidence is sufficient.
Returns INSUFFICIENT_EVIDENCE when crossing is inadequate.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import polars as pl

from swaptrace.contracts import (
    AttributionResult,
    AttributionStatus,
    EvidenceItem,
    FeatureRecord,
    FeatureValidityStatus,
    OwnerCategory,
)
from swaptrace.observability import get_logger

logger = get_logger(__name__)

# Feature → ownership category mapping
FEATURE_OWNER_MAP: dict[str, OwnerCategory] = {
    "dock_cc_current_control_residual": OwnerCategory.CHARGER_DOCK,
    "dock_contact_resistance_excess": OwnerCategory.CHARGER_DOCK,
    "pack_self_heating_excess": OwnerCategory.PACK,
    "pack_electrical_response_anomaly": OwnerCategory.PACK,
    "cell_voltage_dispersion_excess": OwnerCategory.CELL_CHEMISTRY,
    "chemistry_charge_curve_drift": OwnerCategory.CELL_CHEMISTRY,
    "env_sitewide_heat_derate": OwnerCategory.ENVIRONMENT,
    "env_grid_sag_power_loss": OwnerCategory.ENVIRONMENT,
}

# Minimum independent assets required for each owner hypothesis
MIN_INDEPENDENT_PACKS_FOR_DOCK = 2  # dock hypothesis: 2+ distinct packs
MIN_INDEPENDENT_DOCKS_FOR_PACK = 2  # pack hypothesis: 2+ distinct docks
MIN_PACKS_FOR_ENVIRONMENT = 3  # environment: 3+ distinct packs/docks


class PackDockGraph:
    """
    Bipartite graph of observed pack–dock relationships.

    Tracks which packs have visited which docks and whether each session
    was anomalous per feature.
    """

    def __init__(self) -> None:
        # pack_id → set of dock_ids visited
        self.pack_to_docks: dict[str, set[str]] = defaultdict(set)
        # dock_id → set of pack_ids visited
        self.dock_to_packs: dict[str, set[str]] = defaultdict(set)
        # dock_id → station_id
        self.dock_station: dict[str, str] = {}
        # (pack_id, dock_id) → list of session_ids
        self.crossing_sessions: dict[tuple[str, str], list[str]] = defaultdict(list)
        # (entity_id, feature_id) → list of (session_id, score)
        self.anomaly_registry: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    def add_session(
        self,
        session_id: str,
        pack_id: str,
        dock_id: str,
        station_id: str,
    ) -> None:
        self.pack_to_docks[pack_id].add(dock_id)
        self.dock_to_packs[dock_id].add(pack_id)
        self.dock_station[dock_id] = station_id
        self.crossing_sessions[(pack_id, dock_id)].append(session_id)

    def add_anomaly(
        self,
        entity_id: str,
        feature_id: str,
        session_id: str,
        score: float,
    ) -> None:
        self.anomaly_registry[(entity_id, feature_id)].append(
            {
                "session_id": session_id,
                "score": score,
            }
        )

    def get_independent_docks_for_pack(self, pack_id: str) -> set[str]:
        """Return all docks where this pack has been observed."""
        return self.pack_to_docks.get(pack_id, set())

    def get_independent_packs_for_dock(self, dock_id: str) -> set[str]:
        """Return all packs that have charged at this dock."""
        return self.dock_to_packs.get(dock_id, set())

    def get_sibling_docks(self, dock_id: str) -> set[str]:
        """Return other docks at the same station."""
        station = self.dock_station.get(dock_id)
        if not station:
            return set()
        return {d for d, s in self.dock_station.items() if s == station and d != dock_id}

    def pack_crossing_count(self, pack_id: str) -> int:
        return len(self.pack_to_docks.get(pack_id, set()))

    def dock_crossing_count(self, dock_id: str) -> int:
        return len(self.dock_to_packs.get(dock_id, set()))

    def session_pack_map(self) -> dict[str, str]:
        """Map session_id → pack_id for every observed crossing."""
        return {
            sid: pack for (pack, _dock), sids in self.crossing_sessions.items() for sid in sids
        }

    def dock_anomaly_packs(
        self,
        dock_id: str,
        feature_id: str,
        session_pack: dict[str, str],
    ) -> set[str]:
        """Packs that owned sessions in which a dock-feature anomaly fired at this dock."""
        return {
            session_pack[rec["session_id"]]
            for rec in self.anomaly_registry.get((dock_id, feature_id), [])
            if rec["session_id"] in session_pack
        }

    def pack_has_dock_anomaly(
        self,
        pack_id: str,
        dock_id: str,
        feature_id: str,
        session_pack: dict[str, str],
    ) -> bool:
        """True if a dock-feature anomaly at dock_id occurred in a session owned by pack_id."""
        return any(
            session_pack.get(rec["session_id"]) == pack_id
            for rec in self.anomaly_registry.get((dock_id, feature_id), [])
        )


def attribute_session(
    session_id: str,
    pack_id: str,
    dock_id: str,
    station_id: str,
    anomalous_features: list[FeatureRecord],
    graph: PackDockGraph,
    all_features_df: pl.DataFrame | None = None,
) -> AttributionResult:
    """
    Perform cross-asset attribution for a single anomalous session.

    Attribution logic:
    1. Check pack crossing: does the pack show anomalies on other docks too?
    2. Check dock crossing: do other packs show anomalies at this dock?
    3. Check cell/chemistry features (direct evidence, no crossing needed)
    4. Check environment: multiple independent assets at same station
    5. Insufficient evidence if crossing is inadequate

    Returns AttributionResult with selected owner or INSUFFICIENT_EVIDENCE.
    """
    evidence: dict[str, list[EvidenceItem]] = defaultdict(list)
    counterevidence: dict[str, list[EvidenceItem]] = defaultdict(list)
    crossing_support: dict[str, int] = {}

    # Categorize anomalous features by owner
    dock_features = [
        f
        for f in anomalous_features
        if FEATURE_OWNER_MAP.get(f.feature_id) == OwnerCategory.CHARGER_DOCK
    ]
    pack_features = [
        f for f in anomalous_features if FEATURE_OWNER_MAP.get(f.feature_id) == OwnerCategory.PACK
    ]
    cell_features = [
        f
        for f in anomalous_features
        if FEATURE_OWNER_MAP.get(f.feature_id) == OwnerCategory.CELL_CHEMISTRY
    ]
    env_features = [
        f
        for f in anomalous_features
        if FEATURE_OWNER_MAP.get(f.feature_id) == OwnerCategory.ENVIRONMENT
    ]

    selected_owner: OwnerCategory | None = None
    status = AttributionStatus.INSUFFICIENT_EVIDENCE
    confidence = "LOW"
    explanation_parts: list[str] = []

    # --- CHARGER_DOCK hypothesis ---
    if dock_features:
        # Check: do other packs show anomalies at this same dock?
        packs_at_dock = graph.get_independent_packs_for_dock(dock_id)
        other_packs_at_dock = packs_at_dock - {pack_id}
        dock_crossing = graph.dock_crossing_count(dock_id)
        crossing_support["dock_independent_packs"] = dock_crossing

        # Check anomaly registry for other packs at this dock
        session_pack = graph.session_pack_map()
        anomalous_other_packs: set[str] = set()
        for fid in [f.feature_id for f in dock_features]:
            anomalous_other_packs |= graph.dock_anomaly_packs(dock_id, fid, session_pack) - {pack_id}

        # Check: does this pack behave normally elsewhere?
        pack_other_docks = graph.get_independent_docks_for_pack(pack_id) - {dock_id}
        pack_anomalous_elsewhere = False
        for other_dock in pack_other_docks:
            for fid in [f.feature_id for f in dock_features]:
                if graph.pack_has_dock_anomaly(pack_id, other_dock, fid, session_pack):
                    pack_anomalous_elsewhere = True
                    break

        # Sibling dock check: are sibling docks normal?
        sibling_docks = graph.get_sibling_docks(dock_id)
        sibling_anomalous = False
        for sib in sibling_docks:
            for fid in [f.feature_id for f in dock_features]:
                if graph.anomaly_registry.get((sib, fid)):
                    sibling_anomalous = True

        crossing_support["dock_peer_packs_available"] = len(other_packs_at_dock)
        crossing_support["dock_anomalous_peer_packs"] = len(anomalous_other_packs)

        if dock_crossing >= MIN_INDEPENDENT_PACKS_FOR_DOCK and not pack_anomalous_elsewhere:
            evidence[OwnerCategory.CHARGER_DOCK.value].append(
                EvidenceItem(
                    description=f"Dock {dock_id} has served {dock_crossing} independent packs",
                    entity_id=dock_id,
                    count=dock_crossing,
                )
            )
            evidence[OwnerCategory.CHARGER_DOCK.value].append(
                EvidenceItem(
                    description=f"Pack {pack_id} shows normal behavior on other docks",
                    entity_id=pack_id,
                    count=len(pack_other_docks),
                )
            )
            if not sibling_anomalous:
                evidence[OwnerCategory.CHARGER_DOCK.value].append(
                    EvidenceItem(
                        description="Sibling docks at station show no similar anomaly",
                        entity_id=station_id,
                        count=len(sibling_docks),
                    )
                )
            if anomalous_other_packs:
                evidence[OwnerCategory.CHARGER_DOCK.value].append(
                    EvidenceItem(
                        description=(
                            f"{len(anomalous_other_packs)} other pack(s) showed the same "
                            f"dock-feature anomaly at {dock_id} — anomaly follows the dock"
                        ),
                        entity_id=dock_id,
                        count=len(anomalous_other_packs),
                    )
                )
            if len(evidence[OwnerCategory.CHARGER_DOCK.value]) >= 2:
                selected_owner = OwnerCategory.CHARGER_DOCK
                status = AttributionStatus.ATTRIBUTED
                confidence = "HIGH" if dock_crossing >= 3 else "MEDIUM"
                explanation_parts.append(
                    f"Evidence supports CHARGER_DOCK: {dock_crossing} independent packs affected "
                    f"at dock {dock_id}; pack {pack_id} is normal elsewhere."
                )
        elif dock_crossing < MIN_INDEPENDENT_PACKS_FOR_DOCK:
            explanation_parts.append(
                f"Insufficient dock crossing: only {dock_crossing} packs observed at dock {dock_id} "
                f"(need ≥{MIN_INDEPENDENT_PACKS_FOR_DOCK}). Cannot distinguish dock from pack."
            )

        if pack_anomalous_elsewhere:
            counterevidence[OwnerCategory.CHARGER_DOCK.value].append(
                EvidenceItem(
                    description=f"Pack {pack_id} also shows anomalies on other docks — weakens dock hypothesis",
                    entity_id=pack_id,
                )
            )

    # --- PACK hypothesis ---
    if pack_features and selected_owner is None:
        pack_docks = graph.get_independent_docks_for_pack(pack_id)
        pack_crossing = graph.pack_crossing_count(pack_id)
        crossing_support["pack_independent_docks"] = pack_crossing

        # Check: do other packs at those docks behave normally?
        other_packs_normal_at_same_docks = True
        for d in pack_docks - {dock_id}:
            other_packs_at_d = graph.get_independent_packs_for_dock(d) - {pack_id}
            for op in other_packs_at_d:
                for fid in [f.feature_id for f in pack_features]:
                    if graph.anomaly_registry.get((op, fid)):
                        other_packs_normal_at_same_docks = False

        if pack_crossing >= MIN_INDEPENDENT_DOCKS_FOR_PACK and other_packs_normal_at_same_docks:
            evidence[OwnerCategory.PACK.value].append(
                EvidenceItem(
                    description=f"Pack {pack_id} shows anomaly across {pack_crossing} independent docks",
                    entity_id=pack_id,
                    count=pack_crossing,
                )
            )
            evidence[OwnerCategory.PACK.value].append(
                EvidenceItem(
                    description="Other packs at same docks show normal behavior",
                    entity_id=pack_id,
                    count=len(pack_docks),
                )
            )
            selected_owner = OwnerCategory.PACK
            status = AttributionStatus.ATTRIBUTED
            confidence = "HIGH" if pack_crossing >= 3 else "MEDIUM"
            explanation_parts.append(
                f"Evidence supports PACK: anomaly follows pack {pack_id} across "
                f"{pack_crossing} independent docks; those docks are normal with other packs."
            )
        elif pack_crossing < MIN_INDEPENDENT_DOCKS_FOR_PACK:
            explanation_parts.append(
                f"Insufficient pack crossing: pack {pack_id} has only {pack_crossing} dock observations "
                f"(need ≥{MIN_INDEPENDENT_DOCKS_FOR_PACK}). Cannot confirm pack hypothesis."
            )

    # --- CELL_CHEMISTRY hypothesis ---
    if cell_features and selected_owner is None:
        # Cell features are direct evidence — no crossing needed
        evidence[OwnerCategory.CELL_CHEMISTRY.value].extend(
            [
                EvidenceItem(
                    description=f"Cell-level measurement: {f.feature_id}={f.value:.4f}{f.unit}",
                    entity_id=pack_id,
                    session_ids=[f.session_id],
                )
                for f in cell_features
                if f.value is not None
            ]
        )
        selected_owner = OwnerCategory.CELL_CHEMISTRY
        status = AttributionStatus.ATTRIBUTED
        confidence = "MEDIUM"
        explanation_parts.append(
            f"Cell-level voltage divergence or curve drift detected. "
            f"Evidence suggests cell/chemistry investigation for pack {pack_id}. "
            f"Note: specific degradation mechanism is unverified — route to battery engineering."
        )

    # --- ENVIRONMENT hypothesis ---
    if env_features and selected_owner is None:
        # Need multiple independent packs and docks at same station
        station_packs = set()
        station_docks = set()
        for d in graph.dock_station:
            if graph.dock_station[d] == station_id:
                station_docks.add(d)
                station_packs |= graph.get_independent_packs_for_dock(d)

        n_station_packs = len(station_packs)
        n_station_docks = len(station_docks)
        crossing_support["env_station_packs"] = n_station_packs
        crossing_support["env_station_docks"] = n_station_docks

        # Check for measured environmental evidence in feature context
        has_measured_env = any(
            f.context_signature.get("is_sagging") or f.context_signature.get("ambient_c", 0) > 35
            for f in env_features
        )

        if n_station_packs >= MIN_PACKS_FOR_ENVIRONMENT and has_measured_env:
            evidence[OwnerCategory.ENVIRONMENT.value].append(
                EvidenceItem(
                    description=f"Measured environmental condition at station {station_id}",
                    entity_id=station_id,
                    count=n_station_packs,
                )
            )
            evidence[OwnerCategory.ENVIRONMENT.value].append(
                EvidenceItem(
                    description=f"{n_station_packs} packs and {n_station_docks} docks affected at station",
                    entity_id=station_id,
                    count=n_station_docks,
                )
            )
            selected_owner = OwnerCategory.ENVIRONMENT
            status = AttributionStatus.ATTRIBUTED
            confidence = "MEDIUM"
            explanation_parts.append(
                f"Evidence supports ENVIRONMENT: measured site condition at station {station_id} "
                f"with {n_station_packs} affected packs and {n_station_docks} docks. "
                f"Note: shared station hardware faults are a competing hypothesis."
            )
        elif not has_measured_env:
            explanation_parts.append(
                "Environmental feature triggered but no measured ambient/AC evidence — "
                "cannot attribute to ENVIRONMENT without supporting sensor data. Abstaining."
            )

    # Handle conflicting hypotheses
    if (
        OwnerCategory.CHARGER_DOCK.value in evidence
        and OwnerCategory.PACK.value in evidence
        and selected_owner is None
    ):
        status = AttributionStatus.CONFLICTING_EVIDENCE
        confidence = "LOW"
        explanation_parts.append(
            "Both dock and pack hypotheses have partial support. Insufficient evidence to select owner."
        )

    # Concurrent faults across multiple entity types must not produce HIGH confidence
    has_concurrent_faults = (
        bool(dock_features) + bool(pack_features) + bool(cell_features) + bool(env_features)
    ) > 1
    if has_concurrent_faults and confidence == "HIGH":
        confidence = "MEDIUM"
        explanation_parts.append(
            "Concurrent anomalies across multiple components detected; confidence capped at MEDIUM."
        )

    return AttributionResult(
        session_id=session_id,
        candidate_owners=list(
            FEATURE_OWNER_MAP.get(f.feature_id)
            for f in anomalous_features
            if FEATURE_OWNER_MAP.get(f.feature_id) is not None
        ),
        owner_evidence=dict(evidence),
        owner_counterevidence=dict(counterevidence),
        crossing_support=crossing_support,
        selected_owner=selected_owner,
        attribution_status=status,
        confidence_semantics=confidence,
        explanation=" | ".join(explanation_parts)
        if explanation_parts
        else "No anomalies detected.",
    )


class AttributionEngine:
    """
    Runs attribution across all anomalous sessions in a batch.

    Builds the pack-dock graph first, then attributes each anomaly.
    """

    def __init__(self) -> None:
        self.graph = PackDockGraph()

    def build_graph(self, sessions: list[Any]) -> None:
        """Build bipartite graph from all sessions."""
        for s in sessions:
            self.graph.add_session(
                session_id=s.session_id,
                pack_id=s.pack_id,
                dock_id=s.dock_id,
                station_id=s.station_id,
            )
        logger.info(
            "graph_built",
            n_packs=len(self.graph.pack_to_docks),
            n_docks=len(self.graph.dock_to_packs),
        )

    def register_anomalies(
        self,
        anomalous_features: list[FeatureRecord],
    ) -> None:
        """Register all anomalous observations into graph for cross-asset lookup."""
        for fr in anomalous_features:
            if fr.validity_status != FeatureValidityStatus.VALID:
                continue
            owner = FEATURE_OWNER_MAP.get(fr.feature_id)
            if owner in (OwnerCategory.CHARGER_DOCK,) or owner == OwnerCategory.PACK:
                self.graph.add_anomaly(
                    fr.entity_id, fr.feature_id, fr.session_id, fr.normalized_score or 0
                )

    def attribute_batch(
        self,
        sessions: list[Any],
        anomaly_scores: list[Any],
        feature_records: list[FeatureRecord],
    ) -> list[AttributionResult]:
        """Attribute all anomalous sessions."""
        # Group features by session
        session_features: dict[str, list[FeatureRecord]] = defaultdict(list)
        for fr in feature_records:
            if (
                fr.validity_status == FeatureValidityStatus.VALID
                and fr.normalized_score
                and fr.normalized_score > 3.0
            ):
                session_features[fr.session_id].append(fr)

        session_map = {s.session_id: s for s in sessions}
        results: list[AttributionResult] = []

        # Register all anomalies before attribution
        all_anomalous = [fr for frs in session_features.values() for fr in frs]
        self.register_anomalies(all_anomalous)

        for session_id, anom_features in session_features.items():
            session = session_map.get(session_id)
            if session is None:
                continue

            result = attribute_session(
                session_id=session_id,
                pack_id=session.pack_id,
                dock_id=session.dock_id,
                station_id=session.station_id,
                anomalous_features=anom_features,
                graph=self.graph,
            )
            results.append(result)

        n_attributed = sum(
            1 for r in results if r.attribution_status == AttributionStatus.ATTRIBUTED
        )
        n_abstained = sum(
            1 for r in results if r.attribution_status == AttributionStatus.INSUFFICIENT_EVIDENCE
        )
        logger.info(
            "attribution_complete",
            total=len(results),
            attributed=n_attributed,
            abstained=n_abstained,
        )

        return results
