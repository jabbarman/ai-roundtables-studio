# Repository Guidelines

## Project Structure & Module Organization

This repository supports the full roundtable publishing pipeline: topic notes, prompts, model runs, edited transcripts, and published pieces. Python source lives in `src/ai_roundtables/`; `cli.py` defines the command-line entry point, `orchestrator.py` prepares and executes runs, `providers.py` contains provider adapters, and `models.py` contains dataclass configuration objects.

Content and workflow assets are organized by stage:

- `prompts/`: moderator and participant prompt templates.
- `notes/`: topic ideas and example JSON configs.
- `schemas/`: JSON schema for run metadata.
- `runs/raw/` and `runs/edited/`: generated run artifacts; most contents are ignored except README and `.gitkeep` files.
- `transcripts/`: cleaned transcripts before final editorial shaping.
- `published/`: final reader-facing roundtables.
- `docs/`: editorial and methodology guidance.
- `evals/`: evaluation notes and future checks.

## Build, Test, and Development Commands

Use Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Run a dry draft that writes a manifest and transcript stub:

```bash
ai-roundtables draft notes/example-config.json --output-dir runs/raw/example-run
```

Run the OpenAI-backed path after creating `.env` from `.env.example`:

```bash
ai-roundtables run notes/example-config.openai-only.json --output-dir runs/raw/openai-only-run
```

Run tests:

```bash
pytest
```

Evaluate generated run artifacts:

```bash
ai-roundtables eval runs/raw/example-run
```

## Coding Style & Naming Conventions

Follow the existing Python style: 4-space indentation, type annotations, `from __future__ import annotations`, dataclasses for structured records, and `pathlib.Path` for filesystem work. Keep modules small and explicit. Use snake_case for functions, variables, files, and config keys; use PascalCase for classes. Prefer JSON parsing and structured data over string manipulation for manifests and configs.

## Testing Guidelines

Pytest tests live under `tests/` and should be named `test_*.py`. For code changes, run `pytest` plus the dry draft command above and inspect `manifest.json` plus the generated transcript stub. Prefer focused unit tests for config loading, prompt composition, provider skipping, and transcript rendering.

## Commit & Pull Request Guidelines

Use concise imperative commit messages such as `Add OpenAI run validation` or `Document transcript workflow`. Pull requests should describe the workflow impact, list validation commands, link any related issue or topic note, and include screenshots or transcript excerpts only when they clarify user-facing editorial output.

## Security & Configuration Tips

Do not commit `.env`, API keys, or generated raw run contents. Keep example configs in `notes/` free of secrets. Generated artifacts belong under `runs/`; publish only reviewed material in `published/`.
