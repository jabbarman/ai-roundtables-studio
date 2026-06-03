# Audio Layer

Audio is an enrichment layer for reviewed roundtable texts, not a replacement
for the canonical transcript. Use it to make speaker roles sonically distinct
while preserving the argument, uncertainty, and editorial structure of the
written piece.

## Voice Map

| Role | Provider label | ElevenLabs voice | Editorial function |
| --- | --- | --- | --- |
| Moderator / Narrator | Moderator | Charlotte | Listener orientation, transitions, clarification |
| OpenAI / ChatGPT | OpenAI | Daniel | Measured synthesis and structured conclusions |
| Google / Gemini | Google | Josh | Balanced systems framing and reliable collaboration |
| Anthropic / Claude | Anthropic | Serena | Weighted uncertainty and epistemic honesty |

## Working Directories

- `audio/scripts/`: audio-ready scripts derived from reviewed transcripts.
- `audio/manifests/`: voice assignments, source transcript paths, and export metadata.
- `audio/exports/`: generated audio files. Contents are ignored except `.gitkeep`.

## Adaptation Principles

- Keep the published markdown as the source of truth.
- Disclose that voices are assigned presentation choices, not emergent model identities.
- Let Charlotte add brief listener-facing orientation where the transcript needs it.
- Avoid rewriting arguments for drama, banter, or artificial podcast rhythm.
- Keep technical clarification light: explain the hinge of a claim, then return to the exchange.

Set `ELEVENLABS_API_KEY` in the shell or `.env` before generating audio.
