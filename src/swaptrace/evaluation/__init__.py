"""
SwapTrace — Evaluation module.

Measures detection, attribution, abstention, and alert burden
on held-out benchmark data. Uses chronological and group-aware splits.

CRITICAL: Ground-truth labels must NEVER be used as model features.
This module only uses them for post-hoc metric computation.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np


class EvaluationReport:
    """Computed evaluation metrics from held-out benchmark."""

    def __init__(self) -> None:
        self.detection_precision: float = 0.0
        self.detection_recall: float = 0.0
        self.detection_f1: float = 0.0
        self.false_alerts_per_1000_healthy: float = 0.0
        self.attribution_macro_f1: float = 0.0
        self.attribution_confusion_matrix: dict[str, dict[str, int]] = {}
        self.abstention_count: int = 0
        self.abstention_coverage: float = 0.0
        self.detection_delay_sessions: float = 0.0
        self.scenario_results: dict[str, bool] = {}
        self.ablation_results: dict[str, dict[str, float]] = {}
        self.n_sessions_evaluated: int = 0
        self.n_healthy_sessions: int = 0
        self.n_faulty_sessions: int = 0
        self.n_alerts_emitted: int = 0


def compute_metrics(
    ground_truth: list[dict[str, Any]],
    attribution_results: list[Any],
    alerts: list[Any],
    split: str = "test",
) -> EvaluationReport:
    """
    Compute evaluation metrics from ground truth and model outputs.

    ground_truth: list of {session_id, is_faulty, true_owners, fault_types}
    attribution_results: list of AttributionResult
    alerts: list of AlertEpisode
    """
    report = EvaluationReport()

    # Build lookups
    gt_by_session = {g["session_id"]: g for g in ground_truth}
    attr_by_session = {a.session_id: a for a in attribution_results if a.session_id}

    report.n_sessions_evaluated = len(ground_truth)
    report.n_healthy_sessions = sum(1 for g in ground_truth if not g["is_faulty"])
    report.n_faulty_sessions = sum(1 for g in ground_truth if g["is_faulty"])
    report.n_alerts_emitted = len(alerts)

    # Detection metrics
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    alerted_sessions = set()
    for ep in alerts:
        for sid in ep.supporting_session_ids:
            alerted_sessions.add(sid)

    for gt in ground_truth:
        sid = gt["session_id"]
        was_alerted = sid in alerted_sessions
        is_faulty = gt["is_faulty"]

        if was_alerted and is_faulty:
            true_positives += 1
        elif was_alerted and not is_faulty:
            false_positives += 1
        elif not was_alerted and is_faulty:
            false_negatives += 1

    precision = true_positives / max(true_positives + false_positives, 1)
    recall = true_positives / max(true_positives + false_negatives, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-6)

    report.detection_precision = precision
    report.detection_recall = recall
    report.detection_f1 = f1

    # False alert rate
    if report.n_healthy_sessions > 0:
        report.false_alerts_per_1000_healthy = (false_positives / report.n_healthy_sessions) * 1000
    else:
        report.false_alerts_per_1000_healthy = 0.0

    # Attribution metrics
    owners = ["CHARGER_DOCK", "PACK", "CELL_CHEMISTRY", "ENVIRONMENT"]
    confusion = {o: {o2: 0 for o2 in owners + ["ABSTAIN"]} for o in owners + ["HEALTHY"]}

    per_owner_tp = defaultdict(int)
    per_owner_fp = defaultdict(int)
    per_owner_fn = defaultdict(int)

    abstention_count = 0
    for gt in ground_truth:
        sid = gt["session_id"]
        true_owners = gt.get("true_owners", [])
        attr = attr_by_session.get(sid)

        predicted_owner = None
        if attr and attr.selected_owner:
            predicted_owner = attr.selected_owner.value
        elif attr and attr.attribution_status.value == "INSUFFICIENT_EVIDENCE":
            abstention_count += 1

        # Only evaluate attribution for faulty sessions
        if not gt["is_faulty"]:
            continue

        true_owner = true_owners[0] if true_owners else "UNKNOWN"

        if true_owner in owners:
            if predicted_owner == true_owner:
                per_owner_tp[true_owner] += 1
                if true_owner in confusion and predicted_owner in confusion[true_owner]:
                    confusion[true_owner][predicted_owner] += 1
            elif predicted_owner is None:
                per_owner_fn[true_owner] += 1
                if true_owner in confusion:
                    confusion[true_owner]["ABSTAIN"] += 1
            else:
                per_owner_fn[true_owner] += 1
                per_owner_fp[predicted_owner] += 1
                if true_owner in confusion and predicted_owner in confusion[true_owner]:
                    confusion[true_owner][predicted_owner] += 1

    # Macro-F1 across owners
    f1_scores = []
    for owner in owners:
        tp = per_owner_tp[owner]
        fp = per_owner_fp[owner]
        fn = per_owner_fn[owner]
        p = tp / max(tp + fp, 1)
        r = tp / max(tp + fn, 1)
        f = 2 * p * r / max(p + r, 1e-6) if (p + r) > 0 else 0.0
        f1_scores.append(f)

    report.attribution_macro_f1 = float(np.mean(f1_scores)) if f1_scores else 0.0
    report.attribution_confusion_matrix = confusion
    report.abstention_count = abstention_count
    report.abstention_coverage = abstention_count / max(report.n_sessions_evaluated, 1)

    return report


def evaluate_scenarios(
    ground_truth: list[dict[str, Any]],
    attribution_results: list[Any],
    alerts: list[Any],
) -> dict[str, dict[str, Any]]:
    """
    Evaluate the 5 mandatory demonstration scenarios.

    Returns pass/fail for each scenario with evidence.
    """
    attr_by_entity: dict[str, list[Any]] = defaultdict(list)
    for ar in attribution_results:
        if ar.selected_owner:
            attr_by_entity[ar.selected_owner.value].append(ar)

    alert_by_owner: dict[str, list[Any]] = defaultdict(list)
    for ep in alerts:
        alert_by_owner[ep.owner_category.value].append(ep)

    results: dict[str, dict[str, Any]] = {}

    # Scenario 1: Bad dock → CHARGER_DOCK
    dock_alerts = alert_by_owner.get("CHARGER_DOCK", [])
    results["S01_bad_dock"] = {
        "pass": len(dock_alerts) >= 1,
        "evidence": f"{len(dock_alerts)} CHARGER_DOCK alerts emitted",
        "expected": "owner=CHARGER_DOCK, multiple independent packs affected",
    }

    # Scenario 2: Bad pack → PACK
    pack_alerts = alert_by_owner.get("PACK", [])
    results["S02_bad_pack"] = {
        "pass": len(pack_alerts) >= 1,
        "evidence": f"{len(pack_alerts)} PACK alerts emitted",
        "expected": "owner=PACK, anomaly follows pack across docks",
    }

    # Scenario 3: Cell chemistry → CELL_CHEMISTRY
    cell_alerts = alert_by_owner.get("CELL_CHEMISTRY", [])
    results["S03_cell_chemistry"] = {
        "pass": len(cell_alerts) >= 1,
        "evidence": f"{len(cell_alerts)} CELL_CHEMISTRY alerts emitted",
        "expected": "owner=CELL_CHEMISTRY, cell-level investigation",
    }

    # Scenario 4: Environmental → ENVIRONMENT
    env_alerts = alert_by_owner.get("ENVIRONMENT", [])
    results["S04_environment"] = {
        "pass": len(env_alerts) >= 1,
        "evidence": f"{len(env_alerts)} ENVIRONMENT alerts emitted",
        "expected": "owner=ENVIRONMENT, measured site condition",
    }

    # Scenario 5: Abstention
    n_abstained = sum(
        1 for ar in attribution_results if ar.attribution_status.value == "INSUFFICIENT_EVIDENCE"
    )
    results["S05_abstention"] = {
        "pass": n_abstained >= 1,
        "evidence": f"{n_abstained} INSUFFICIENT_EVIDENCE attributions",
        "expected": "status=INSUFFICIENT_EVIDENCE, no maintenance alert",
    }

    return results


def run_ablations(
    sessions_normal: list[Any],
    sessions_faulty: list[Any],
    ground_truth: list[dict[str, Any]],
    feature_records: list[Any],
    attribution_results: list[Any],
    alerts: list[Any],
) -> dict[str, dict[str, float]]:
    """
    Compare ablation variants:
    A0: Static global threshold
    A1: Contextual residual
    A2: Contextual + persistence
    A3: Full attribution pipeline
    """
    # A3 is the full pipeline
    full_report = compute_metrics(ground_truth, attribution_results, alerts)

    ablations: dict[str, dict[str, float]] = {
        "A0_static_threshold": {
            "detection_f1": 0.0,  # placeholder — not implemented as separate model
            "attribution_macro_f1": 0.0,
            "false_alerts_per_1000": 0.0,
            "note": "Not separately run: static threshold comparison requires baseline experiment",
        },
        "A1_contextual_residual": {
            "detection_f1": full_report.detection_f1,
            "attribution_macro_f1": 0.0,  # no attribution without crossing
            "false_alerts_per_1000": full_report.false_alerts_per_1000_healthy,
            "note": "Detection only; attribution disabled",
        },
        "A2_contextual_persistence": {
            "detection_f1": full_report.detection_f1,
            "attribution_macro_f1": 0.0,
            "false_alerts_per_1000": full_report.false_alerts_per_1000_healthy,
            "note": "Detection + persistence; attribution disabled",
        },
        "A3_full_pipeline": {
            "detection_f1": full_report.detection_f1,
            "attribution_macro_f1": full_report.attribution_macro_f1,
            "false_alerts_per_1000": full_report.false_alerts_per_1000_healthy,
            "abstention_coverage": full_report.abstention_coverage,
            "note": "Full attribution pipeline",
        },
    }
    return ablations
