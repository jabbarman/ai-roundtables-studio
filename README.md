# AI Roundtables Studio

`AI Roundtables Studio` is a production and publishing repo for moderated, multi-model conversations that are intellectually serious, readable, and engaging for an intelligent lay audience.

This repo is designed to support the whole pipeline:

`topic -> prompt pack -> model turns -> raw transcript -> edited transcript -> published roundtable`

It is the companion to the earlier `ai-roundtables` repo, which stands as the curated first edition. This repo is for the next phase: a more rigorous, more reproducible, and more extensible roundtable workflow.

## Editorial Direction

The goal is not academic prose for its own sake.

The goal is:

- erudite without being stuffy
- accessible without becoming simplistic
- rigorous underneath without reading like a methods section
- alive to disagreement, tension, and surprise

Each published conversation should be readable by an intelligent non-specialist while still being defensible to technically informed readers.

## What Lives Here

- `published/`: final edited roundtables intended for readers
- `transcripts/`: cleaned transcripts derived from runs, before editorial shaping
- `runs/`: raw and edited machine outputs, manifests, and run artifacts
- `prompts/`: moderator, participant, and format prompts
- `schemas/`: metadata and run schemas
- `docs/`: editorial standards and methodology
- `src/ai_roundtables/`: orchestration code
- `evals/`: checks for disagreement quality, evidence use, and transcript health
- `notes/`: topic ideas, working notes, and source packets

## Working Principles

- A published roundtable should be enjoyable to read.
- A raw run should be reproducible enough to audit.
- Human editing is allowed, but it should be declared.
- The three speakers should sound distinct.
- Claims should be grounded often enough to avoid empty profundity.
- The moderator should actively create tension, not just invite consensus.

## Suggested Workflow

1. Define a topic and intended audience.
2. Choose a format such as roundtable, debate, Delphi, or consensus-plus-dissent.
3. Prepare a source packet when the discussion benefits from evidence.
4. Run the orchestrator to generate a raw transcript.
5. Clean the transcript into `transcripts/`.
6. Edit for readability and shape into `published/`.
7. Attach metadata covering model IDs, prompts, source inputs, and editorial intervention.

## Quick Start

Install the package in editable mode, create a config file, and then run:

```bash
pip install -e .
ai-roundtables draft path/to/config.json --output-dir runs/raw/example-run
```

If you are working without an editable install, the module form also works:

```bash
PYTHONPATH=src python3 -m ai_roundtables.cli draft path/to/config.json --output-dir runs/raw/example-run
```

The dry-run orchestrator prepares prompts, manifests, and markdown transcript stubs without calling model providers.

For a real provider-backed run:

```bash
cp .env.example .env
# add OPENAI_API_KEY, ANTHROPIC_API_KEY, and/or GEMINI_API_KEY to .env
ai-roundtables run notes/example-config.openai-only.json --output-dir runs/raw/openai-only-run
```

Evaluate a run directory after draft or live generation:

```bash
ai-roundtables eval runs/raw/example-run
```

Promote a raw run into a cleaned transcript scaffold:

```bash
ai-roundtables promote runs/raw/example-run --output transcripts/example.md
```

Create a published markdown scaffold from a cleaned transcript:

```bash
ai-roundtables publish transcripts/example.md --output published/example.md
```

Check published metadata and regenerate the published index:

```bash
ai-roundtables check published/example.md
ai-roundtables index
```

Configs can enable visible moderator turns with:

```json
"moderator_turns": "between_rounds"
```

When enabled, the moderator contributes an opening or follow-up before each participant round. Keep `"moderator_turns": "none"` or omit it for participant-only transcripts.

## Provider Setup

You can use this repo in stages.

- `OPENAI_API_KEY` enables OpenAI Responses API participants.
- `ANTHROPIC_API_KEY` enables Anthropic Messages API participants.
- `GEMINI_API_KEY` enables Gemini `generateContent` participants.
- If a provider is present in a config but its key is missing, the orchestrator will skip that seat and note why in the transcript and manifest.

## First Files To Read

- [docs/EDITORIAL.md](docs/EDITORIAL.md)
- [docs/METHODOLOGY.md](docs/METHODOLOGY.md)
- [schemas/roundtable-run.schema.json](schemas/roundtable-run.schema.json)
- [prompts/moderator.md](prompts/moderator.md)
