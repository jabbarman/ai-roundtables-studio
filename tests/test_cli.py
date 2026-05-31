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
    assert "ai-roundtables 0.3.0" in capsys.readouterr().out


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
