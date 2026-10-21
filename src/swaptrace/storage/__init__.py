"""
SwapTrace — Storage layer (DuckDB + Parquet).

Provides idempotent persistence for sessions, features, alerts, and evaluation artifacts.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import polars as pl

from swaptrace.observability import get_logger

logger = get_logger(__name__)

DATA_DIR = Path("data")
DERIVED_DIR = DATA_DIR / "derived"
VALIDATED_DIR = DATA_DIR / "validated"
RAW_DIR = DATA_DIR / "raw"
ARTIFACTS_DIR = Path("artifacts")


def ensure_dirs() -> None:
    for d in [
        RAW_DIR,
        VALIDATED_DIR,
        DERIVED_DIR,
        ARTIFACTS_DIR / "evaluation",
        ARTIFACTS_DIR / "alerts",
        ARTIFACTS_DIR / "screenshots",
    ]:
        d.mkdir(parents=True, exist_ok=True)


class SwapTraceDB:
    """DuckDB-backed analytical storage with Parquet persistence."""

    def __init__(self, db_path: str | Path = ":memory:", data_dir: Path = DATA_DIR) -> None:
        self.db_path = str(db_path)
        self.data_dir = data_dir
        self.conn = duckdb.connect(self.db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id VARCHAR PRIMARY KEY,
                pack_id VARCHAR NOT NULL,
                dock_id VARCHAR NOT NULL,
                station_id VARCHAR NOT NULL,
                chemistry_id VARCHAR,
                charge_protocol_id VARCHAR,
                start_ts TIMESTAMPTZ,
                end_ts TIMESTAMPTZ,
                duration_s DOUBLE,
                initial_soc_pct DOUBLE,
                final_soc_pct DOUBLE,
                initial_pack_temperature_c DOUBLE,
                ambient_temperature_c DOUBLE,
                charge_status VARCHAR,
                integrated_charge_ah DOUBLE,
                integrated_energy_wh DOUBLE,
                data_quality_status VARCHAR,
                data_quality_reasons VARCHAR,
                sensor_capabilities VARCHAR,
                sample_count INTEGER,
                source_type VARCHAR,
                source_dataset VARCHAR,
                pipeline_version VARCHAR,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS features (
                feature_id VARCHAR NOT NULL,
                feature_version INTEGER NOT NULL,
                session_id VARCHAR NOT NULL,
                entity_type VARCHAR,
                entity_id VARCHAR NOT NULL,
                value DOUBLE,
                unit VARCHAR,
                expected_value DOUBLE,
                residual DOUBLE,
                normalized_score DOUBLE,
                context_signature VARCHAR,
                baseline_version VARCHAR,
                validity_status VARCHAR NOT NULL,
                invalidity_reason VARCHAR,
                sample_count INTEGER,
                computed_at TIMESTAMPTZ,
                PRIMARY KEY (feature_id, session_id)
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id VARCHAR PRIMARY KEY,
                episode_key VARCHAR NOT NULL,
                owner_category VARCHAR NOT NULL,
                owner_team VARCHAR NOT NULL,
                entity_id VARCHAR NOT NULL,
                severity VARCHAR NOT NULL,
                status VARCHAR NOT NULL DEFAULT 'OPEN',
                feature_ids VARCHAR,
                observed_value DOUBLE,
                expected_value DOUBLE,
                observed_unit VARCHAR,
                residual_normalized DOUBLE,
                evidence VARCHAR,
                counterevidence VARCHAR,
                independent_support_counts VARCHAR,
                recommended_actions VARCHAR,
                explanation TEXT,
                first_seen_ts TIMESTAMPTZ,
                last_seen_ts TIMESTAMPTZ,
                opened_at TIMESTAMPTZ,
                occurrence_count INTEGER DEFAULT 1,
                baseline_version VARCHAR,
                pipeline_version VARCHAR,
                data_provenance VARCHAR,
                supporting_session_ids VARCHAR,
                resolution VARCHAR,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS attributions (
                session_id VARCHAR NOT NULL,
                entity_id VARCHAR NOT NULL,
                selected_owner VARCHAR,
                attribution_status VARCHAR NOT NULL,
                confidence_semantics VARCHAR,
                explanation TEXT,
                crossing_support VARCHAR,
                computed_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (session_id, entity_id)
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS run_manifests (
                run_id VARCHAR PRIMARY KEY,
                seed INTEGER,
                git_commit VARCHAR,
                configuration_hash VARCHAR,
                schema_version VARCHAR,
                start_time TIMESTAMPTZ,
                end_time TIMESTAMPTZ,
                raw_events INTEGER,
                validated_events INTEGER,
                rejected_events INTEGER,
                sessions_total INTEGER,
                sessions_complete INTEGER,
                sessions_eligible INTEGER,
                features_computed INTEGER,
                features_not_computable INTEGER,
                alerts_emitted INTEGER,
                alerts_deduplicated INTEGER,
                abstentions INTEGER,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

    def upsert_sessions(self, sessions: list[Any]) -> int:
        """Idempotent session persistence."""
        rows = []
        for s in sessions:
            rows.append(
                {
                    "session_id": s.session_id,
                    "pack_id": s.pack_id,
                    "dock_id": s.dock_id,
                    "station_id": s.station_id,
                    "chemistry_id": s.chemistry_id,
                    "charge_protocol_id": s.charge_protocol_id,
                    "start_ts": s.start_ts,
                    "end_ts": s.end_ts,
                    "duration_s": s.duration_s,
                    "initial_soc_pct": s.initial_soc_pct,
                    "final_soc_pct": s.final_soc_pct,
                    "initial_pack_temperature_c": s.initial_pack_temperature_c,
                    "ambient_temperature_c": s.ambient_temperature_c,
                    "charge_status": s.charge_status.value
                    if hasattr(s.charge_status, "value")
                    else s.charge_status,
                    "integrated_charge_ah": s.integrated_charge_ah,
                    "integrated_energy_wh": s.integrated_energy_wh,
                    "data_quality_status": s.data_quality_status.value
                    if hasattr(s.data_quality_status, "value")
                    else s.data_quality_status,
                    "data_quality_reasons": json.dumps(s.data_quality_reasons),
                    "sensor_capabilities": json.dumps(s.sensor_capabilities),
                    "sample_count": s.sample_count,
                    "source_type": s.source_type.value
                    if hasattr(s.source_type, "value")
                    else s.source_type,
                    "source_dataset": s.source_dataset,
                    "pipeline_version": s.pipeline_version,
                }
            )
        if not rows:
            return 0
        df = pl.DataFrame(rows)
        cols = ", ".join(rows[0].keys())
        self.conn.execute(f"""
            INSERT OR REPLACE INTO sessions ({cols})
            SELECT {cols} FROM df
        """)
        logger.info("sessions_persisted", count=len(rows))
        return len(rows)

    def upsert_features(self, features: list[Any]) -> int:
        """Idempotent feature persistence."""
        rows = []
        for f in features:
            rows.append(
                {
                    "feature_id": f.feature_id,
                    "feature_version": f.feature_version,
                    "session_id": f.session_id,
                    "entity_type": f.entity_type,
                    "entity_id": f.entity_id,
                    "value": f.value,
                    "unit": f.unit,
                    "expected_value": f.expected_value,
                    "residual": f.residual,
                    "normalized_score": f.normalized_score,
                    "context_signature": json.dumps(f.context_signature),
                    "baseline_version": f.baseline_version,
                    "validity_status": f.validity_status.value
                    if hasattr(f.validity_status, "value")
                    else f.validity_status,
                    "invalidity_reason": f.invalidity_reason,
                    "sample_count": f.sample_count,
                    "computed_at": f.computed_at,
                }
            )
        if not rows:
            return 0
        df = pl.DataFrame(rows)
        self.conn.execute("INSERT OR REPLACE INTO features SELECT * FROM df")
        return len(rows)

    def upsert_alert(self, alert: Any) -> None:
        """Idempotent alert persistence — never mutates historical evidence."""
        self.conn.execute(
            """
            INSERT OR REPLACE INTO alerts (
                alert_id, episode_key, owner_category, owner_team, entity_id,
                severity, status, feature_ids, observed_value, expected_value,
                observed_unit, residual_normalized, evidence, counterevidence,
                independent_support_counts, recommended_actions, explanation,
                first_seen_ts, last_seen_ts, opened_at, occurrence_count,
                baseline_version, pipeline_version, data_provenance,
                supporting_session_ids, resolution
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                alert.alert_id,
                alert.episode_key,
                alert.owner_category.value
                if hasattr(alert.owner_category, "value")
                else alert.owner_category,
                alert.owner_team,
                alert.entity_id,
                alert.severity.value if hasattr(alert.severity, "value") else alert.severity,
                alert.status.value if hasattr(alert.status, "value") else alert.status,
                json.dumps(alert.feature_ids),
                alert.observed_value,
                alert.expected_value,
                alert.observed_unit,
                alert.residual_normalized,
                json.dumps([e.model_dump() for e in alert.evidence]),
                json.dumps([e.model_dump() for e in alert.counterevidence]),
                json.dumps(alert.independent_support_counts),
                json.dumps(alert.recommended_actions),
                alert.explanation,
                alert.first_seen_ts,
                alert.last_seen_ts,
                alert.opened_at,
                alert.occurrence_count,
                alert.baseline_version,
                alert.pipeline_version,
                alert.data_provenance.value
                if hasattr(alert.data_provenance, "value")
                else alert.data_provenance,
                json.dumps(alert.supporting_session_ids),
                alert.resolution.model_dump_json() if alert.resolution else None,
            ],
        )

    def query(self, sql: str, params: list[Any] | None = None) -> pl.DataFrame:
        if params:
            return self.conn.execute(sql, params).pl()
        return self.conn.execute(sql).pl()

    def get_sessions(self, filters: dict[str, Any] | None = None) -> pl.DataFrame:
        sql = "SELECT * FROM sessions"
        if filters:
            clauses = [f"{k} = ?" for k in filters]
            sql += " WHERE " + " AND ".join(clauses)
            return self.query(sql, list(filters.values()))
        return self.query(sql)

    def get_features(self, feature_id: str | None = None) -> pl.DataFrame:
        if feature_id:
            return self.query("SELECT * FROM features WHERE feature_id = ?", [feature_id])
        return self.query("SELECT * FROM features")

    def get_alerts(self) -> pl.DataFrame:
        return self.query("SELECT * FROM alerts ORDER BY last_seen_ts DESC")

    def save_parquet(self, table: str, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        df = self.query(f"SELECT * FROM {table}")
        df.write_parquet(str(path))
        logger.info("parquet_saved", table=table, path=str(path), rows=len(df))

    def load_parquet(self, table: str, path: Path) -> int:
        if not path.exists():
            return 0
        df = pl.read_parquet(str(path))
        self.conn.execute(f"INSERT OR REPLACE INTO {table} SELECT * FROM df")
        return len(df)

    def get_pack_dock_graph(self) -> pl.DataFrame:
        """Return all observed pack-dock relationships with session counts."""
        return self.query("""
            SELECT pack_id, dock_id, station_id,
                   COUNT(*) as session_count,
                   MIN(start_ts) as first_seen,
                   MAX(start_ts) as last_seen
            FROM sessions
            WHERE data_quality_status = 'OK'
            GROUP BY pack_id, dock_id, station_id
        """)

    def close(self) -> None:
        self.conn.close()


# Module-level singleton
_db_instance: SwapTraceDB | None = None


def get_db(db_path: str = "data/swaptrace.db") -> SwapTraceDB:
    global _db_instance
    if _db_instance is None:
        ensure_dirs()
        _db_instance = SwapTraceDB(db_path=db_path)
    return _db_instance
