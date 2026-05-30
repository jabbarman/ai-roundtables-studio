from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, date, datetime
import hashlib
from importlib.metadata import PackageNotFoundError, version
import os
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from .models import ModeratorConfig, ParticipantConfig, RoundtableConfig, TurnRecord
from .providers import provider_adapter_for


class ConfigError(ValueError):
    """Raised when a roundtable config is invalid or incomplete."""


class DraftOrchestrator:
    """Build prompt materials and transcript stubs for a roundtable run.

    This is intentionally lightweight. It prepares the structure for a run
    without locking the project to any one provider SDK yet.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self._env_loaded = False

    def load_config(self, config_path: Path) -> RoundtableConfig:
        try:
            raw = json.loads(config_path.read_text())
        except FileNotFoundError as exc:
            raise ConfigError(f"Config file not found: {config_path}") from exc
        except json.JSONDecodeError as exc:
            raise ConfigError(
                f"Invalid JSON config: {config_path}: "
                f"line {exc.lineno} column {exc.colno}: {exc.msg}"
            ) from exc
        self._validate_config(raw)
        self._validate_prompt_files(raw)
        moderator_raw = raw["moderator"]
        participants_raw = raw["participants"]

        moderator = ModeratorConfig(
            name=moderator_raw["name"],
            prompt_file=moderator_raw["prompt_file"],
        )
        participants = [
            ParticipantConfig(
                name=item["name"],
                provider=item["provider"],
                model=item["model"],
                prompt_file=item["prompt_file"],
                stance=item["stance"],
                temperature=item.get("temperature"),
            )
            for item in participants_raw
        ]

        return RoundtableConfig(
            slug=raw["slug"],
            title=raw["title"],
            date=date.fromisoformat(raw["date"]),
            audience=raw["audience"],
            format=raw["format"],
            topic=raw["topic"],
            brief=raw.get("brief", ""),
            source_packet=raw.get("source_packet", []),
            config_snapshot=raw,
            moderator=moderator,
            participants=participants,
            editorial_goals=raw.get("editorial_goals", []),
            turns=raw.get("turns", 1),
        )

    def _validate_config(self, raw: dict) -> None:
        schema_path = self.repo_root / "schemas" / "roundtable-run.schema.json"
        schema = json.loads(schema_path.read_text())
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(raw), key=lambda item: list(item.path))
        if not errors:
            return

        messages = []
        for validation_error in errors:
            location = ".".join(str(part) for part in validation_error.path) or "<root>"
            messages.append(f"{location}: {validation_error.message}")
        raise ConfigError("Invalid roundtable config:\n- " + "\n- ".join(messages))

    def _validate_prompt_files(self, raw: dict) -> None:
        prompt_files = [raw["moderator"]["prompt_file"]]
        prompt_files.extend(participant["prompt_file"] for participant in raw["participants"])
        missing = [
            prompt_file
            for prompt_file in sorted(set(prompt_files))
            if not (self.repo_root / prompt_file).is_file()
        ]
        if missing:
            raise ConfigError(
                "Invalid roundtable config:\n- missing prompt file(s): "
                + ", ".join(missing)
            )

    def build_turn_plan(self, config: RoundtableConfig) -> list[TurnRecord]:
        moderator_prompt = self._read_text(config.moderator.prompt_file)
        records: list[TurnRecord] = []

        for turn_number in range(1, config.turns + 1):
            for participant in config.participants:
                participant_prompt = self._read_text(participant.prompt_file)
                prompt = self._compose_prompt(
                    moderator_prompt=moderator_prompt,
                    participant_prompt=participant_prompt,
                    config=config,
                    participant=participant,
                    turn_number=turn_number,
                )
                records.append(
                    TurnRecord(
                        speaker=participant.name,
                        prompt=prompt,
                        provider=participant.provider,
                        model=participant.model,
                    )
                )
        return records

    def write_draft_run(self, config: RoundtableConfig, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        plan = self.build_turn_plan(config)

        manifest = {
            "run": self._run_metadata(config, output_dir, "draft"),
            "slug": config.slug,
            "title": config.title,
            "date": config.date.isoformat(),
            "audience": config.audience,
            "format": config.format,
            "topic": config.topic,
            "brief": config.brief,
            "source_packet": config.source_packet,
            "editorial_goals": config.editorial_goals,
            "turns": config.turns,
            "moderator": asdict(config.moderator),
            "participants": [asdict(participant) for participant in config.participants],
            "config_snapshot": config.config_snapshot,
            "prompt_files": self._prompt_file_metadata(config),
            "planned_turn_records": [asdict(record) for record in plan],
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n"
        )
        (output_dir / "transcript.stub.md").write_text(self._render_stub(config, plan))

    def run_live(self, config: RoundtableConfig, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        self._load_env_file()
        transcript_entries: list[dict[str, str]] = []
        completed_records: list[TurnRecord] = []

        moderator_prompt = self._read_text(config.moderator.prompt_file)
        for turn_number in range(1, config.turns + 1):
            for participant in config.participants:
                participant_prompt = self._read_text(participant.prompt_file)
                prompt = self._compose_prompt(
                    moderator_prompt=moderator_prompt,
                    participant_prompt=participant_prompt,
                    config=config,
                    participant=participant,
                    turn_number=turn_number,
                    transcript_entries=transcript_entries,
                )
                record = TurnRecord(
                    speaker=participant.name,
                    prompt=prompt,
                    provider=participant.provider,
                    model=participant.model,
                )
                response_text, status = self._generate_response(participant, prompt)
                record.response = response_text
                record.status = status
                completed_records.append(record)
                transcript_entries.append(
                    {
                        "speaker": participant.name,
                        "status": status,
                        "content": response_text,
                    }
                )

        manifest = {
            "run": self._run_metadata(config, output_dir, "live"),
            "slug": config.slug,
            "title": config.title,
            "date": config.date.isoformat(),
            "audience": config.audience,
            "format": config.format,
            "topic": config.topic,
            "brief": config.brief,
            "source_packet": config.source_packet,
            "editorial_goals": config.editorial_goals,
            "turns": config.turns,
            "moderator": asdict(config.moderator),
            "participants": [asdict(participant) for participant in config.participants],
            "config_snapshot": config.config_snapshot,
            "prompt_files": self._prompt_file_metadata(config),
            "executed_turn_records": [asdict(record) for record in completed_records],
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n"
        )
        (output_dir / "transcript.md").write_text(
            self._render_completed_transcript(config, completed_records)
        )

    def _compose_prompt(
        self,
        *,
        moderator_prompt: str,
        participant_prompt: str,
        config: RoundtableConfig,
        participant: ParticipantConfig,
        turn_number: int,
        transcript_entries: list[dict[str, str]] | None = None,
    ) -> str:
        transcript_text = self._render_context(transcript_entries or [])
        return (
            f"{moderator_prompt.strip()}\n\n"
            f"{participant_prompt.strip()}\n\n"
            f"Roundtable title: {config.title}\n"
            f"Topic: {config.topic}\n"
            f"Audience: {config.audience}\n"
            f"Format: {config.format}\n"
            f"Turn number: {turn_number}\n"
            f"Participant name: {participant.name}\n"
            f"Participant stance: {participant.stance}\n"
            f"Brief: {config.brief}\n"
            f"Editorial goals: {', '.join(config.editorial_goals) or 'none provided'}\n"
            f"Conversation so far:\n{transcript_text}\n\n"
            "Write only this participant's next contribution. Keep it between 120 and 220 words unless the prompt clearly demands brevity."
        )

    def _render_stub(
        self, config: RoundtableConfig, plan: list[TurnRecord]
    ) -> str:
        lines = [
            f"# {config.title}",
            "",
            f"- Date: {config.date.isoformat()}",
            f"- Format: {config.format}",
            f"- Audience: {config.audience}",
            f"- Topic: {config.topic}",
            "",
            "## Planned Transcript",
            "",
        ]
        for record in plan:
            lines.append(f"### {record.speaker}")
            lines.append("")
            lines.append("_Response pending._")
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def _render_completed_transcript(
        self, config: RoundtableConfig, records: list[TurnRecord]
    ) -> str:
        lines = [
            f"# {config.title}",
            "",
            f"- Date: {config.date.isoformat()}",
            f"- Format: {config.format}",
            f"- Audience: {config.audience}",
            f"- Topic: {config.topic}",
            "",
        ]
        for record in records:
            lines.append(
                f"## {record.speaker} ({record.provider}:{record.model}, {record.status})"
            )
            lines.append("")
            lines.append(record.response.strip() or "_No response._")
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def _render_context(self, transcript_entries: list[dict[str, str]]) -> str:
        if not transcript_entries:
            return "No prior turns yet."
        rendered: list[str] = []
        for entry in transcript_entries:
            rendered.append(
                f"{entry['speaker']} [{entry['status']}]: {entry['content'].strip()}"
            )
        return "\n\n".join(rendered)

    def _load_env_file(self) -> None:
        if self._env_loaded:
            return
        env_path = self.repo_root / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip("'\""))
        self._env_loaded = True

    def _generate_response(
        self, participant: ParticipantConfig, prompt: str
    ) -> tuple[str, str]:
        response = provider_adapter_for(participant.provider).generate(participant, prompt)
        return (response.text, response.status)

    def _run_metadata(
        self, config: RoundtableConfig, output_dir: Path, mode: str
    ) -> dict[str, str]:
        return {
            "mode": mode,
            "slug": config.slug,
            "output_dir": str(output_dir),
            "generated_at": datetime.now(UTC).isoformat(),
            "package_version": package_version(),
        }

    def _prompt_file_metadata(self, config: RoundtableConfig) -> list[dict[str, str]]:
        prompt_files = [config.moderator.prompt_file]
        prompt_files.extend(participant.prompt_file for participant in config.participants)
        metadata = []
        for prompt_file in sorted(set(prompt_files)):
            content = self._read_text(prompt_file).encode("utf-8")
            metadata.append(
                {
                    "path": prompt_file,
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
        return metadata

    def _read_text(self, relative_path: str) -> str:
        return (self.repo_root / relative_path).read_text()


def package_version() -> str:
    try:
        return version("ai-roundtables-studio")
    except PackageNotFoundError:
        return "0.1.0-dev"
