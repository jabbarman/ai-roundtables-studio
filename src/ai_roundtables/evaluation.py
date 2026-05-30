from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RunEvaluation:
    run_dir: str
    passed: bool
    mode: str
    record_count: int
    status_counts: dict[str, int] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_run(run_dir: Path) -> RunEvaluation:
    issues: list[str] = []
    warnings: list[str] = []
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        return RunEvaluation(
            run_dir=str(run_dir),
            passed=False,
            mode="unknown",
            record_count=0,
            issues=[f"Missing manifest: {manifest_path}"],
        )

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        return RunEvaluation(
            run_dir=str(run_dir),
            passed=False,
            mode="unknown",
            record_count=0,
            issues=[
                f"Invalid manifest JSON: line {exc.lineno} column {exc.colno}: {exc.msg}"
            ],
        )

    mode = manifest.get("run", {}).get("mode", "unknown")
    records_key = "executed_turn_records"
    transcript_name = "transcript.md"
    if records_key not in manifest:
        records_key = "planned_turn_records"
        transcript_name = "transcript.stub.md"
    records = manifest.get(records_key, [])
    status_counts = Counter(record.get("status", "unknown") for record in records)

    transcript_path = run_dir / transcript_name
    if not transcript_path.is_file():
        issues.append(f"Missing transcript: {transcript_path}")

    expected_records = manifest.get("turns", 0) * len(manifest.get("participants", []))
    if expected_records and len(records) != expected_records:
        issues.append(
            f"Expected {expected_records} turn records, found {len(records)}"
        )
    if not records:
        issues.append("No turn records found")

    for index, record in enumerate(records, start=1):
        speaker = record.get("speaker", f"record {index}")
        status = record.get("status", "unknown")
        response = record.get("response", "")
        if status.startswith("error_"):
            issues.append(f"{speaker} ended with provider error status: {status}")
        elif status.startswith("skipped_"):
            warnings.append(f"{speaker} was skipped: {status}")
        elif status == "completed" and not response.strip():
            issues.append(f"{speaker} completed with an empty response")

    return RunEvaluation(
        run_dir=str(run_dir),
        passed=not issues,
        mode=mode,
        record_count=len(records),
        status_counts=dict(status_counts),
        issues=issues,
        warnings=warnings,
    )


def format_evaluation(evaluation: RunEvaluation) -> str:
    lines = [
        f"Run evaluation: {'PASS' if evaluation.passed else 'FAIL'}",
        f"Run directory: {evaluation.run_dir}",
        f"Mode: {evaluation.mode}",
        f"Turn records: {evaluation.record_count}",
    ]
    if evaluation.status_counts:
        statuses = ", ".join(
            f"{status}={count}"
            for status, count in sorted(evaluation.status_counts.items())
        )
        lines.append(f"Statuses: {statuses}")
    if evaluation.issues:
        lines.append("Issues:")
        lines.extend(f"- {issue}" for issue in evaluation.issues)
    if evaluation.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in evaluation.warnings)
    return "\n".join(lines)
