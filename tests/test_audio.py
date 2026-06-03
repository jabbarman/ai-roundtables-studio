from __future__ import annotations

import json
from pathlib import Path

from ai_roundtables.audio import build_audio_script, render_audio_script


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
    assert len(script.segments) == 2
    assert script.segments[0].speaker == "Moderator"
    assert script.segments[0].voice == "Charlotte"
    assert script.segments[1].speaker == "OpenAI"
    assert "https://example.com" not in script.segments[1].text
    assert "a source" in script.segments[1].text


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

    assert script.segments[0].text == "First sentence."


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
    assert manifest["dry_run"] is True
