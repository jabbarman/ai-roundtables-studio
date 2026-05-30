from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import evaluate_run, format_evaluation
from .orchestrator import ConfigError, DraftOrchestrator, package_version


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-roundtables",
        description="AI Roundtables Studio CLI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {package_version()}",
    )
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

    eval_parser = subparsers.add_parser(
        "eval",
        help="Check a run directory for manifest, transcript, and provider-status issues.",
    )
    eval_parser.add_argument("run_dir", help="Path to a raw or edited run directory.")
    eval_parser.add_argument(
        "--json",
        action="store_true",
        help="Write machine-readable evaluation output.",
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

        if args.command == "eval":
            evaluation = evaluate_run(Path(args.run_dir))
            if args.json:
                print(json.dumps(evaluation.to_dict(), indent=2))
            else:
                print(format_evaluation(evaluation))
            return 0 if evaluation.passed else 1
    except ConfigError as exc:
        parser.exit(1, f"{exc}\n")

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
