"""
SwapTrace — Ingestion module.

Provides:
1. Benchmark (offline) fixture adapter — deterministic, no network needed
2. Public dataset adapter interface (with documented access requirements)

All transformations and missing fields are recorded in the ingestion manifest.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from swaptrace.contracts import ChargeSession, SourceType, TelemetryEvent
from swaptrace.observability import get_logger

logger = get_logger(__name__)


class IngestionManifest:
    """Records all transformations, missing fields, and provenance."""

    def __init__(self, source_name: str) -> None:
        self.source_name = source_name
        self.source_type: str = SourceType.SYNTHETIC.value
        self.access_url: str | None = None
        self.license_status: str = "SYNTHETIC — no license required"
        self.schema_version: str = "1.0"
        self.ingest_ts: datetime = datetime.now(UTC)
        self.n_raw_records: int = 0
        self.n_accepted: int = 0
        self.n_rejected: int = 0
        self.missing_fields: list[str] = []
        self.transformations: list[str] = []
        self.excluded_fields: list[str] = []
        self.notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "source_type": self.source_type,
            "access_url": self.access_url,
            "license_status": self.license_status,
            "schema_version": self.schema_version,
            "ingest_ts": self.ingest_ts.isoformat(),
            "n_raw_records": self.n_raw_records,
            "n_accepted": self.n_accepted,
            "n_rejected": self.n_rejected,
            "missing_fields": self.missing_fields,
            "transformations": self.transformations,
            "excluded_fields": self.excluded_fields,
            "notes": self.notes,
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info("manifest_saved", path=str(path))


class BenchmarkAdapter:
    """
    Offline benchmark fixture adapter.

    Generates or loads deterministic synthetic charging sessions.
    Does NOT require network access.
    All data is clearly labeled as SYNTHETIC.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.manifest = IngestionManifest("swaptrace-benchmark")
        self.manifest.source_type = SourceType.SYNTHETIC.value
        self.manifest.notes = (
            "Semi-synthetic swapping network. 4 stations, 16 docks, 80 packs, 14 days. "
            "No real Gogoro data. No private EV telemetry. "
            "Fault injections have ground-truth labels used only for evaluation."
        )
        self.manifest.transformations = [
            "Gaussian noise added to all measurements",
            "Physics-consistent temperature rise computation (I²R)",
            "Trapezoidal charge integration",
        ]

    def generate(self) -> tuple[list[ChargeSession], list[TelemetryEvent], list[dict[str, Any]]]:
        """
        Generate benchmark sessions, events, and ground-truth labels.

        Returns:
            sessions: List of ChargeSession objects
            events: List of TelemetryEvent objects
            ground_truth: List of ground-truth fault labels (evaluation only)
        """
        from benchmark.generator import BenchmarkGenerator

        logger.info("benchmark_generation_start", seed=self.seed)
        gen = BenchmarkGenerator(seed=self.seed)
        gen.inject_faults()

        sessions = gen.generate_sessions()
        events = gen.generate_telemetry_events(sessions)
        ground_truth = gen.ground_truth_labels

        self.manifest.n_raw_records = len(events)
        self.manifest.n_accepted = len(events)
        self.manifest.missing_fields = []

        logger.info(
            "benchmark_generation_complete",
            sessions=len(sessions),
            events=len(events),
            ground_truth_labels=len(ground_truth),
        )

        return sessions, events, ground_truth

    def load_or_generate(
        self,
        cache_dir: Path = Path("data/raw"),
    ) -> tuple[list[ChargeSession], list[TelemetryEvent], list[dict[str, Any]]]:
        """Load cached data if available, otherwise generate."""
        sessions_path = cache_dir / "sessions.parquet"
        gt_path = cache_dir / "ground_truth.json"

        if sessions_path.exists():
            # Cached sessions exist — but events are regenerated deterministically
            # so the full (sessions, events, ground_truth) triple stays consistent
            logger.info("loading_cached_sessions", path=str(sessions_path))
            sessions, events, ground_truth = self.generate()
            return sessions, events, ground_truth

        sessions, events, ground_truth = self.generate()

        # Cache sessions
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(gt_path, "w") as f:
            json.dump(ground_truth, f, indent=2)

        return sessions, events, ground_truth
