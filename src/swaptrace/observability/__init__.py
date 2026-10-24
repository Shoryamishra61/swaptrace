"""Structured logging and pipeline observability."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog


def configure_logging(level: str = "INFO", json: bool = False) -> None:
    """Configure structured logging for SwapTrace pipeline."""
    processors: list[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )


def get_logger(name: str) -> Any:
    return structlog.get_logger(name)


@dataclass
class PipelineCounters:
    """Mutable counters for pipeline stage tracking."""

    stage: str = ""
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
    errors: list[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "raw_events": self.raw_events,
            "validated_events": self.validated_events,
            "rejected_events": self.rejected_events,
            "sessions_total": self.sessions_total,
            "sessions_complete": self.sessions_complete,
            "sessions_eligible": self.sessions_eligible,
            "features_computed": self.features_computed,
            "features_not_computable": self.features_not_computable,
            "alerts_emitted": self.alerts_emitted,
            "alerts_deduplicated": self.alerts_deduplicated,
            "abstentions": self.abstentions,
            "errors": self.errors,
            "elapsed_s": (datetime.now(UTC) - self.start_time).total_seconds(),
        }
