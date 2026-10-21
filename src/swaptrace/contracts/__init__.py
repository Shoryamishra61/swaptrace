"""
SwapTrace — Canonical data contracts (Pydantic schemas).

All typed boundaries for the pipeline. Every module must import from here.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SourceType(str, Enum):
    PUBLIC = "PUBLIC"
    SYNTHETIC = "SYNTHETIC"
    INJECTED = "INJECTED"


class OwnerCategory(str, Enum):
    CHARGER_DOCK = "CHARGER_DOCK"
    PACK = "PACK"
    CELL_CHEMISTRY = "CELL_CHEMISTRY"
    ENVIRONMENT = "ENVIRONMENT"


class AttributionStatus(str, Enum):
    ATTRIBUTED = "ATTRIBUTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class AlertStatus(str, Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"
    REOPENED = "REOPENED"


class ChargeStatus(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    ABORTED = "ABORTED"
    QUALITY_REJECTED = "QUALITY_REJECTED"


class DataQualityStatus(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    REJECTED = "REJECTED"


class FeatureValidityStatus(str, Enum):
    VALID = "VALID"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"
    SENSOR_MISSING = "SENSOR_MISSING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    PHYSICAL_CONSTRAINT_VIOLATED = "PHYSICAL_CONSTRAINT_VIOLATED"
    OUT_OF_DISTRIBUTION = "OUT_OF_DISTRIBUTION"


class SensorCapability(str, Enum):
    CHARGER_CURRENT = "charger_current"
    CHARGER_VOLTAGE = "charger_voltage"
    PACK_CURRENT = "pack_current"
    PACK_VOLTAGE = "pack_voltage"
    PACK_TEMPERATURE = "pack_temperature"
    CELL_VOLTAGE = "cell_voltage"
    AMBIENT_TEMPERATURE = "ambient_temperature"
    AC_INPUT_VOLTAGE = "ac_input_voltage"
    COMMANDED_CURRENT = "commanded_current"
    SOC = "soc"
    DOCK_TEMPERATURE = "dock_temperature"


# ---------------------------------------------------------------------------
# Telemetry Event
# ---------------------------------------------------------------------------


class TelemetryEvent(BaseModel):
    """A single time-indexed measurement from charging hardware."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_ts: datetime  # UTC measurement time
    ingest_ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: str
    station_id: str
    dock_id: str
    pack_id: str
    charge_protocol_id: str = "DEFAULT"

    # Core measurements — nullable; never fabricated
    charger_current_a: float | None = None
    charger_voltage_v: float | None = None
    pack_current_a: float | None = None
    pack_voltage_v: float | None = None
    pack_temperature_c: float | None = None
    soc_pct: float | None = None

    # Optional high-value measurements
    commanded_current_a: float | None = None
    commanded_voltage_v: float | None = None
    ambient_temperature_c: float | None = None
    dock_temperature_c: float | None = None
    cell_voltages_v: list[float] | None = None
    ac_input_voltage_v: float | None = None
    bms_limit_reason: str | None = None
    charger_error_code: str | None = None
    chemistry_id: str | None = None
    equivalent_cycles: float | None = None

    # Provenance
    source_type: SourceType = SourceType.SYNTHETIC
    source_record_id: str | None = None

    @field_validator("soc_pct")
    @classmethod
    def soc_in_range(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError(f"soc_pct must be 0-100, got {v}")
        return v

    @field_validator("event_ts", "ingest_ts", mode="before")
    @classmethod
    def ensure_utc(cls, v: Any) -> datetime:
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=UTC)
            return v
        raise ValueError(f"Expected datetime, got {type(v)}")


# ---------------------------------------------------------------------------
# Charge Session
# ---------------------------------------------------------------------------


class PhaseInterval(BaseModel):
    phase: str  # CC, CV, TAPER, UNKNOWN
    start_ts: datetime
    end_ts: datetime
    sample_count: int = 0


class ChargeSession(BaseModel):
    """A complete reconstructed charging session with quality metadata."""

    session_id: str
    pack_id: str
    dock_id: str
    station_id: str
    chemistry_id: str | None = None
    charge_protocol_id: str = "DEFAULT"

    start_ts: datetime
    end_ts: datetime
    duration_s: float = 0.0

    initial_soc_pct: float | None = None
    final_soc_pct: float | None = None
    initial_pack_temperature_c: float | None = None
    ambient_temperature_c: float | None = None

    charge_status: ChargeStatus = ChargeStatus.COMPLETE
    phase_intervals: list[PhaseInterval] = Field(default_factory=list)

    integrated_charge_ah: float | None = None
    integrated_energy_wh: float | None = None

    data_quality_status: DataQualityStatus = DataQualityStatus.OK
    data_quality_reasons: list[str] = Field(default_factory=list)
    sensor_capabilities: list[str] = Field(default_factory=list)

    sample_count: int = 0
    source_type: SourceType = SourceType.SYNTHETIC
    source_dataset: str = "benchmark"
    pipeline_version: str = "1.0.0"

    # Fault injection metadata — NEVER used as model features
    _injected_fault: str | None = None
    _fault_owner: str | None = None


# ---------------------------------------------------------------------------
# Feature Record
# ---------------------------------------------------------------------------


