from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .editorial import parse_front_matter


DEFAULT_DIALOGUE_MODEL = "eleven_v3"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_CHUNK_CHARS = 1800

INTENDED_VOICE_MAP = {
    "Moderator": {
        "voice": "Charlotte",
        "voice_id": "rhS7yjXTU4uIlRxXhNW7",
        "source": "shared",
        "description": "Listener orientation, transitions, clarification",
    },
    "OpenAI": {
        "voice": "Daniel",
        "voice_id": "onwK4e9ZLuTAKqWW03F9",
        "source": "saved",
        "description": "Measured synthesis and structured conclusions",
    },
    "Google": {
        "voice": "Josh",
        "voice_id": "ZoiZ8fuDWInAcwPXaVeq",
        "source": "shared",
        "description": "Balanced systems framing and reliable collaboration",
    },
    "Anthropic": {
        "voice": "Serena",
        "voice_id": "ZbKehTnuETNa9LsAnRO8",
        "source": "shared",
        "description": "Weighted uncertainty and epistemic honesty",
    },
}

FREE_CHECK_VOICE_MAP = {
    "Moderator": {
        "voice": "Alice",
        "voice_id": "Xb7hH8MSUJpSbSDYk0k2",
        "source": "premade",
        "description": "Clear listener orientation fallback for API checks",
    },
    "OpenAI": {
        "voice": "Daniel",
        "voice_id": "onwK4e9ZLuTAKqWW03F9",
        "source": "premade",
        "description": "Measured synthesis and structured conclusions",
    },
    "Google": {
        "voice": "Eric",
        "voice_id": "cjVigY5qzO86Huf0OWal",
        "source": "premade",
        "description": "Smooth, trustworthy systems-framing fallback",
    },
    "Anthropic": {
        "voice": "Matilda",
        "voice_id": "XrExE9yKIg1WjnnlVkGX",
        "source": "premade",
        "description": "Professional uncertainty fallback",
    },
}

VOICE_PROFILES = {
    "intended": INTENDED_VOICE_MAP,
    "free-check": FREE_CHECK_VOICE_MAP,
}

SPEAKER_PATTERN = re.compile(r"^\*\*(?P<speaker>[^:*]+):\*\*\s*(?P<text>.*)$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")


@dataclass(slots=True)
class AudioSegment:
    speaker: str
    voice: str
    voice_id: str
    text: str


@dataclass(slots=True)
class AudioScript:
    source: str
    title: str
    generated_at: str
    model_id: str = DEFAULT_DIALOGUE_MODEL
    voice_map: dict[str, dict[str, str]] = field(default_factory=dict)
    segments: list[AudioSegment] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "title": self.title,
            "generated_at": self.generated_at,
            "model_id": self.model_id,
            "voice_map": self.voice_map,
            "segments": [
                {
                    "speaker": segment.speaker,
                    "voice": segment.voice,
                    "voice_id": segment.voice_id,
                    "text": segment.text,
                }
                for segment in self.segments
            ],
        }


def create_audio_script(
    published_path: Path,
    *,
    output_path: Path,
    max_segments: int | None = None,
    max_segment_chars: int | None = None,
    voice_profile: str = "intended",
) -> AudioScript:
    script = build_audio_script(
        published_path,
        max_segments=max_segments,
        max_segment_chars=max_segment_chars,
        voice_profile=voice_profile,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(script.to_dict(), indent=2) + "\n")
    return script


def build_audio_script(
    published_path: Path,
    *,
    max_segments: int | None = None,
    max_segment_chars: int | None = None,
    voice_profile: str = "intended",
) -> AudioScript:
    voice_map = _voice_map_for_profile(voice_profile)
    metadata, body = parse_front_matter(published_path.read_text())
    title = metadata.get("title") or _first_heading(body) or published_path.stem
    segments = _extract_segments(
        body,
        voice_map=voice_map,
        max_segment_chars=max_segment_chars,
    )
    if max_segments is not None:
        segments = segments[:max_segments]
    return AudioScript(
        source=_repo_relative(published_path),
        title=title,
        generated_at=datetime.now(UTC).isoformat(),
        voice_map=voice_map,
        segments=segments,
    )


