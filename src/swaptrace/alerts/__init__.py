"""
SwapTrace — Alert policy module.

Implements:
- Episode deduplication (stable episode keys)
- Persistence enforcement (non-safety alerts require repeated evidence)
- Owner/evidence/action validation (actionability invariant)
- Lifecycle transitions with audit history
- Severity routing
"""

from __future__ import annotations

from datetime import UTC, datetime, timezone
from typing import Any

from swaptrace.contracts import (
    AlertEpisode,
    AlertSeverity,
    AlertStatus,
    AlertTransition,
    AttributionResult,
    AttributionStatus,
    EvidenceItem,
    FeatureRecord,
    FeatureValidityStatus,
    OwnerCategory,
    ResolutionFeedback,
    SourceType,
)
from swaptrace.detection import PersistenceTracker
from swaptrace.observability import get_logger

logger = get_logger(__name__)

# Owner → responsible team routing
OWNER_TEAM_MAP: dict[OwnerCategory, str] = {
    OwnerCategory.CHARGER_DOCK: "charging_infrastructure",
    OwnerCategory.PACK: "battery_service",
    OwnerCategory.CELL_CHEMISTRY: "cell_engineering",
    OwnerCategory.ENVIRONMENT: "site_facilities",
}

# Owner → recommended actions
OWNER_ACTIONS: dict[OwnerCategory, list[str]] = {
    OwnerCategory.CHARGER_DOCK: [
        "Inspect dock control circuitry and power delivery hardware",
        "Test contact pins and connector path resistance",
        "Isolate dock from service for authorized technical review",
        "Cross-validate with other packs at same dock",
    ],
    OwnerCategory.PACK: [
        "Run pack electrical diagnostics (BMS health check)",
        "Inspect pack thermal system and temperature sensors",
        "Compare pack behavior at an independent dock",
        "Consider scheduling battery service or replacement assessment",
    ],
    OwnerCategory.CELL_CHEMISTRY: [
        "Inspect individual cell voltages under controlled conditions",
        "Validate cell voltage sensor calibration",
        "Route to battery engineering for electrochemical investigation",
        "Do not assume specific degradation mechanism without lab confirmation",
    ],
    OwnerCategory.ENVIRONMENT: [
        "Inspect site cooling, HVAC, and ventilation systems",
        "Check upstream electrical supply and distribution",
        "Validate AC power quality at station level",
        "Review shared infrastructure for concurrent failures",
    ],
}

# Feature → severity thresholds
FEATURE_SEVERITY_MAP: dict[str, tuple[float, float]] = {
    # (MEDIUM threshold, HIGH threshold) for normalized score
    "dock_cc_current_control_residual": (0.3, 0.5),
    "dock_contact_resistance_excess": (2.0, 5.0),
    "pack_self_heating_excess": (1.5, 3.0),
    "pack_electrical_response_anomaly": (1.5, 3.0),
    "cell_voltage_dispersion_excess": (1.0, 3.0),
    "chemistry_charge_curve_drift": (1.0, 3.0),
    "env_sitewide_heat_derate": (0.8, 2.0),
    "env_grid_sag_power_loss": (1.0, 2.0),
}


def determine_severity(
    feature_id: str,
    normalized_score: float | None,
    owner: OwnerCategory,
    persistence_count: int,
) -> AlertSeverity:
    """Determine alert severity from feature score and persistence."""
    if normalized_score is None:
        return AlertSeverity.LOW

    thresholds = FEATURE_SEVERITY_MAP.get(feature_id, (1.5, 3.0))
    med_thresh, high_thresh = thresholds

    if normalized_score >= high_thresh and persistence_count >= 3:
        return AlertSeverity.HIGH
    elif normalized_score >= med_thresh and persistence_count >= 2:
        return AlertSeverity.MEDIUM
    else:
        return AlertSeverity.LOW


