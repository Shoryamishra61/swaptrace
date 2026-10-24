"""
SwapTrace — Contextual baseline module.

Implements context-conditioned expected behavior estimation.
Point-in-time safe: never fits baselines using future observations.

Uses robust statistics (MAD, median) to resist outlier contamination.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import numpy as np
import polars as pl

from swaptrace.contracts import BaselineMetadata
from swaptrace.observability import get_logger

logger = get_logger(__name__)


class ContextualBaseline:
    """
    Contextual baseline for a single feature.

    Groups sessions by context variables and computes robust statistics
    (median + MAD). Never uses future data.

    Context variables:
    - chemistry_id
    - initial_soc_bucket (10% wide)
    - ambient_temperature_bucket (5°C wide)
    - charge_protocol_id
    """

    def __init__(
        self,
        feature_id: str,
        context_vars: list[str] | None = None,
        min_support: int = 5,
        training_cutoff: datetime | None = None,
    ) -> None:
        self.feature_id = feature_id
        self.context_vars = context_vars or ["chemistry_id", "soc_bucket", "temp_bucket"]
        self.min_support = min_support
        self.training_cutoff = training_cutoff or datetime.now(UTC)
        self._groups: dict[tuple[Any, ...], dict[str, float]] = {}
        self._global_median: float = 0.0
        self._global_mad: float = 1.0
        self._n_training: int = 0
        self.metadata = BaselineMetadata(
            feature_id=feature_id,
            training_cutoff=self.training_cutoff,
            context_variables=self.context_vars,
            minimum_support=min_support,
        )

    def _soc_bucket(self, soc: float | None) -> str:
        if soc is None:
            return "unknown"
        b = int(soc // 10) * 10
        return f"soc_{b}_{b + 10}"

    def _temp_bucket(self, temp: float | None) -> str:
        if temp is None:
            return "unknown"
        b = int(temp // 5) * 5
        return f"temp_{b}_{b + 5}"

    def _context_key(self, row: dict[str, Any]) -> tuple[Any, ...]:
        parts = []
        for var in self.context_vars:
            if var == "soc_bucket":
                parts.append(self._soc_bucket(row.get("initial_soc_pct")))
            elif var == "temp_bucket":
                parts.append(self._temp_bucket(row.get("ambient_temperature_c")))
            else:
                parts.append(str(row.get(var, "unknown")))
        return tuple(parts)

    def fit(
        self,
        sessions_df: pl.DataFrame,
        values_series: list[float | None],
        session_ids: list[str],
    ) -> ContextualBaseline:
        """
        Fit baseline from training sessions.

        CRITICAL: Only call with sessions whose start_ts < training_cutoff.
        """
        rows = sessions_df.to_dicts()
        valid_pairs: list[tuple[tuple[Any, ...], float]] = []

        for row, val in zip(rows, values_series, strict=False):
            if val is None or not np.isfinite(val):
                continue
            # Point-in-time: exclude future
            ts = row.get("start_ts")
            if ts and hasattr(ts, "timestamp") and ts.replace(tzinfo=UTC) > self.training_cutoff:
                continue
            key = self._context_key(row)
            valid_pairs.append((key, val))

        if not valid_pairs:
            logger.warning("baseline_empty", feature_id=self.feature_id)
            return self

        all_vals = [v for _, v in valid_pairs]
        self._global_median = float(np.median(all_vals))
        self._global_mad = float(np.median(np.abs(np.array(all_vals) - self._global_median)))
        if self._global_mad < 1e-6:
            self._global_mad = float(np.std(all_vals)) + 1e-6
        self._n_training = len(all_vals)

        # Group by context
        from collections import defaultdict

        groups: dict[tuple[Any, ...], list[float]] = defaultdict(list)
        for key, val in valid_pairs:
            groups[key].append(val)

        for key, vals in groups.items():
            if len(vals) < self.min_support:
                continue
            arr = np.array(vals)
            median = float(np.median(arr))
            mad = float(np.median(np.abs(arr - median)))
            if mad < 1e-6:
                mad = float(np.std(arr)) + 1e-6
            self._groups[key] = {
                "median": median,
                "mad": mad,
                "count": len(vals),
            }

        self.metadata.population_size = self._n_training
        logger.info(
            "baseline_fitted",
            feature_id=self.feature_id,
            n_training=self._n_training,
            n_groups=len(self._groups),
        )
        return self

    def predict(
        self,
        row: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Predict expected value and robust z-score for a session.
        Falls back to global statistics if context group has insufficient support.
        """
        key = self._context_key(row)
        group = self._groups.get(key)

        if group and group["count"] >= self.min_support:
            expected = group["median"]
            mad = group["mad"]
            coverage = "contextual"
            support = group["count"]
        else:
            expected = self._global_median
            mad = self._global_mad
            coverage = "global_fallback"
            support = self._n_training

        return {
            "expected_value": expected,
            "mad": mad,
            "coverage": coverage,
            "support": support,
            "context_key": key,
            "out_of_distribution": group is None,
        }

    def robust_z_score(self, observed: float, row: dict[str, Any]) -> float:
        """
        Compute robust normalized residual:
        z = 0.6745 * (observed - median) / (MAD + ε)
        """
        pred = self.predict(row)
        mad = pred["mad"]
        median = pred["expected_value"]
        epsilon = 1e-6
        return 0.6745 * (observed - median) / (mad + epsilon)