def render_audio_script(
    script_path: Path,
    *,
    output_path: Path,
    dry_run: bool = False,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    chunk_chars: int = DEFAULT_CHUNK_CHARS,
) -> dict[str, Any]:
    script = json.loads(script_path.read_text())
    segments = script.get("segments", [])
    if not segments:
        raise ValueError(f"Audio script contains no segments: {script_path}")

    manifest = {
        "source_script": _repo_relative(script_path),
        "output": _repo_relative(output_path),
        "model_id": script.get("model_id", DEFAULT_DIALOGUE_MODEL),
        "output_format": output_format,
        "segments": len(segments),
        "characters": sum(len(segment.get("text", "")) for segment in segments),
        "dry_run": dry_run,
    }
    if dry_run:
        return manifest

    api_key = _load_elevenlabs_api_key()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks = _chunk_segments(segments, chunk_chars=chunk_chars)
    audio_parts = [
        _create_dialogue_audio(
            api_key=api_key,
            inputs=[
                {"text": segment["text"], "voice_id": segment["voice_id"]}
                for segment in chunk
            ],
            model_id=script.get("model_id", DEFAULT_DIALOGUE_MODEL),
            output_format=output_format,
        )
        for chunk in chunks
    ]
    output_path.write_bytes(b"".join(audio_parts))
    manifest["chunks"] = len(chunks)
    manifest["bytes"] = output_path.stat().st_size
    return manifest


def _extract_segments(
    body: str,
    *,
    voice_map: dict[str, dict[str, str]],
    max_segment_chars: int | None,
) -> list[AudioSegment]:
    segments: list[AudioSegment] = []
    current_speaker: str | None = None
    current_lines: list[str] = []
    in_roundtable = False

    for line in body.splitlines():
        if line.startswith("## Editorial Note"):
            break
        if line.startswith("## Roundtable"):
            in_roundtable = True
            continue
        if not in_roundtable:
            continue
        match = SPEAKER_PATTERN.match(line)
        if match:
            _append_segment(
                segments,
                current_speaker,
                current_lines,
                voice_map,
                max_segment_chars,
            )
            current_speaker = match.group("speaker").strip()
            current_lines = [match.group("text").strip()]
            continue
        if current_speaker is not None:
            current_lines.append(line)

    _append_segment(
        segments,
        current_speaker,
        current_lines,
        voice_map,
        max_segment_chars,
    )
    return segments


def _append_segment(
    segments: list[AudioSegment],
    speaker: str | None,
    lines: list[str],
    voice_map: dict[str, dict[str, str]],
    max_segment_chars: int | None,
) -> None:
    if speaker is None:
        return
    voice_config = voice_map.get(speaker)
    if voice_config is None:
        raise ValueError(f"No audio voice configured for speaker: {speaker}")
    text = _clean_audio_text("\n".join(lines))
    if max_segment_chars is not None:
        text = _truncate_at_sentence(text, max_segment_chars)
    if not text:
        return
    segments.append(
        AudioSegment(
            speaker=speaker,
            voice=voice_config["voice"],
            voice_id=voice_config["voice_id"],
            text=text,
        )
    )


def _clean_audio_text(text: str) -> str:
    text = MARKDOWN_LINK_PATTERN.sub(r"\1", text)
    text = text.replace("`", "")
    text = re.sub(r"^\s*-\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n", text.strip())
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _truncate_at_sentence(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rstrip()
    sentence_end = max(truncated.rfind("."), truncated.rfind("?"), truncated.rfind("!"))
    if sentence_end >= max_chars // 2:
        return truncated[: sentence_end + 1]
    return truncated.rsplit(" ", 1)[0].rstrip() + "."


def _voice_map_for_profile(profile: str) -> dict[str, dict[str, str]]:
    try:
        return VOICE_PROFILES[profile]
    except KeyError as exc:
        choices = ", ".join(sorted(VOICE_PROFILES))
        raise ValueError(f"Unknown voice profile: {profile}. Choices: {choices}") from exc


def _chunk_segments(
    segments: list[dict[str, str]],
    *,
    chunk_chars: int,
) -> list[list[dict[str, str]]]:
    chunks: list[list[dict[str, str]]] = []
    current: list[dict[str, str]] = []
    current_chars = 0
    for segment in segments:
        segment_chars = len(segment.get("text", ""))
        if current and current_chars + segment_chars > chunk_chars:
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(segment)
        current_chars += segment_chars
    if current:
        chunks.append(current)
    return chunks


def _create_dialogue_audio(
    *,
    api_key: str,
    inputs: list[dict[str, str]],
    model_id: str,
    output_format: str,
) -> bytes:
    query = urlencode({"output_format": output_format})
    request = Request(
        f"https://api.elevenlabs.io/v1/text-to-dialogue?{query}",
        data=json.dumps({"inputs": inputs, "model_id": model_id}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=180) as response:
            return response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ValueError(
            f"ElevenLabs dialogue request failed with HTTP {exc.code}: {detail}"
        ) from exc


def _load_elevenlabs_api_key() -> str:
    _load_env_file(Path.cwd() / ".env")
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY is not set")
    return api_key


def _load_env_file(env_path: Path) -> None:
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def _first_heading(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _repo_relative(path: Path) -> str:
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()
