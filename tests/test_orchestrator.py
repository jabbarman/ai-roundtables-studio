from __future__ import annotations

import json
from pathlib import Path

from ai_roundtables.orchestrator import DraftOrchestrator


def write_fixture_repo(tmp_path: Path) -> Path:
    (tmp_path / "prompts").mkdir()
    (tmp_path / "notes").mkdir()
    (tmp_path / "prompts" / "moderator.md").write_text("Moderate firmly.\n")
    (tmp_path / "prompts" / "participant.md").write_text("Argue clearly.\n")
    config = {
        "slug": "test-roundtable",
        "title": "Test Roundtable",
        "date": "2026-04-12",
        "audience": "intelligent_lay",
        "format": "roundtable",
        "topic": "How should the pipeline behave?",
        "brief": "Keep it practical.",
        "moderator": {
            "name": "Moderator",
            "prompt_file": "prompts/moderator.md",
        },
        "participants": [
            {
                "name": "OpenAI",
                "provider": "openai",
                "model": "gpt-test",
                "prompt_file": "prompts/participant.md",
                "stance": "Pragmatic.",
            },
            {
                "name": "Anthropic",
                "provider": "anthropic",
                "model": "claude-test",
                "prompt_file": "prompts/participant.md",
                "stance": "Cautious.",
            },
        ],
        "editorial_goals": ["Show disagreement."],
        "turns": 2,
    }
    (tmp_path / "notes" / "config.json").write_text(json.dumps(config))
    return tmp_path / "notes" / "config.json"


def test_load_config_and_build_turn_plan(tmp_path: Path) -> None:
    config_path = write_fixture_repo(tmp_path)
    orchestrator = DraftOrchestrator(repo_root=tmp_path)

    config = orchestrator.load_config(config_path)
    plan = orchestrator.build_turn_plan(config)

    assert config.slug == "test-roundtable"
    assert config.turns == 2
    assert [participant.name for participant in config.participants] == [
        "OpenAI",
        "Anthropic",
    ]
    assert len(plan) == 4
    assert "Roundtable title: Test Roundtable" in plan[0].prompt
    assert "Conversation so far:\nNo prior turns yet." in plan[0].prompt


def test_write_draft_run_writes_manifest_and_stub(tmp_path: Path) -> None:
    config_path = write_fixture_repo(tmp_path)
    output_dir = tmp_path / "runs" / "raw" / "draft"
    orchestrator = DraftOrchestrator(repo_root=tmp_path)

    config = orchestrator.load_config(config_path)
    orchestrator.write_draft_run(config, output_dir)

    manifest = json.loads((output_dir / "manifest.json").read_text())
    transcript = (output_dir / "transcript.stub.md").read_text()
    assert manifest["slug"] == "test-roundtable"
    assert len(manifest["planned_turn_records"]) == 4
    assert "# Test Roundtable" in transcript
    assert transcript.count("_Response pending._") == 4


def test_run_live_skips_participants_without_keys(
    tmp_path: Path, monkeypatch
) -> None:
    config_path = write_fixture_repo(tmp_path)
    output_dir = tmp_path / "runs" / "raw" / "live"
    orchestrator = DraftOrchestrator(repo_root=tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    config = orchestrator.load_config(config_path)
    orchestrator.run_live(config, output_dir)

    manifest = json.loads((output_dir / "manifest.json").read_text())
    statuses = [record["status"] for record in manifest["executed_turn_records"]]
    transcript = (output_dir / "transcript.md").read_text()
    assert statuses == ["skipped_missing_key"] * 4
    assert "OpenAI (openai:gpt-test, skipped_missing_key)" in transcript
    assert "Anthropic (anthropic:claude-test, skipped_missing_key)" in transcript


def test_extract_openai_text_supports_known_response_shapes(tmp_path: Path) -> None:
    orchestrator = DraftOrchestrator(repo_root=tmp_path)

    assert orchestrator._extract_openai_text({"output_text": " Direct text "}) == (
        "Direct text"
    )
    assert (
        orchestrator._extract_openai_text(
            {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "First"},
                            {"type": "output_text", "text": "Second"},
                        ],
                    }
                ]
            }
        )
        == "First\n\nSecond"
    )
