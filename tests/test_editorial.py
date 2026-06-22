from __future__ import annotations

import json
from pathlib import Path

from ai_roundtables.editorial import (
    check_published,
    parse_front_matter,
    promote_run,
    publish_transcript,
    render_editorial_check,
    write_published_index,
)


def write_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    manifest = {
        "run": {"mode": "live"},
        "title": "Test Roundtable",
        "date": "2026-05-31",
        "format": "consensus_dissent",
        "audience": "intelligent_lay",
        "turns": 1,
        "moderator_turns": "between_rounds",
        "moderator": {"name": "Moderator", "model": "gpt-test"},
        "participants": [
            {"name": "OpenAI", "provider": "openai", "model": "gpt-test"},
            {
                "name": "Anthropic",
                "provider": "anthropic",
                "model": "claude-test",
            },
        ],
        "executed_turn_records": [
            {
                "speaker": "Moderator",
                "status": "completed",
                "response": "Opening question.",
            },
            {
                "speaker": "OpenAI",
                "status": "completed",
                "response": "OpenAI answer.",
            },
            {
                "speaker": "Anthropic",
                "status": "completed",
                "response": "Anthropic answer.",
            },
        ],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    (run_dir / "transcript.md").write_text("# Test Roundtable\n")


def test_promote_run_writes_transcript_scaffold(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "runs" / "raw" / "test"
    output = tmp_path / "transcripts" / "test.md"
    write_run(run_dir)

    promote_run(run_dir, output)

    metadata, body = parse_front_matter(output.read_text())
    assert metadata["title"] == "Test Roundtable"
    assert metadata["source_run"] == "runs/raw/test"
    assert metadata["models"]["moderator"] == "gpt-test"
    assert "## Moderator" in body
    assert "Opening question." in body


def test_publish_transcript_writes_published_scaffold(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "runs" / "raw" / "test"
    transcript = tmp_path / "transcripts" / "test.md"
    output = tmp_path / "published" / "test.md"
    write_run(run_dir)
    promote_run(run_dir, transcript)

    publish_transcript(transcript, output)

    metadata, body = parse_front_matter(output.read_text())
    assert metadata["source_transcript"] == "transcripts/test.md"
    assert metadata["external_retrieval"]
    assert "<!-- Add a reader-facing introduction here before publishing. -->" in body
    assert "## Roundtable" in body


def test_check_published_validates_required_metadata(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    (transcript_dir / "test.md").write_text("# Transcript\n")
    published = tmp_path / "published.md"
    published.write_text(
        """---
title: "Test"
date: 2026-05-31
source_run: runs/raw/test
source_transcript: transcripts/test.md
format: consensus_dissent
audience: intelligent_lay
models:
  openai: gpt-test
external_retrieval: "No retrieval."
editorial_intervention: "Edited."
---

# Test

See https://example.com/source.

## Editorial Note

Done.
"""
    )

    check = check_published(published, repo_root=tmp_path)

    assert check.passed
    assert check.warnings == ["Source run is not present locally: runs/raw/test"]
    assert "Editorial check: PASS" in render_editorial_check(check)


def test_write_published_index_lists_pieces(tmp_path: Path) -> None:
    published_dir = tmp_path / "published"
    published_dir.mkdir()
    first = published_dir / "first.md"
    first.write_text(
        """---
title: "First"
date: 2026-05-31
source_run: runs/raw/first
series: Series One
models:
  openai: gpt-test
---

# First
"""
    )
    (published_dir / "README.md").write_text("# Published\n")
    output = published_dir / "INDEX.md"

    write_published_index(published_dir, output)

    assert "[First](first.md)" in output.read_text()
    assert "## Series One" in output.read_text()
    assert "`runs/raw/first`" in output.read_text()
