from __future__ import annotations

import argparse
import json
from pathlib import Path

from .editorial import (
    check_published,
    promote_run,
    publish_transcript,
    render_editorial_check,
    write_published_index,
)
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

    promote_parser = subparsers.add_parser(
        "promote",
        help="Create a cleaned transcript scaffold from a run directory.",
    )
    promote_parser.add_argument("run_dir", help="Path to a raw run directory.")
    promote_parser.add_argument(
        "--output",
        required=True,
        help="Transcript markdown path to write.",
    )

    publish_parser = subparsers.add_parser(
        "publish",
        help="Create a published markdown scaffold from a cleaned transcript.",
    )
    publish_parser.add_argument("transcript", help="Path to cleaned transcript.")
    publish_parser.add_argument(
        "--output",
        required=True,
        help="Published markdown path to write.",
    )

    check_parser = subparsers.add_parser(
        "check",
        help="Check a published markdown file for required editorial metadata.",
    )
    check_parser.add_argument("published_file", help="Published markdown path.")

    index_parser = subparsers.add_parser(
        "index",
        help="Generate an index of published roundtables.",
    )
    index_parser.add_argument(
        "--published-dir",
        default="published",
        help="Directory containing published markdown files.",
    )
    index_parser.add_argument(
        "--output",
        default="published/INDEX.md",
        help="Index markdown path to write.",
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

        if args.command == "promote":
            promote_run(Path(args.run_dir), Path(args.output))
            print(f"Transcript scaffold written to {args.output}")
            return 0

        if args.command == "publish":
            publish_transcript(Path(args.transcript), Path(args.output))
            print(f"Published scaffold written to {args.output}")
            return 0

        if args.command == "check":
            check = check_published(Path(args.published_file), repo_root=repo_root)
            print(render_editorial_check(check))
            return 0 if check.passed else 1

        if args.command == "index":
            write_published_index(Path(args.published_dir), Path(args.output))
            print(f"Published index written to {args.output}")
            return 0
    except ConfigError as exc:
        parser.exit(1, f"{exc}\n")
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
