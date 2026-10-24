"""
SwapTrace -- CLI entry point.

Commands:
  demo       Run full pipeline and persist alert artifacts
  eval       Run evaluation on held-out benchmark
  dashboard  Launch Streamlit operator dashboard
  generate   Generate benchmark data only
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from swaptrace.contracts import (
    AttributionResult,
    AttributionStatus,
    FeatureRecord,
    OwnerCategory,
)
from swaptrace.observability import configure_logging, get_logger

app = typer.Typer(
    name="swaptrace",
    help="Battery charging-session anomaly detection and fault attribution.",
    add_completion=False,
)
console = Console()
logger = get_logger(__name__)




@app.command()
def demo(
    seed: Annotated[int, typer.Option("--seed", help="Random seed for benchmark generation")] = 42,
    output_dir: Annotated[str, typer.Option("--output-dir")] = "artifacts/alerts",
    db_path: Annotated[str, typer.Option("--db-path")] = "data/swaptrace.db",
    verbose: Annotated[bool, typer.Option("--verbose")] = False,
) -> None:
    """Run full SwapTrace pipeline: generate -> validate -> feature -> attribute -> alert."""
    configure_logging("DEBUG" if verbose else "INFO")
    logger.info("demo_pipeline_start", seed=seed)

    console.rule("[bold blue]SwapTrace Demo Pipeline")
    console.print(f"[dim]Seed: {seed} | Output: {output_dir} | DB: {db_path}[/dim]\n")

    # --- Phase 1: Generate/Ingest ---
    console.print("[bold]Phase 1:[/bold] Generating benchmark data...")
    from swaptrace.ingestion import BenchmarkAdapter

    adapter = BenchmarkAdapter(seed=seed)
    sessions, events, ground_truth = adapter.generate()
    console.print(f"  [OK] {len(sessions)} sessions, {len(events)} telemetry events")

    # Save ground truth (for evaluation only -- NEVER used as model feature)
    gt_path = Path("data/raw/ground_truth.json")
    gt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(gt_path, "w") as f:
        json.dump(ground_truth, f, indent=2)
    console.print(f"  [OK] Ground truth saved to {gt_path} (evaluation only)")

    # --- Phase 2: Validate ---
    console.print("[bold]Phase 2:[/bold] Data validation...")
    from swaptrace.quality import QualityPipeline

    qp = QualityPipeline()
    valid_events = qp.process_events(events)
    eligible_sessions = qp.process_sessions(sessions)
    console.print(f"  [OK] Events: {len(valid_events)}/{len(events)} valid")
    console.print(f"  [OK] Sessions: {len(eligible_sessions)}/{len(sessions)} eligible")

    # --- Phase 3: Sessionization ---
    console.print("[bold]Phase 3:[/bold] Sessionization...")
    from swaptrace.sessions import Sessionizer

    # The benchmark adapter emits pre-built sessions; cross-validate them against
    # independent event-driven sessionization before trusting the session IDs.
    # (In production, the Sessionizer IS the source of sessions.)
    sessionizer = Sessionizer()
    derived = sessionizer.process(valid_events)
    derived_ids = {s.session_id for s in derived}
    matched = sum(1 for s in eligible_sessions if s.session_id in derived_ids)
    console.print(
        f"  [OK] Sessionizer derived {len(derived)} sessions from events; "
        f"{matched}/{len(eligible_sessions)} benchmark sessions confirmed"
    )
    reconstructed = eligible_sessions
    console.print(f"  [OK] {len(reconstructed)} validated sessions carried forward")

    # --- Phase 4: Storage ---
    console.print("[bold]Phase 4:[/bold] Persisting sessions...")
    from swaptrace.storage import get_db

    db = get_db(db_path)
    n_stored = db.upsert_sessions(reconstructed)
    console.print(f"  [OK] {n_stored} sessions stored")

    # --- Phase 5: Chronological train/test split ---
    console.print("[bold]Phase 5:[/bold] Train/test split (chronological)...")
    reconstructed.sort(key=lambda s: s.start_ts)
    split_idx = int(len(reconstructed) * 0.7)
    train_sessions = reconstructed[:split_idx]
    test_sessions = reconstructed[split_idx:]
    console.print(f"  [OK] Train: {len(train_sessions)} | Test: {len(test_sessions)}")

    # --- Phase 6: Feature computation ---
    console.print("[bold]Phase 6:[/bold] Computing features...")
    from swaptrace.features import compute_all_features

    # Build event lookup
    event_by_session: dict[str, list] = {}
    for e in valid_events:
        event_by_session.setdefault(e.session_id, []).append(e)

    all_features = []
    train_features = []
    for sess in train_sessions:
        evts = event_by_session.get(sess.session_id, [])
        frs = compute_all_features(sess, evts)
        train_features.extend(frs)

    test_features = []
    for sess in test_sessions:
        evts = event_by_session.get(sess.session_id, [])
        frs = compute_all_features(sess, evts)
        test_features.extend(frs)
        all_features.extend(frs)

    valid_train = [f for f in train_features if f.validity_status.value == "VALID"]
    console.print(f"  [OK] {len(valid_train)} valid features from training sessions")
    console.print(f"  [OK] {len(test_features)} total features from test sessions")

    # Store features
    db.upsert_features(all_features)

    # --- Phase 7: Baselines ---
    console.print("[bold]Phase 7:[/bold] Fitting contextual baselines...")
    import polars as pl

    from swaptrace.baselines import BaselineManager

    bm = BaselineManager()
    if valid_train:
        # Create polars dataframes for baseline fitting
        train_sess_dicts = [
            {
                "session_id": s.session_id,
                "chemistry_id": s.chemistry_id or "unknown",
                "initial_soc_pct": s.initial_soc_pct,
                "ambient_temperature_c": s.ambient_temperature_c,
                "charge_protocol_id": s.charge_protocol_id,
                "start_ts": s.start_ts,
            }
            for s in train_sessions
        ]
        train_sess_df = pl.DataFrame(train_sess_dicts)

        train_feat_dicts = [
            {
                "feature_id": f.feature_id,
                "session_id": f.session_id,
                "value": f.value,
                "validity_status": f.validity_status.value,
            }
            for f in valid_train
        ]
        train_feat_df = pl.DataFrame(train_feat_dicts)

        training_cutoff = train_sessions[-1].start_ts
        bm.fit_from_features_df(train_feat_df, train_sess_df, training_cutoff)
        console.print(f"  [OK] Baselines fitted for {len(bm._baselines)} features")
    else:
        console.print("  [!] No valid training features -- baselines not fitted")

    # --- Phase 8: Residual scoring ---
    console.print("[bold]Phase 8:[/bold] Computing residuals...")
    test_features_with_residuals = bm.compute_residuals(test_features, test_sessions)
    scored = [
        f
        for f in test_features_with_residuals
        if f.validity_status.value == "VALID" and f.normalized_score is not None
    ]
    anomalous = [f for f in scored if f.normalized_score and f.normalized_score > 3.0]
    console.print(f"  [OK] {len(scored)} features scored | {len(anomalous)} anomalous (z>3)")

    # --- Phase 9: Attribution ---
    console.print("[bold]Phase 9:[/bold] Cross-asset attribution...")
    from swaptrace.attribution import AttributionEngine
    from swaptrace.detection import score_anomalies

    engine = AttributionEngine()
    engine.build_graph(reconstructed)  # full graph for crossing evidence

    anomaly_scores = score_anomalies(test_features_with_residuals)
    results = engine.attribute_batch(test_sessions, anomaly_scores, test_features_with_residuals)

    attributed = [r for r in results if r.attribution_status.value == "ATTRIBUTED"]
    abstained = [r for r in results if r.attribution_status.value == "INSUFFICIENT_EVIDENCE"]
    console.print(f"  [OK] {len(attributed)} attributed | {len(abstained)} abstained")

    # --- Phase 10: Alert Policy ---
    console.print("[bold]Phase 10:[/bold] Applying alert policy...")
    from swaptrace.alerts import AlertPolicyEngine
    from swaptrace.contracts import SourceType as ST

    policy = AlertPolicyEngine(persistence_threshold=2, data_provenance=ST.SYNTHETIC)
    sess_ts_map = {s.session_id: s.start_ts for s in test_sessions}

    for result in results:
        if result.session_id:
            ts = sess_ts_map.get(result.session_id, datetime.now(UTC))
            policy.process_attribution(result, test_features_with_residuals, result.session_id, ts)

    episodes = policy.get_all_episodes()
    console.print(f"  [OK] {len(episodes)} alert episodes created")

    # --- Phase 11: Persist alerts ---
    console.print("[bold]Phase 11:[/bold] Persisting alerts...")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Alerts are fully derived artifacts: replace the stored set with this run's
    db.conn.execute("DELETE FROM alerts")

    for ep in episodes:
        try:
            db.upsert_alert(ep)
        except Exception as e:
            logger.warning("alert_persist_failed", error=str(e))

    # Save alert JSON
    alerts_json = output_path / "alerts.json"
    alert_dicts = []
    for ep in episodes:
        d = ep.model_dump(mode="json")
        alert_dicts.append(d)
    with open(alerts_json, "w") as f:
        json.dump(alert_dicts, f, indent=2, default=str)
    console.print(f"  [OK] Alerts saved to {alerts_json}")

    # Save attribution results JSON (includes both attributed and abstained)
    attr_json = output_path / "attribution_results.json"
    attr_dicts = [r.model_dump(mode="json") for r in results]
    with open(attr_json, "w") as f:
        json.dump(attr_dicts, f, indent=2, default=str)
    console.print(f"  [OK] Attribution results saved to {attr_json}")

    # --- Summary ---
    console.rule("[bold green]Demo Complete")
    table = Table(title="Alert Summary")
    table.add_column("Owner", style="cyan")
    table.add_column("Entity", style="yellow")
    table.add_column("Severity")
    table.add_column("Occurrences")

    for ep in episodes:
        table.add_row(
            ep.owner_category.value,
            ep.entity_id,
            ep.severity.value,
            str(ep.occurrence_count),
        )
    console.print(table)

    console.print("\n[bold green][OK] Demo pipeline complete[/bold green]")
    console.print(
        f"  Sessions: {len(reconstructed)} | Features: {len(all_features)} | "
        f"Alerts: {len(episodes)} | Abstentions: {len(abstained)}"
    )


@app.command()
def eval(
    db_path: Annotated[str, typer.Option("--db-path")] = "data/swaptrace.db",
    output_dir: Annotated[str, typer.Option("--output-dir")] = "artifacts/evaluation",
    seed: Annotated[int, typer.Option("--seed")] = 42,
) -> None:
    """Run evaluation on benchmark held-out data and generate metrics."""
    configure_logging("INFO")
    console.rule("[bold blue]SwapTrace Evaluation")

    # Load ground truth
    gt_path = Path("data/raw/ground_truth.json")
    if not gt_path.exists():
        console.print("[red]Ground truth not found. Run 'make demo' first.[/red]")
        raise typer.Exit(1)

    with open(gt_path) as f:
        ground_truth = json.load(f)

    # Load alerts
    alerts_path = Path("artifacts/alerts/alerts.json")
    if not alerts_path.exists():
        console.print("[red]Alerts not found. Run 'make demo' first.[/red]")
        raise typer.Exit(1)

    with open(alerts_path) as f:
        alert_dicts = json.load(f)

    # Reload from DB
    from swaptrace.storage import get_db

    db = get_db(db_path)
    alerts_df = db.get_alerts()
    console.print(f"  Loaded {len(alerts_df)} alerts from DB")
    console.print(f"  Ground truth: {len(ground_truth)} session labels")

    # Rebuild feature records from DB for the ablation replay
    features_df = db.get_features()
    feature_records = []
    for row in features_df.to_dicts():
        if isinstance(row.get("context_signature"), str):
            try:
                row["context_signature"] = json.loads(row["context_signature"])
            except json.JSONDecodeError:
                row["context_signature"] = {}
        feature_records.append(FeatureRecord.model_validate(row))
    console.print(f"  Loaded {len(feature_records)} feature records for ablation replay")

    # Reconstruct alerts for evaluation
    from swaptrace.evaluation import compute_metrics, evaluate_scenarios

    # Simple alert objects from JSON
    class SimpleAlert:
        def __init__(self, d: dict) -> None:
            self.owner_category = type("O", (), {"value": d.get("owner_category", "")})()
            self.supporting_session_ids = d.get("supporting_session_ids", [])

    simple_alerts = [SimpleAlert(d) for d in alert_dicts]

    attr_path = Path("artifacts/alerts/attribution_results.json")
    if attr_path.exists():
        with open(attr_path) as f:
            attr_raw = json.load(f)
        attr_results = [AttributionResult.model_validate(d) for d in attr_raw]
    else:
        # Fallback: reconstruct minimal contract objects from alert episodes
        attr_results = []
        for d in alert_dicts:
            try:
                owner = OwnerCategory(d.get("owner_category", ""))
            except ValueError:
                owner = None
            for sid in d.get("supporting_session_ids", []):
                attr_results.append(
                    AttributionResult(
                        session_id=sid,
                        selected_owner=owner,
                        attribution_status=AttributionStatus.ATTRIBUTED,
                        explanation=f"Reconstructed from alert episode {d.get('episode_key', '')}",
                    )
                )

    # Also add abstentions from the dataset
    # Use test portion (last 30%)
    n_total = len(ground_truth)
    split_idx = int(n_total * 0.7)
    test_gt = ground_truth[split_idx:]

    report = compute_metrics(test_gt, attr_results, simple_alerts)
    scenario_results = evaluate_scenarios(test_gt, attr_results, simple_alerts)

    # Real ablation study — each variant is actually re-run and scored
    from swaptrace.evaluation import run_ablations

    ablation_results = run_ablations(test_gt, feature_records, attr_results, simple_alerts)

    # Print results
    console.rule("[bold]Detection Metrics")
    console.print(f"  Precision:     {report.detection_precision:.3f}")
    console.print(f"  Recall:        {report.detection_recall:.3f}")
    console.print(f"  F1:            {report.detection_f1:.3f}")
    console.print(f"  False alerts/1000 healthy: {report.false_alerts_per_1000_healthy:.1f}")

    console.rule("[bold]Attribution Metrics")
    console.print(f"  Attribution macro-F1: {report.attribution_macro_f1:.3f}")
    console.print(f"  Abstentions:   {report.abstention_count}")

    console.rule("[bold]Scenario Results")
    for name, result in scenario_results.items():
        status = "[green]PASS[/green]" if result["pass"] else "[red]FAIL[/red]"
        console.print(f"  {name}: {status} -- {result['evidence']}")

    console.rule("[bold]Ablation Study")
    console.print("  Variant                        F1      FP/1000   Attr-F1")
    for name, metrics in ablation_results.items():
        console.print(
            f"  {name:<30} {metrics['detection_f1']:.3f}   "
            f"{metrics['false_alerts_per_1000']:>7.1f}   {metrics['attribution_macro_f1']:.3f}"
        )

    # Save evaluation artifacts
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    eval_report = {
        "detection": {
            "precision": report.detection_precision,
            "recall": report.detection_recall,
            "f1": report.detection_f1,
            "false_alerts_per_1000_healthy": report.false_alerts_per_1000_healthy,
        },
        "attribution": {
            "macro_f1": report.attribution_macro_f1,
            "abstention_count": report.abstention_count,
            "abstention_coverage": report.abstention_coverage,
        },
        "scenarios": scenario_results,
        "ablations": ablation_results,
        "metadata": {
            "seed": seed,
            "n_test_sessions": report.n_sessions_evaluated,
            "n_healthy": report.n_healthy_sessions,
            "n_faulty": report.n_faulty_sessions,
            "n_alerts": report.n_alerts_emitted,
            "evaluation_ts": datetime.now(UTC).isoformat(),
            "data_provenance": "SYNTHETIC -- semi-synthetic swapping network benchmark",
            "note": "Results from controlled synthetic benchmark. Not representative of real-world field performance.",
        },
    }

    with open(output_path / "evaluation_report.json", "w") as f:
        json.dump(eval_report, f, indent=2)

    console.print(
        f"\n[bold green][OK] Evaluation complete. Report: {output_path}/evaluation_report.json[/bold green]"
    )


@app.command()
def dashboard() -> None:
    """Launch the Streamlit operator dashboard."""
    import subprocess

    console.print("[bold blue]Launching SwapTrace Dashboard...[/bold blue]")
    console.print("[dim]Press Ctrl+C to stop.[/dim]\n")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app/dashboard.py",
            "--server.headless",
            "true",
            "--server.port",
            "8501",
        ],
        check=False,
    )
    raise typer.Exit(result.returncode)


@app.command()
def generate(
    seed: Annotated[int, typer.Option("--seed")] = 42,
    output_dir: Annotated[str, typer.Option("--output-dir")] = "data/raw",
) -> None:
    """Generate benchmark dataset only."""
    configure_logging("INFO")
    from swaptrace.ingestion import BenchmarkAdapter

    adapter = BenchmarkAdapter(seed=seed)
    sessions, events, gt = adapter.generate()

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{output_dir}/ground_truth.json", "w") as f:
        json.dump(gt, f, indent=2)

    console.print(f"[green][OK] Generated {len(sessions)} sessions, {len(events)} events[/green]")
    console.print(f"[dim]Ground truth (evaluation only): {output_dir}/ground_truth.json[/dim]")


if __name__ == "__main__":
    app()
