from __future__ import annotations

import argparse
from pathlib import Path

from .orchestrator import ConfigError, DraftOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Roundtables Studio CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft_parser = subparsers.add_parser(
        "draft", help="Create a manifest and transcript stub from a config file."
    )
    draft_parser.add_argument("config", help="Path to a roundtable JSON config.")
    draft_parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where manifest.json and transcript.stub.md will be written.",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Execute a roundtable with configured providers and write a transcript.",
    )
    run_parser.add_argument("config", help="Path to a roundtable JSON config.")
    run_parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where manifest.json and transcript.md will be written.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = Path.cwd()
    orchestrator = DraftOrchestrator(repo_root=repo_root)

    try:
        if args.command == "draft":
            config = orchestrator.load_config(Path(args.config))
            orchestrator.write_draft_run(config, Path(args.output_dir))
            print(f"Draft run written to {args.output_dir}")
            return 0

        if args.command == "run":
            config = orchestrator.load_config(Path(args.config))
            orchestrator.run_live(config, Path(args.output_dir))
            print(f"Live run written to {args.output_dir}")
            return 0
    except ConfigError as exc:
        parser.exit(1, f"{exc}\n")

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
