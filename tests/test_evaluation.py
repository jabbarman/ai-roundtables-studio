from __future__ import annotations

import json
from pathlib import Path

from ai_roundtables.evaluation import evaluate_run, format_evaluation
from ai_roundtables.orchestrator import DraftOrchestrator
from test_orchestrator import write_fixture_repo


def test_evaluate_draft_run_passes(tmp_path: Path) -> None:
    config_path = write_fixture_repo(tmp_path)
    output_dir = tmp_path / "runs" / "raw" / "draft"
    orchestrator = DraftOrchestrator(repo_root=tmp_path)
    config = orchestrator.load_config(config_path)
    orchestrator.write_draft_run(config, output_dir)

    evaluation = evaluate_run(output_dir)

    assert evaluation.passed
    assert evaluation.mode == "draft"
    assert evaluation.record_count == 4
    assert evaluation.status_counts == {"pending": 4}
    assert "Run evaluation: PASS" in format_evaluation(evaluation)


def test_evaluate_live_run_reports_provider_errors(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "raw" / "failed"
    run_dir.mkdir(parents=True)
    manifest = {
        "run": {"mode": "live"},
        "turns": 1,
        "participants": [{"name": "A"}, {"name": "B"}],
        "executed_turn_records": [
            {
                "speaker": "A",
                "status": "completed",
                "response": "Useful response.",
            },
            {
                "speaker": "B",
                "status": "error_http",
                "response": "[Provider failed.]",
            },
        ],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    (run_dir / "transcript.md").write_text("# Transcript\n")

    evaluation = evaluate_run(run_dir)

    assert not evaluation.passed
    assert evaluation.status_counts == {"completed": 1, "error_http": 1}
    assert evaluation.issues == ["B ended with provider error status: error_http"]


def test_evaluate_missing_manifest_fails(tmp_path: Path) -> None:
    evaluation = evaluate_run(tmp_path / "missing")

    assert not evaluation.passed
    assert "Missing manifest" in evaluation.issues[0]
