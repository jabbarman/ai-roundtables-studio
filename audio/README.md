# Audio Layer

Audio is an enrichment layer for reviewed roundtable texts, not a replacement
for the canonical transcript. Use it to make speaker roles sonically distinct
while preserving the argument, uncertainty, and editorial structure of the
written piece.

## Voice Map

The intended production profile is:

| Role | Provider label | ElevenLabs voice | Editorial function |
| --- | --- | --- | --- |
| Moderator / Narrator | Moderator | Charlotte | Listener orientation, transitions, clarification |
| OpenAI / ChatGPT | OpenAI | Daniel | Measured synthesis and structured conclusions |
| Google / Gemini | Google | Josh | Balanced systems framing and reliable collaboration |
| Anthropic / Claude | Anthropic | Serena | Weighted uncertainty and epistemic honesty |

On plans where shared or professional library voices are unavailable through the
API, use `--voice-profile free-check` to render a pipeline check with premade
fallback voices.

## Working Directories

- `audio/scripts/`: audio-ready scripts derived from reviewed transcripts.
- `audio/manifests/`: voice assignments, source transcript paths, and export metadata.
- `audio/exports/`: generated audio files. Contents are ignored except `.gitkeep`.
- `audio/pronunciations.json`: repository-level text replacements for common pronunciation fixes.

## Commands

Create a short check script from a published roundtable:

```bash
ai-roundtables audio-script published/explain-reasoning-or-conclusions.md \
  --output audio/scripts/explain-reasoning-sample.json \
  --max-segments 5 \
  --max-segment-chars 360 \
  --voice-profile intended \
  --pronunciations audio/pronunciations.json \
  --intro "This is {title}, an A I roundtable." \
  --outro "That was {title}."
```

Render the script through ElevenLabs:

```bash
ai-roundtables audio-render audio/scripts/explain-reasoning-sample.json \
  --output audio/exports/explain-reasoning-sample.mp3 \
  --manifest audio/manifests/explain-reasoning-sample.render.json
```

For a no-upgrade API check, create the script with `--voice-profile free-check`.

Build the script and MP3 in one step:

```bash
ai-roundtables audio-build published/explain-reasoning-or-conclusions.md \
  --script-output audio/scripts/explain-reasoning-sample.json \
  --output audio/exports/explain-reasoning-sample.mp3 \
  --manifest audio/manifests/explain-reasoning-sample.render.json \
  --voice-profile intended \
  --pronunciations audio/pronunciations.json
```

Use `audio-render --mode segments` when you want retryable per-speaker MP3
parts. Existing part files are reused unless `--force` is set.

Pause metadata is stored on each segment. `--pause-style ssml` can append SSML
break tags during per-segment rendering with compatible ElevenLabs models; Eleven
v3 does not support SSML breaks, so the default is `--pause-style none`.

## Adaptation Principles

- Keep the published markdown as the source of truth.
- Disclose that voices are assigned presentation choices, not emergent model identities.
- Let Charlotte add brief listener-facing orientation where the transcript needs it.
- Avoid rewriting arguments for drama, banter, or artificial podcast rhythm.
- Keep technical clarification light: explain the hinge of a claim, then return to the exchange.

Set `ELEVENLABS_API_KEY` in the shell or `.env` before generating audio.
