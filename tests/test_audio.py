from __future__ import annotations

import json
from pathlib import Path

from ai_roundtables import audio
from ai_roundtables.audio import (
    build_and_render_audio,
    build_audio_script,
    render_audio_script,
)


def test_build_audio_script_extracts_roundtable_segments(tmp_path: Path) -> None:
    published = tmp_path / "published.md"
    published.write_text(
        """---
title: Audio Test
---

# Audio Test

Intro text.

## Roundtable

**Moderator:** First question?

**OpenAI:** First answer with [a source](https://example.com).

More detail.

**Anthropic:** Second answer.

## Editorial Note

Done.
"""
    )

    script = build_audio_script(published, max_segments=2)

    assert script.title == "Audio Test"
    assert len(script.segments) == 3
    assert script.segments[0].speaker == "Moderator"
    assert script.segments[0].kind == "cast_intro"
    assert "Daniel will read OpenAI" in script.segments[0].text
    assert script.segments[0].voice == "Charlotte"
    assert script.segments[2].speaker == "OpenAI"
    assert "https://example.com" not in script.segments[2].text
    assert "a source" in script.segments[2].text
    assert script.to_dict()["estimated_characters"] > 0


def test_build_audio_script_extracts_heading_speaker_segments(tmp_path: Path) -> None:
    published = tmp_path / "published.md"
    published.write_text(
        """# Audio Test

## Roundtable

## Moderator

First question?

## OpenAI

First answer.
"""
    )

    script = build_audio_script(published, cast_intro=False)

    assert [segment.speaker for segment in script.segments] == ["Moderator", "OpenAI"]
    assert script.segments[0].text == "First question?"
    assert script.segments[1].text == "First answer."


def test_build_audio_script_can_use_free_check_profile(tmp_path: Path) -> None:
    published = tmp_path / "published.md"
    published.write_text(
        """# Audio Test

## Roundtable

**Moderator:** First question?
"""
    )

    script = build_audio_script(published, voice_profile="free-check")

    assert script.segments[0].speaker == "Moderator"
    assert script.segments[0].voice == "Alice"
    assert script.voice_map["Moderator"]["source"] == "premade"


def test_build_audio_script_can_trim_segments_at_sentence_boundary(
    tmp_path: Path,
) -> None:
    published = tmp_path / "published.md"
    published.write_text(
        """# Audio Test

## Roundtable

**OpenAI:** First sentence. Second sentence that is much longer than the limit.
"""
    )

    script = build_audio_script(published, max_segment_chars=20)

    assert script.segments[1].text == "First sentence."


def test_build_audio_script_can_add_bookends_and_pronunciations(
    tmp_path: Path,
) -> None:
    published = tmp_path / "published.md"
    pronunciations = tmp_path / "pronunciations.json"
    pronunciations.write_text(json.dumps({"replacements": {"AI": "A I"}}))
    published.write_text(
        """---
title: Pronunciation Test
---

## Roundtable

**Moderator:** AI systems?
"""
    )

    script = build_audio_script(
        published,
        intro_text="Welcome to {title}.",
        outro_text="End of {title}.",
        pronunciation_path=pronunciations,
    )

    assert [segment.kind for segment in script.segments] == ["intro", "turn", "outro"]
    assert script.segments[1].text == "A I systems?"
    assert script.pronunciation_map == {"AI": "A I"}


def test_audio_render_dry_run_returns_manifest(tmp_path: Path) -> None:
    script = tmp_path / "script.json"
    script.write_text(
        json.dumps(
            {
                "model_id": "eleven_v3",
                "segments": [
                    {
                        "speaker": "Moderator",
                        "voice": "Charlotte",
                        "voice_id": "voice-1",
                        "text": "Hello.",
                    }
                ],
            }
        )
    )

    manifest = render_audio_script(
        script,
        output_path=tmp_path / "sample.mp3",
        dry_run=True,
    )

    assert manifest["segments"] == 1
    assert manifest["characters"] == 6
    assert manifest["estimated_requests"] == 1
    assert manifest["dry_run"] is True


