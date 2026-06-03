from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from ai_roundtables.orchestrator import ConfigError, DraftOrchestrator


def write_fixture_repo(tmp_path: Path) -> Path:
    (tmp_path / "prompts").mkdir()
    (tmp_path / "notes").mkdir()
    (tmp_path / "schemas").mkdir()
    schema = (
        Path(__file__).resolve().parents[1]
        / "schemas"
        / "roundtable-run.schema.json"
    ).read_text()
    (tmp_path / "schemas" / "roundtable-run.schema.json").write_text(schema)
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
                "output_tokens": 640,
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
    assert config.audio_intent == "none"
    assert config.source_packet == []
    assert config.config_snapshot["slug"] == "test-roundtable"
    assert [participant.name for participant in config.participants] == [
        "OpenAI",
        "Anthropic",
    ]
    assert config.participants[0].output_tokens == 640
    assert config.participants[1].output_tokens is None
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
    assert manifest["source_packet"] == []
    assert manifest["moderator_turns"] == "none"
    assert manifest["audio_intent"] == "none"
    assert manifest["run"]["mode"] == "draft"
    assert manifest["run"]["slug"] == "test-roundtable"
    assert manifest["run"]["package_version"]
    datetime.fromisoformat(manifest["run"]["generated_at"])
    assert manifest["config_snapshot"]["slug"] == "test-roundtable"
    prompt_files = {item["path"]: item["sha256"] for item in manifest["prompt_files"]}
    assert set(prompt_files) == {"prompts/moderator.md", "prompts/participant.md"}
    assert all(len(value) == 64 for value in prompt_files.values())
    assert len(manifest["planned_turn_records"]) == 4
    assert "# Test Roundtable" in transcript
    assert transcript.count("_Response pending._") == 4


def test_write_draft_run_can_include_visible_moderator_turns(
    tmp_path: Path,
) -> None:
    config_path = write_fixture_repo(tmp_path)
    raw = json.loads(config_path.read_text())
    raw["moderator"]["provider"] = "openai"
    raw["moderator"]["model"] = "gpt-moderator"
    raw["moderator"]["output_tokens"] = 256
    raw["moderator_turns"] = "between_rounds"
    config_path.write_text(json.dumps(raw))
    output_dir = tmp_path / "runs" / "raw" / "moderated-draft"
    orchestrator = DraftOrchestrator(repo_root=tmp_path)

    config = orchestrator.load_config(config_path)
    orchestrator.write_draft_run(config, output_dir)

    manifest = json.loads((output_dir / "manifest.json").read_text())
    transcript = (output_dir / "transcript.stub.md").read_text()
    records = manifest["planned_turn_records"]
    assert manifest["moderator_turns"] == "between_rounds"
    assert manifest["moderator"]["model"] == "gpt-moderator"
    assert manifest["moderator"]["output_tokens"] == 256
    assert len(records) == 6
    assert [record["speaker"] for record in records] == [
        "Moderator",
        "OpenAI",
        "Anthropic",
        "Moderator",
        "OpenAI",
        "Anthropic",
    ]
    assert "### Moderator" in transcript


def test_audio_intent_adds_listener_guidance_to_prompts(tmp_path: Path) -> None:
    config_path = write_fixture_repo(tmp_path)
    raw = json.loads(config_path.read_text())
    raw["audio_intent"] = "podcast_adaptable"
    raw["moderator_turns"] = "between_rounds"
    config_path.write_text(json.dumps(raw))
    output_dir = tmp_path / "runs" / "raw" / "audio-draft"
    orchestrator = DraftOrchestrator(repo_root=tmp_path)

    config = orchestrator.load_config(config_path)
    orchestrator.write_draft_run(config, output_dir)

    manifest = json.loads((output_dir / "manifest.json").read_text())
    prompts = [record["prompt"] for record in manifest["planned_turn_records"]]
    assert manifest["audio_intent"] == "podcast_adaptable"
    assert config.audio_intent == "podcast_adaptable"
    assert any("may later become an audio roundtable" in prompt for prompt in prompts)
    assert any("listener-facing clarification" in prompt for prompt in prompts)


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


def test_run_live_skips_visible_moderator_without_key(
    tmp_path: Path, monkeypatch
) -> None:
    config_path = write_fixture_repo(tmp_path)
    raw = json.loads(config_path.read_text())
    raw["moderator_turns"] = "between_rounds"
    raw["turns"] = 1
    config_path.write_text(json.dumps(raw))
    output_dir = tmp_path / "runs" / "raw" / "moderated-live"
    orchestrator = DraftOrchestrator(repo_root=tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    config = orchestrator.load_config(config_path)
    orchestrator.run_live(config, output_dir)

    manifest = json.loads((output_dir / "manifest.json").read_text())
    records = manifest["executed_turn_records"]
    assert [record["speaker"] for record in records] == [
        "Moderator",
        "OpenAI",
        "Anthropic",
    ]
    assert [record["status"] for record in records] == [
        "skipped_missing_key",
        "skipped_missing_key",
        "skipped_missing_key",
    ]


def test_load_config_rejects_schema_errors(tmp_path: Path) -> None:
    config_path = write_fixture_repo(tmp_path)
    raw = json.loads(config_path.read_text())
    raw["turns"] = 0
    raw["participants"] = raw["participants"][:1]
    raw["unknown"] = "not allowed"
    config_path.write_text(json.dumps(raw))

    orchestrator = DraftOrchestrator(repo_root=tmp_path)

    try:
        orchestrator.load_config(config_path)
    except ConfigError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ConfigError")

    assert "Invalid roundtable config" in message
    assert "participants" in message
    assert "turns" in message
    assert "unknown" in message


def test_load_config_rejects_missing_prompt_files(tmp_path: Path) -> None:
    config_path = write_fixture_repo(tmp_path)
    raw = json.loads(config_path.read_text())
    raw["participants"][0]["prompt_file"] = "prompts/missing.md"
    config_path.write_text(json.dumps(raw))

    orchestrator = DraftOrchestrator(repo_root=tmp_path)

    try:
        orchestrator.load_config(config_path)
    except ConfigError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ConfigError")

    assert "missing prompt file(s): prompts/missing.md" in message


def test_load_config_rejects_invalid_json(tmp_path: Path) -> None:
    (tmp_path / "schemas").mkdir()
    schema = (
        Path(__file__).resolve().parents[1]
        / "schemas"
        / "roundtable-run.schema.json"
    ).read_text()
    (tmp_path / "schemas" / "roundtable-run.schema.json").write_text(schema)
    config_path = tmp_path / "broken.json"
    config_path.write_text("not json")

    orchestrator = DraftOrchestrator(repo_root=tmp_path)

    try:
        orchestrator.load_config(config_path)
    except ConfigError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ConfigError")

    assert "Invalid JSON config" in message
    assert "line 1 column 1" in message