class FeatureRecord(BaseModel):
    """Computed diagnostic feature for a session."""

    feature_id: str
    feature_version: int = 1
    session_id: str
    entity_type: str  # "pack", "dock", "station"
    entity_id: str

    value: float | None = None
    unit: str
    expected_value: float | None = None
    residual: float | None = None
    normalized_score: float | None = None

    context_signature: dict[str, Any] = Field(default_factory=dict)
    baseline_version: str = "1.0"
    validity_status: FeatureValidityStatus = FeatureValidityStatus.VALID
    invalidity_reason: str | None = None
    sample_count: int = 0
    supporting_session_ids: list[str] = Field(default_factory=list)
    computed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Baseline Metadata
# ---------------------------------------------------------------------------


class BaselineMetadata(BaseModel):
    """Versioned baseline model metadata — point-in-time correctness."""

    baseline_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    feature_id: str
    version: str = "1.0"
    training_cutoff: datetime
    training_source_ids: list[str] = Field(default_factory=list)
    context_variables: list[str] = Field(default_factory=list)
    population_size: int = 0
    coverage_description: str = ""
    minimum_support: int = 10
    out_of_distribution_context: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Attribution Result
# ---------------------------------------------------------------------------


class EvidenceItem(BaseModel):
    description: str
    entity_id: str | None = None
    session_ids: list[str] = Field(default_factory=list)
    count: int = 1


class AttributionResult(BaseModel):
    """Owner attribution for an observed anomalous session/episode."""

    session_id: str | None = None
    episode_id: str | None = None

    candidate_owners: list[OwnerCategory] = Field(default_factory=list)
    owner_evidence: dict[str, list[EvidenceItem]] = Field(default_factory=dict)
    owner_counterevidence: dict[str, list[EvidenceItem]] = Field(default_factory=dict)
    crossing_support: dict[str, int] = Field(default_factory=dict)  # independent asset counts

    selected_owner: OwnerCategory | None = None
    attribution_status: AttributionStatus = AttributionStatus.INSUFFICIENT_EVIDENCE
    confidence_semantics: str = "LOW"  # HIGH/MEDIUM/LOW/INSUFFICIENT
    explanation: str = ""


# ---------------------------------------------------------------------------
# Alert Episode
# ---------------------------------------------------------------------------


class AlertTransition(BaseModel):
    from_status: AlertStatus | None = None
    to_status: AlertStatus
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor: str = "system"
    reason: str | None = None


class ResolutionFeedback(BaseModel):
    episode_id: str
    resolution_outcome: str  # CONFIRMED, FALSE_POSITIVE, INCONCLUSIVE, NO_DEFECT_FOUND
    resolved_by: str
    resolved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: str | None = None
    actual_owner: OwnerCategory | None = None


class AlertEpisode(BaseModel):
    """Actionable maintenance alert with full evidence chain."""

    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    episode_key: str  # stable deduplication key: owner:entity:feature

    owner_category: OwnerCategory
    owner_team: str
    entity_id: str
    severity: AlertSeverity

    status: AlertStatus = AlertStatus.OPEN
    feature_ids: list[str] = Field(default_factory=list)

    observed_value: float | None = None
    expected_value: float | None = None
    observed_unit: str = ""
    residual_normalized: float | None = None

    evidence: list[EvidenceItem] = Field(default_factory=list)
    counterevidence: list[EvidenceItem] = Field(default_factory=list)
    independent_support_counts: dict[str, int] = Field(default_factory=dict)

    recommended_actions: list[str] = Field(default_factory=list)
    explanation: str = ""

    first_seen_ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_seen_ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    opened_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    occurrence_count: int = 1

    baseline_version: str = "1.0"
    pipeline_version: str = "1.0.0"
    data_provenance: SourceType = SourceType.SYNTHETIC

    supporting_session_ids: list[str] = Field(default_factory=list)
    transitions: list[AlertTransition] = Field(default_factory=list)
    resolution: ResolutionFeedback | None = None

    @model_validator(mode="after")
    def validate_actionability(self) -> AlertEpisode:
        """Enforce: every emitted maintenance alert has owner, entity, evidence, action."""
        if self.severity == AlertSeverity.INSUFFICIENT_EVIDENCE:
            return self  # investigative observations exempt
        if not self.owner_team:
            raise ValueError("Alert must specify owner_team")
        if not self.recommended_actions:
            raise ValueError("Alert must specify at least one recommended_action")
        if not self.evidence:
            raise ValueError("Alert must contain at least one evidence item")
        return self


# ---------------------------------------------------------------------------
# Run Manifest
# ---------------------------------------------------------------------------


class RunManifest(BaseModel):
    """Reproducibility and provenance record for a pipeline execution."""

    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seed: int = 42
    git_commit: str = "unknown"
    configuration_hash: str = ""
    schema_version: str = "1.0"
    feature_versions: dict[str, int] = Field(default_factory=dict)
    baseline_version: str = "1.0"
    source_manifest: dict[str, str] = Field(default_factory=dict)
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None

    # Counts
    raw_events: int = 0
    validated_events: int = 0
    rejected_events: int = 0
    sessions_total: int = 0
    sessions_complete: int = 0
    sessions_eligible: int = 0
    features_computed: int = 0
    features_not_computable: int = 0
    alerts_emitted: int = 0
    alerts_deduplicated: int = 0
    abstentions: int = 0