class BaselineManager:
    """Manages multiple feature baselines with version tracking."""

    def __init__(self) -> None:
        self._baselines: dict[str, ContextualBaseline] = {}
        self.version: str = "1.0"

    def register(self, baseline: ContextualBaseline) -> None:
        self._baselines[baseline.feature_id] = baseline

    def get(self, feature_id: str) -> ContextualBaseline | None:
        return self._baselines.get(feature_id)

    def fit_from_features_df(
        self,
        features_df: pl.DataFrame,
        sessions_df: pl.DataFrame,
        training_cutoff: datetime,
    ) -> None:
        """Fit all feature baselines from historical data."""
        feature_ids = features_df.get_column("feature_id").unique().to_list()

        for fid in feature_ids:
            fdf = features_df.filter(
                (pl.col("feature_id") == fid) & (pl.col("validity_status") == "VALID")
            )
            if len(fdf) < 5:
                continue

            session_ids = fdf.get_column("session_id").to_list()
            values = fdf.get_column("value").to_list()

            matched_sessions = sessions_df.filter(pl.col("session_id").is_in(session_ids))
            if len(matched_sessions) == 0:
                continue

            baseline = ContextualBaseline(
                feature_id=fid,
                training_cutoff=training_cutoff,
            )
            # Align values to matched sessions
            sess_ids_set = set(matched_sessions.get_column("session_id").to_list())
            aligned_values = []
            for sid, val in zip(session_ids, values, strict=False):
                if sid in sess_ids_set:
                    aligned_values.append(val)

            baseline.fit(matched_sessions, aligned_values, session_ids)
            self.register(baseline)

        logger.info("baselines_fitted", count=len(self._baselines))

    def compute_residuals(
        self,
        feature_records: list[Any],
        sessions: list[Any],
    ) -> list[Any]:
        """Compute normalized residuals for all valid feature records."""
        session_map = {s.session_id: s for s in sessions}

        for fr in feature_records:
            if fr.validity_status.value != "VALID" or fr.value is None:
                continue
            baseline = self.get(fr.feature_id)
            if baseline is None:
                continue
            session = session_map.get(fr.session_id)
            if session is None:
                continue
            row = {
                "chemistry_id": session.chemistry_id,
                "initial_soc_pct": session.initial_soc_pct,
                "ambient_temperature_c": session.ambient_temperature_c,
                "charge_protocol_id": session.charge_protocol_id,
            }
            pred = baseline.predict(row)
            fr.expected_value = pred["expected_value"]
            fr.residual = fr.value - pred["expected_value"]
            fr.normalized_score = abs(baseline.robust_z_score(fr.value, row))
            fr.baseline_version = (
                baseline.metadata.version if hasattr(baseline.metadata, "version") else "1.0"
            )
            fr.context_signature.update(
                {
                    "baseline_coverage": pred["coverage"],
                    "baseline_support": pred["support"],
                }
            )
        return feature_records
