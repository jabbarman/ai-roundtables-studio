from __future__ import annotations

from pathlib import Path
import pytest

from ai_roundtables import cli
from test_orchestrator import write_fixture_repo


def test_cli_uses_current_directory_for_project_assets(
    tmp_path: Path, monkeypatch
) -> None:
    config_path = write_fixture_repo(tmp_path)
    output_dir = tmp_path / "runs" / "raw" / "cli"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        [
            "ai-roundtables",
            "draft",
            str(config_path.relative_to(tmp_path)),
            "--output-dir",
            str(output_dir.relative_to(tmp_path)),
        ],
    )

    assert cli.main() == 0
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "transcript.stub.md").exists()


def test_cli_version(monkeypatch, capsys) -> None:
    monkeypatch.setattr("sys.argv", ["ai-roundtables", "--version"])

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 0
    assert "ai-roundtables 0.9.1" in capsys.readouterr().out


def test_cli_eval_returns_zero_for_valid_draft_run(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    config_path = write_fixture_repo(tmp_path)
    output_dir = tmp_path / "runs" / "raw" / "cli-eval"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        [
            "ai-roundtables",
            "draft",
            str(config_path.relative_to(tmp_path)),
            "--output-dir",
            str(output_dir.relative_to(tmp_path)),
        ],
    )
    assert cli.main() == 0

    monkeypatch.setattr(
        "sys.argv",
        ["ai-roundtables", "eval", str(output_dir.relative_to(tmp_path))],
    )

    assert cli.main() == 0
    assert "Run evaluation: PASS" in capsys.readouterr().out


def test_cli_promote_publish_check_and_index(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    run_dir = tmp_path / "runs" / "raw" / "editorial"
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(
        """{
  "run": {"mode": "live"},
  "title": "Editorial Test",
  "date": "2026-05-31",
  "format": "roundtable",
  "audience": "intelligent_lay",
  "turns": 1,
  "moderator": {"name": "Moderator", "model": "gpt-test"},
  "participants": [{"name": "OpenAI", "provider": "openai", "model": "gpt-test"}],
  "executed_turn_records": [
    {"speaker": "OpenAI", "status": "completed", "response": "A substantial answer."}
  ]
}
"""
    )
    (run_dir / "transcript.md").write_text("# Editorial Test\n")
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "ai-roundtables",
            "promote",
            "runs/raw/editorial",
            "--output",
            "transcripts/editorial.md",
        ],
    )
    assert cli.main() == 0

    monkeypatch.setattr(
        "sys.argv",
        [
            "ai-roundtables",
            "publish",
            "transcripts/editorial.md",
            "--output",
            "published/editorial.md",
        ],
    )
    assert cli.main() == 0
    published = tmp_path / "published" / "editorial.md"
    published.write_text(
        published.read_text().replace(
            "<!-- Add a reader-facing introduction here before publishing. -->",
            "Intro with https://example.com/source.",
        )
        + "\n## Editorial Note\n\nDone.\n"
    )

    monkeypatch.setattr(
        "sys.argv",
        ["ai-roundtables", "check", "published/editorial.md"],
    )
    assert cli.main() == 0
    assert "Editorial check: PASS" in capsys.readouterr().out

    monkeypatch.setattr(
        "sys.argv",
        ["ai-roundtables", "index", "--published-dir", "published"],
    )
    assert cli.main() == 0
    assert (tmp_path / "published" / "INDEX.md").exists()