class AlertPolicyEngine:
    """
    Converts attribution results into schema-valid, deduplicated alert episodes.

    Invariant: Every emitted maintenance alert has owner, entity, evidence, action.
    """

    def __init__(
        self,
        persistence_threshold: int = 2,
        data_provenance: SourceType = SourceType.SYNTHETIC,
    ) -> None:
        self.persistence = PersistenceTracker(min_occurrences=persistence_threshold)
        self.data_provenance = data_provenance
        self._episodes: dict[str, AlertEpisode] = {}  # episode_key → episode

    def _make_episode_key(
        self,
        owner: OwnerCategory,
        entity_id: str,
        feature_id: str,
    ) -> str:
        return f"{owner.value}:{entity_id}:{feature_id}"

    def process_attribution(
        self,
        result: AttributionResult,
        feature_records: list[FeatureRecord],
        session_id: str,
        session_ts: datetime,
    ) -> AlertEpisode | None:
        """
        Process one attribution result and return an alert if warranted.

        Returns None if:
        - Insufficient evidence
        - Not yet persistent enough (non-safety)
        """
        if result.attribution_status != AttributionStatus.ATTRIBUTED:
            return None
        if result.selected_owner is None:
            return None

        owner = result.selected_owner
        entity_id = self._get_entity_id(result, feature_records)

        # Find the primary anomalous feature
        owner_features = [
            fr
            for fr in feature_records
            if fr.session_id == session_id
            and fr.validity_status == FeatureValidityStatus.VALID
            and fr.normalized_score
            and fr.normalized_score > 3.0
        ]
        if not owner_features:
            return None

        primary_feature = max(owner_features, key=lambda f: f.normalized_score or 0)
        feature_id = primary_feature.feature_id

        # Record persistence
        self.persistence.record(
            entity_id=entity_id,
            feature_id=feature_id,
            session_id=session_id,
            ts=session_ts,
            z_score=primary_feature.normalized_score,
        )

        persistence_count = self.persistence.get_count(entity_id, feature_id)

        # Non-safety: require persistence threshold
        if not self.persistence.is_persistent(entity_id, feature_id):
            logger.debug(
                "alert_suppressed_not_persistent",
                entity_id=entity_id,
                feature_id=feature_id,
                count=persistence_count,
            )
            return None

        severity = determine_severity(
            feature_id=feature_id,
            normalized_score=primary_feature.normalized_score,
            owner=owner,
            persistence_count=persistence_count,
        )

        # Build evidence items
        evidence_items = list(result.owner_evidence.get(owner.value, []))
        evidence_items.append(
            EvidenceItem(
                description=(
                    f"Feature {feature_id} anomaly: "
                    f"observed={primary_feature.value:.3f}{primary_feature.unit}, "
                    + (
                        f"expected={primary_feature.expected_value:.3f}{primary_feature.unit}, "
                        if primary_feature.expected_value is not None
                        else "expected=N/A, "
                    )
                    + f"z-score={primary_feature.normalized_score:.2f}"
                ),
                entity_id=entity_id,
                session_ids=self.persistence.get_sessions(entity_id, feature_id),
                count=persistence_count,
            )
        )

        counterevidence_items = list(result.owner_counterevidence.get(owner.value, []))

        episode_key = self._make_episode_key(owner, entity_id, feature_id)

        # Deduplication: update existing episode or create new
        if episode_key in self._episodes:
            existing = self._episodes[episode_key]
            existing.last_seen_ts = session_ts
            existing.occurrence_count = persistence_count
            existing.supporting_session_ids = self.persistence.get_sessions(entity_id, feature_id)
            existing.evidence = evidence_items
            existing.observed_value = primary_feature.value
            existing.residual_normalized = primary_feature.normalized_score
            logger.debug("alert_episode_updated", episode_key=episode_key, count=persistence_count)
            return existing

        # New episode — must validate actionability via Pydantic
        try:
            episode = AlertEpisode(
                episode_key=episode_key,
                owner_category=owner,
                owner_team=OWNER_TEAM_MAP[owner],
                entity_id=entity_id,
                severity=severity,
                feature_ids=[feature_id],
                observed_value=primary_feature.value,
                expected_value=primary_feature.expected_value,
                observed_unit=primary_feature.unit,
                residual_normalized=primary_feature.normalized_score,
                evidence=evidence_items,
                counterevidence=counterevidence_items,
                independent_support_counts=result.crossing_support,
                recommended_actions=OWNER_ACTIONS[owner][:2],  # top 2 actions
                explanation=result.explanation,
                first_seen_ts=session_ts,
                last_seen_ts=session_ts,
                opened_at=datetime.now(UTC),
                occurrence_count=persistence_count,
                data_provenance=self.data_provenance,
                supporting_session_ids=self.persistence.get_sessions(entity_id, feature_id),
            )
        except Exception as e:
            logger.error("alert_validation_failed", error=str(e), episode_key=episode_key)
            return None

        self._episodes[episode_key] = episode
        logger.info(
            "alert_episode_created",
            episode_key=episode_key,
            owner=owner.value,
            entity_id=entity_id,
            severity=severity.value,
        )
        return episode

    def _get_entity_id(
        self,
        result: AttributionResult,
        feature_records: list[FeatureRecord],
    ) -> str:
        """Get the primary entity ID for the selected owner."""
        if result.selected_owner in (OwnerCategory.CHARGER_DOCK,):
            # Get dock_id from feature entity
            for fr in feature_records:
                if fr.entity_type == "dock" and fr.validity_status == FeatureValidityStatus.VALID:
                    return fr.entity_id
        elif (
            result.selected_owner == OwnerCategory.PACK
            or result.selected_owner == OwnerCategory.CELL_CHEMISTRY
        ):
            for fr in feature_records:
                if fr.entity_type == "pack":
                    return fr.entity_id
        elif result.selected_owner == OwnerCategory.ENVIRONMENT:
            for fr in feature_records:
                if fr.entity_type == "station":
                    return fr.entity_id
        return feature_records[0].entity_id if feature_records else "unknown"

    def get_all_episodes(self) -> list[AlertEpisode]:
        return list(self._episodes.values())

    def acknowledge(self, episode_key: str, actor: str = "operator") -> bool:
        ep = self._episodes.get(episode_key)
        if not ep or ep.status != AlertStatus.OPEN:
            return False
        ep.status = AlertStatus.ACKNOWLEDGED
        ep.transitions.append(
            AlertTransition(
                from_status=AlertStatus.OPEN,
                to_status=AlertStatus.ACKNOWLEDGED,
                actor=actor,
            )
        )
        return True

    def resolve(self, episode_key: str, feedback: ResolutionFeedback) -> bool:
        ep = self._episodes.get(episode_key)
        if not ep:
            return False
        ep.status = AlertStatus.RESOLVED
        ep.resolution = feedback
        ep.transitions.append(
            AlertTransition(
                from_status=ep.status,
                to_status=AlertStatus.RESOLVED,
                actor=feedback.resolved_by,
                reason=feedback.notes,
            )
        )
        return True
