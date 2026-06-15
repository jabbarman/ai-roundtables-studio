from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, date, datetime
import hashlib
import os
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from .models import ModeratorConfig, ParticipantConfig, RoundtableConfig, TurnRecord
from .providers import provider_adapter_for
from ._version import __version__


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
        self._validate_round_goals(raw)
        self._validate_prompt_files(raw)
        moderator_raw = raw["moderator"]
        participants_raw = raw["participants"]

        moderator = ModeratorConfig(
            name=moderator_raw["name"],
            prompt_file=moderator_raw["prompt_file"],
            provider=moderator_raw.get("provider", "openai"),
            model=moderator_raw.get("model", "gpt-5.4"),
            temperature=moderator_raw.get("temperature"),
            output_tokens=moderator_raw.get("output_tokens"),
        )
        participants = [
            ParticipantConfig(
                name=item["name"],
                provider=item["provider"],
                model=item["model"],
                prompt_file=item["prompt_file"],
                stance=item["stance"],
                temperature=item.get("temperature"),
                output_tokens=item.get("output_tokens"),
                thinking_tokens=item.get("thinking_tokens"),
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
            round_goals=raw.get("round_goals", []),
            turns=raw.get("turns", 1),
            moderator_turns=raw.get("moderator_turns", "none"),
            audio_intent=raw.get("audio_intent", "none"),
            participant_order=raw.get("participant_order", "fixed"),
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

    def _validate_round_goals(self, raw: dict) -> None:
        round_goals = raw.get("round_goals", [])
        if round_goals and len(round_goals) != raw.get("turns", 1):
            raise ConfigError(
                "Invalid roundtable config:\n- round_goals must contain exactly "
                "one entry per turn"
            )

    def build_turn_plan(self, config: RoundtableConfig) -> list[TurnRecord]:
        moderator_prompt = self._read_text(config.moderator.prompt_file)
        records: list[TurnRecord] = []

        for turn_number in range(1, config.turns + 1):
            if config.moderator_turns == "between_rounds":
                prompt = self._compose_moderator_prompt(
                    moderator_prompt=moderator_prompt,
                    config=config,
                    turn_number=turn_number,
                )
                records.append(
                    TurnRecord(
                        speaker=config.moderator.name,
                        prompt=prompt,
                        provider=config.moderator.provider,
                        model=config.moderator.model,
                    )
                )
            for participant in self._participants_for_turn(config, turn_number):
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
        if self._includes_moderator_closing(config):
            records.append(
                TurnRecord(
                    speaker=config.moderator.name,
                    prompt=self._compose_moderator_closing_prompt(
                        moderator_prompt=moderator_prompt,
                        config=config,
                    ),
                    provider=config.moderator.provider,
                    model=config.moderator.model,
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
            "round_goals": config.round_goals,
            "turns": config.turns,
            "moderator_turns": config.moderator_turns,
            "moderator_closing_summary": self._includes_moderator_closing(config),
            "audio_intent": config.audio_intent,
            "participant_order": config.participant_order,
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
            if config.moderator_turns == "between_rounds":
                prompt = self._compose_moderator_prompt(
                    moderator_prompt=moderator_prompt,
                    config=config,
                    turn_number=turn_number,
                    transcript_entries=transcript_entries,
                )
                moderator_participant = self._moderator_as_participant(config)
                record = TurnRecord(
                    speaker=config.moderator.name,
                    prompt=prompt,
                    provider=config.moderator.provider,
                    model=config.moderator.model,
                )
                response_text, status = self._generate_response(
                    moderator_participant, prompt
                )
                record.response = response_text
                record.status = status
                completed_records.append(record)
                transcript_entries.append(
                    {
                        "speaker": config.moderator.name,
                        "status": status,
                        "content": response_text,
                    }
                )
            for participant in self._participants_for_turn(config, turn_number):
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

        if self._includes_moderator_closing(config):
            prompt = self._compose_moderator_closing_prompt(
                moderator_prompt=moderator_prompt,
                config=config,
                transcript_entries=transcript_entries,
            )
            moderator_participant = self._moderator_as_participant(config)
            record = TurnRecord(
                speaker=config.moderator.name,
                prompt=prompt,
                provider=config.moderator.provider,
                model=config.moderator.model,
            )
            response_text, status = self._generate_response(
                moderator_participant, prompt
            )
            record.response = response_text
            record.status = status
            completed_records.append(record)
            transcript_entries.append(
                {
                    "speaker": config.moderator.name,
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
            "round_goals": config.round_goals,
            "turns": config.turns,
            "moderator_turns": config.moderator_turns,
            "moderator_closing_summary": self._includes_moderator_closing(config),
            "audio_intent": config.audio_intent,
            "participant_order": config.participant_order,
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
            f"Source packet:\n{self._render_source_packet(config)}\n"
            f"Editorial goals: {', '.join(config.editorial_goals) or 'none provided'}\n"
            f"Goal for this round: {self._round_goal(config, turn_number)}\n"
            f"Audio adaptation intent:\n{self._render_audio_context(config)}\n"
            f"Conversation so far:\n{transcript_text}\n\n"
            "Write only this participant's next contribution. Keep it between 120 and 220 words unless the prompt clearly demands brevity."
        )

    def _compose_moderator_prompt(
        self,
        *,
        moderator_prompt: str,
        config: RoundtableConfig,
        turn_number: int,
        transcript_entries: list[dict[str, str]] | None = None,
    ) -> str:
        transcript_text = self._render_context(transcript_entries or [])
        role_instruction = {
            1: (
                "Open the roundtable with a sharp setup and one specific question "
                "that creates disagreement."
            ),
            config.turns: (
                "Give a final challenge or synthesis prompt that forces the "
                "participants to name the practical consequence of their disagreement."
            ),
        }.get(
            turn_number,
            "Ask a follow-up that directly pressures the prior disagreement.",
        )
        return (
            f"{moderator_prompt.strip()}\n\n"
            f"Roundtable title: {config.title}\n"
            f"Topic: {config.topic}\n"
            f"Audience: {config.audience}\n"
            f"Format: {config.format}\n"
            f"Moderator turn number: {turn_number} of {config.turns}\n"
            f"Brief: {config.brief}\n"
            f"Source packet:\n{self._render_source_packet(config)}\n"
            f"Editorial goals: {', '.join(config.editorial_goals) or 'none provided'}\n"
            f"Goal for this round: {self._round_goal(config, turn_number)}\n"
            f"Audio adaptation intent:\n{self._render_audio_context(config)}\n"
            f"Conversation so far:\n{transcript_text}\n\n"
            f"{role_instruction} Write only the moderator's next contribution. "
            "Keep it between 60 and 120 words."
        )

    def _compose_moderator_closing_prompt(
        self,
        *,
        moderator_prompt: str,
        config: RoundtableConfig,
        transcript_entries: list[dict[str, str]] | None = None,
    ) -> str:
        transcript_text = self._render_context(transcript_entries or [])
        return (
            f"{moderator_prompt.strip()}\n\n"
            f"Roundtable title: {config.title}\n"
            f"Topic: {config.topic}\n"
            f"Audience: {config.audience}\n"
            f"Format: {config.format}\n"
            f"Brief: {config.brief}\n"
            f"Source packet:\n{self._render_source_packet(config)}\n"
            f"Editorial goals: {', '.join(config.editorial_goals) or 'none provided'}\n"
            f"Audio adaptation intent:\n{self._render_audio_context(config)}\n"
            f"Completed conversation:\n{transcript_text}\n\n"
            "Close the roundtable for a reader or listener. State briefly what the "
            "participants agreed on, identify the central unresolved disagreement, "
            "and name the strongest practical conclusion or decision rule that "
            "survived the exchange. If no conclusion was reached, say so plainly. "
            "Do not introduce new evidence, ask another question, thank the "
            "participants, or manufacture consensus. Write only the moderator's "
            "closing synthesis. Keep it between 80 and 140 words."
        )

    def _render_source_packet(self, config: RoundtableConfig) -> str:
        if not config.source_packet:
            return "No source packet provided."
        rendered = []
        for index, source in enumerate(config.source_packet, start=1):
            title = source.get("title", "Untitled source")
            kind = source.get("kind", "source")
            url = source.get("url", "")
            notes = source.get("notes", "")
            rendered.append(
                f"{index}. {title} ({kind})\n"
                f"   URL: {url or 'not provided'}\n"
                f"   Notes: {notes or 'none'}"
            )
        return "\n".join(rendered)

    def _participants_for_turn(
        self, config: RoundtableConfig, turn_number: int
    ) -> list[ParticipantConfig]:
        participants = list(config.participants)
        if config.participant_order != "rotate_by_round" or not participants:
            return participants
        offset = (turn_number - 1) % len(participants)
        return participants[offset:] + participants[:offset]

    def _round_goal(self, config: RoundtableConfig, turn_number: int) -> str:
        if not config.round_goals:
            return "No round-specific goal provided."
        return config.round_goals[turn_number - 1]

    def _includes_moderator_closing(self, config: RoundtableConfig) -> bool:
        return (
            config.moderator_turns == "between_rounds"
            and config.audio_intent == "podcast_adaptable"
        )

    def _render_audio_context(self, config: RoundtableConfig) -> str:
        if config.audio_intent != "podcast_adaptable":
            return "No audio adaptation intent declared."
        return (
            "This transcript may later become an audio roundtable. Keep the prose "
            "clear when heard once: use compact transitions, explain dense terms "
            "plainly, and let the moderator ask brief listener-facing clarification "
            "questions when needed. Do not add banter, stage directions, or podcast "
            "performance."
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

    def _moderator_as_participant(self, config: RoundtableConfig) -> ParticipantConfig:
        return ParticipantConfig(
            name=config.moderator.name,
            provider=config.moderator.provider,
            model=config.moderator.model,
            prompt_file=config.moderator.prompt_file,
            stance="Moderator",
            temperature=config.moderator.temperature,
            output_tokens=config.moderator.output_tokens,
        )

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
    return __version__
