from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REQUIRED_PUBLISHED_FIELDS = [
    "title",
    "date",
    "source_run",
    "source_transcript",
    "format",
    "audience",
    "models",
    "external_retrieval",
    "editorial_intervention",
]


@dataclass(slots=True)
class EditorialCheck:
    path: str
    passed: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def promote_run(run_dir: Path, output_path: Path) -> None:
    manifest = _read_manifest(run_dir)
    records = manifest.get("executed_turn_records") or manifest.get(
        "planned_turn_records", []
    )
    source_run = _repo_relative(run_dir)
    front_matter = {
        "title": manifest["title"],
        "date": manifest["date"],
        "source_run": source_run,
        "format": manifest["format"],
        "audience": manifest["audience"],
        "models": _models_from_manifest(manifest),
        "editorial_status": "cleaned transcript",
        "editorial_intervention": (
            "Formatting and punctuation cleanup only; substance and turn order preserved."
        ),
    }
    lines = [
        render_front_matter(front_matter),
        f"# {manifest['title']}",
        "",
    ]
    for record in records:
        lines.extend(
            [
                f"## {record.get('speaker', 'Unknown')}",
                "",
                (record.get("response") or "_Response pending._").strip(),
                "",
            ]
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).strip() + "\n")


def publish_transcript(transcript_path: Path, output_path: Path) -> None:
    metadata, body = parse_front_matter(transcript_path.read_text())
    if not metadata:
        raise ValueError(f"Transcript has no front matter: {transcript_path}")
    source_transcript = _repo_relative(transcript_path)
    published_metadata = {
        "title": metadata["title"],
        "date": metadata["date"],
        "source_run": metadata["source_run"],
        "source_transcript": source_transcript,
        "format": metadata["format"],
        "audience": metadata["audience"],
        "models": metadata.get("models", {}),
        "external_retrieval": "No live retrieval during model turns; source packet supplied in prompt.",
        "editorial_intervention": "Edited for flow, punctuation, and reader orientation; speaker order and substantive claims preserved.",
    }
    body_lines = body.strip().splitlines()
    intro = [
        render_front_matter(published_metadata),
        f"# {metadata['title']}",
        "",
        "<!-- Add a reader-facing introduction here before publishing. -->",
        "",
        "## Roundtable",
        "",
    ]
    if body_lines and body_lines[0].startswith("# "):
        body_lines = body_lines[1:]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(intro + body_lines).strip() + "\n")


def check_published(path: Path, repo_root: Path | None = None) -> EditorialCheck:
    repo_root = repo_root or Path.cwd()
    issues: list[str] = []
    warnings: list[str] = []
    if not path.is_file():
        return EditorialCheck(str(path), False, [f"Missing file: {path}"], [])

    metadata, body = parse_front_matter(path.read_text())
    if not metadata:
        issues.append("Missing front matter")
    for field_name in REQUIRED_PUBLISHED_FIELDS:
        if field_name not in metadata:
            issues.append(f"Missing front matter field: {field_name}")

    source_run = metadata.get("source_run")
    if source_run and not (repo_root / source_run).exists():
        warnings.append(f"Source run is not present locally: {source_run}")
    source_transcript = metadata.get("source_transcript")
    if source_transcript and not (repo_root / source_transcript).is_file():
        issues.append(f"Source transcript not found: {source_transcript}")

    if "[Skipped:" in body or "error_" in body:
        issues.append("Published body contains skipped/error provider text")
    if "## Editorial Note" not in body:
        issues.append("Missing Editorial Note section")
    if "<!--" in body:
        warnings.append("Published body contains template comments")
    if "http" not in body:
        warnings.append("Published body contains no source links")

    return EditorialCheck(str(path), not issues, issues, warnings)


def render_editorial_check(check: EditorialCheck) -> str:
    lines = [f"Editorial check: {'PASS' if check.passed else 'FAIL'}", check.path]
    if check.issues:
        lines.append("Issues:")
        lines.extend(f"- {issue}" for issue in check.issues)
    if check.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in check.warnings)
    return "\n".join(lines)


def write_published_index(published_dir: Path, output_path: Path) -> None:
    entries = []
    for path in sorted(published_dir.glob("*.md")):
        if path.name.upper() in {"README.MD", "INDEX.MD"}:
            continue
        metadata, _body = parse_front_matter(path.read_text())
        if not metadata:
            continue
        entries.append((path, metadata))

    lines = ["# Published Roundtables", ""]
    grouped_entries: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for path, metadata in entries:
        series = metadata.get("series", "Other")
        grouped_entries.setdefault(series, []).append((path, metadata))

    for series in sorted(grouped_entries, key=_published_series_sort_key):
        lines.extend(
            [
                f"## {series}",
                "",
                "| Date | Title | Models | Source Run |",
                "| --- | --- | --- | --- |",
            ]
        )
        for path, metadata in sorted(
            grouped_entries[series],
            key=lambda item: (item[1].get("date", ""), item[1].get("title", "")),
        ):
            models = metadata.get("models", {})
            model_text = ", ".join(f"{key}: {value}" for key, value in models.items())
            lines.append(
                f"| {metadata.get('date', '')} | "
                f"[{metadata.get('title', path.stem)}]({path.name}) | "
                f"{model_text} | `{metadata.get('source_run', '')}` |"
            )
        lines.append("")
    output_path.write_text("\n".join(lines).strip() + "\n")


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    metadata_text = text[4:end]
    body = text[end + 5 :]
    return parse_simple_yaml(metadata_text), body


def parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current_map: dict[str, str] | None = None
    for line in text.splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and current_map is not None:
            key, value = line.strip().split(":", 1)
            current_map[key.strip()] = _unquote(value.strip())
            continue
        current_map = None
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            root[key] = _unquote(value)
        else:
            root[key] = {}
            current_map = root[key]
    return root


def render_front_matter(metadata: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for child_key, child_value in value.items():
                lines.append(f"  {child_key}: {child_value}")
        else:
            lines.append(f"{key}: {json.dumps(value) if _needs_quotes(value) else value}")
    lines.append("---")
    return "\n".join(lines)


def _read_manifest(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"Missing manifest: {manifest_path}")
    return json.loads(manifest_path.read_text())


def _models_from_manifest(manifest: dict[str, Any]) -> dict[str, str]:
    models: dict[str, str] = {}
    moderator = manifest.get("moderator", {})
    if manifest.get("moderator_turns") == "between_rounds":
        models["moderator"] = moderator.get("model", "")
    for participant in manifest.get("participants", []):
        models[participant["provider"]] = participant["model"]
    return models


def _published_series_sort_key(series: str) -> tuple[int, str]:
    priority = {
        "Series One": 0,
        "Pilot / Archive": 1,
        "Other": 2,
    }
    return (priority.get(series, 99), series)


def _repo_relative(path: Path) -> str:
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def _needs_quotes(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return any(character in value for character in [":", '"', "'", ";"])