def test_audio_render_writes_manifest_on_dry_run(tmp_path: Path) -> None:
    script = tmp_path / "script.json"
    manifest_path = tmp_path / "manifest.json"
    script.write_text(
        json.dumps(
            {
                "model_id": "eleven_v3",
                "segments": [
                    {
                        "speaker": "Moderator",
                        "voice": "Charlotte",
                        "voice_id": "voice-1",
                        "text": "Hello.",
                    }
                ],
            }
        )
    )

    render_audio_script(
        script,
        output_path=tmp_path / "sample.mp3",
        dry_run=True,
        manifest_path=manifest_path,
        cache_dir=tmp_path / "cache",
    )

    assert json.loads(manifest_path.read_text())["dry_run"] is True


def test_audio_render_segments_reuses_existing_parts(
    tmp_path: Path, monkeypatch
) -> None:
    script = tmp_path / "script.json"
    script.write_text(
        json.dumps(
            {
                "model_id": "eleven_v3",
                "segments": [
                    {
                        "speaker": "Moderator",
                        "voice": "Charlotte",
                        "voice_id": "voice-1",
                        "text": "Hello.",
                    },
                    {
                        "speaker": "OpenAI",
                        "voice": "Daniel",
                        "voice_id": "voice-2",
                        "text": "There.",
                    },
                ],
            }
        )
    )
    calls: list[str] = []

    def fake_tts_audio(**kwargs: str) -> bytes:
        calls.append(kwargs["voice_id"])
        return kwargs["voice_id"].encode()

    monkeypatch.setattr(audio, "_load_elevenlabs_api_key", lambda: "test-key")
    monkeypatch.setattr(audio, "_create_tts_audio", fake_tts_audio)

    output = tmp_path / "sample.mp3"
    manifest = render_audio_script(
        script,
        output_path=output,
        mode="segments",
        cache_dir=tmp_path / "cache",
    )
    assert output.read_bytes() == b"voice-1voice-2"
    assert manifest["mode"] == "segments"
    assert len(manifest["parts"]) == 2
    assert calls == ["voice-1", "voice-2"]

    calls.clear()
    render_audio_script(
        script,
        output_path=output,
        mode="segments",
        cache_dir=tmp_path / "cache",
    )
    assert calls == []


def test_audio_render_uses_content_addressed_cache(
    tmp_path: Path, monkeypatch
) -> None:
    script = tmp_path / "script.json"
    script.write_text(
        json.dumps(
            {
                "model_id": "eleven_v3",
                "segments": [
                    {
                        "speaker": "Moderator",
                        "voice": "Charlotte",
                        "voice_id": "voice-1",
                        "text": "Hello.",
                    }
                ],
            }
        )
    )
    calls = 0

    def fake_dialogue_audio(**kwargs: str) -> bytes:
        nonlocal calls
        calls += 1
        return b"audio"

    monkeypatch.setattr(audio, "_load_elevenlabs_api_key", lambda: "test-key")
    monkeypatch.setattr(audio, "_create_dialogue_audio", fake_dialogue_audio)

    first = render_audio_script(
        script,
        output_path=tmp_path / "first.mp3",
        cache_dir=tmp_path / "cache",
    )
    second = render_audio_script(
        script,
        output_path=tmp_path / "second.mp3",
        cache_dir=tmp_path / "cache",
    )

    assert calls == 1
    assert first["cache"]["misses"] == 1
    assert second["cache"]["hits"] == 1
    assert (tmp_path / "second.mp3").read_bytes() == b"audio"


def test_build_and_render_audio_dry_run_writes_script(tmp_path: Path) -> None:
    published = tmp_path / "published.md"
    published.write_text(
        """# Build Test

## Roundtable

**Moderator:** First question?
"""
    )

    manifest = build_and_render_audio(
        published,
        script_path=tmp_path / "script.json",
        output_path=tmp_path / "sample.mp3",
        dry_run=True,
        max_segments=1,
    )

    assert (tmp_path / "script.json").is_file()
    assert manifest["dry_run"] is True
    assert manifest["segments"] == 1
