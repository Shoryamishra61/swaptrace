"""
SwapTrace — Detection module.

Robust residual scoring, anomaly detection, and persistence checking.
Uses contextual baselines to compute z-scores and detect anomalies.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from swaptrace.contracts import FeatureRecord, FeatureValidityStatus
from swaptrace.observability import get_logger

logger = get_logger(__name__)

# Default z-score threshold for flagging anomalies
DEFAULT_Z_THRESHOLD = 3.0

# Minimum occurrences before emitting a non-safety maintenance alert
DEFAULT_PERSISTENCE_THRESHOLD = 2


class AnomalyScore:
    """Anomaly detection result for a feature observation."""

    def __init__(
        self,
        feature_record: FeatureRecord,
        is_anomaly: bool,
        z_score: float | None,
        threshold_used: float,
    ) -> None:
        self.feature_record = feature_record
        self.is_anomaly = is_anomaly
        self.z_score = z_score
        self.threshold_used = threshold_used


class PersistenceTracker:
    """
    Tracks repeated anomaly observations per entity+feature.

    Prevents single-outlier false alerts.
    Non-safety anomalies require `min_occurrences` before triggering.
    """

    def __init__(self, min_occurrences: int = DEFAULT_PERSISTENCE_THRESHOLD) -> None:
        self.min_occurrences = min_occurrences
        # entity_key → feature_id → list of (session_id, ts, z_score)
        self._history: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
            lambda: defaultdict(list)
        )

    def record(
        self,
        entity_id: str,
        feature_id: str,
        session_id: str,
        ts: datetime,
        z_score: float | None,
    ) -> None:
        self._history[entity_id][feature_id].append(
            {
                "session_id": session_id,
                "ts": ts,
                "z_score": z_score,
            }
        )

    def get_count(self, entity_id: str, feature_id: str) -> int:
        return len(self._history[entity_id].get(feature_id, []))

    def get_sessions(self, entity_id: str, feature_id: str) -> list[str]:
        return [r["session_id"] for r in self._history[entity_id].get(feature_id, [])]

    def is_persistent(self, entity_id: str, feature_id: str) -> bool:
        return self.get_count(entity_id, feature_id) >= self.min_occurrences

    def clear(self, entity_id: str, feature_id: str) -> None:
        self._history[entity_id][feature_id] = []


def score_anomalies(
    feature_records: list[FeatureRecord],
    z_threshold: float = DEFAULT_Z_THRESHOLD,
) -> list[AnomalyScore]:
    """
    Apply anomaly threshold to normalized feature scores.

    Uses the normalized_score (robust z-score equivalent) from baselines.
    Returns AnomalyScore for each valid feature record.
    """
    scores: list[AnomalyScore] = []

    for fr in feature_records:
        if fr.validity_status != FeatureValidityStatus.VALID:
            continue

        z = fr.normalized_score
        is_anomaly = (z is not None) and (z > z_threshold)

        scores.append(
            AnomalyScore(
                feature_record=fr,
                is_anomaly=is_anomaly,
                z_score=z,
                threshold_used=z_threshold,
            )
        )

    n_anomalies = sum(1 for s in scores if s.is_anomaly)
    logger.debug(
        "anomaly_scoring_complete", total=len(scores), anomalies=n_anomalies, threshold=z_threshold
    )
    return scores
