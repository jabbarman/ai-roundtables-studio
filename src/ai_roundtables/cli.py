from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audio import build_and_render_audio, create_audio_script, render_audio_script
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

    audio_script_parser = subparsers.add_parser(
        "audio-script",
        help="Create an audio-ready script JSON from a published roundtable.",
    )
    audio_script_parser.add_argument("published_file", help="Published markdown path.")
    audio_script_parser.add_argument(
        "--output",
        required=True,
        help="Audio script JSON path to write.",
    )
    audio_script_parser.add_argument(
        "--max-segments",
        type=int,
        help="Limit script generation to the first N speaker turns.",
    )
    audio_script_parser.add_argument(
        "--max-segment-chars",
        type=int,
        help="Trim each speaker turn to a sentence boundary near this length.",
    )
    audio_script_parser.add_argument(
        "--voice-profile",
        default="intended",
        choices=["intended", "free-check"],
        help="Voice assignment profile to use.",
    )
    audio_script_parser.add_argument(
        "--intro",
        help="Optional moderator intro text. Use {title} for the roundtable title.",
    )
    audio_script_parser.add_argument(
        "--outro",
        help="Optional moderator outro text. Use {title} for the roundtable title.",
    )
    audio_script_parser.add_argument(
        "--pause-after-ms",
        type=int,
        default=450,
        help="Pause metadata to attach after each segment.",
    )
    audio_script_parser.add_argument(
        "--pronunciations",
        help="JSON replacement map for audio pronunciation cleanup.",
    )

    audio_render_parser = subparsers.add_parser(
        "audio-render",
        help="Render an audio script through ElevenLabs.",
    )
    audio_render_parser.add_argument("script", help="Audio script JSON path.")
    audio_render_parser.add_argument(
        "--output",
        required=True,
        help="MP3 output path to write.",
    )
    audio_render_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the script and print a render manifest without calling ElevenLabs.",
    )
    audio_render_parser.add_argument(
        "--output-format",
        default="mp3_44100_128",
        help="ElevenLabs output format.",
    )
    audio_render_parser.add_argument(
        "--chunk-chars",
        type=int,
        default=1800,
        help="Approximate maximum characters per dialogue request.",
    )
    audio_render_parser.add_argument(
        "--mode",
        default="dialogue",
        choices=["dialogue", "segments"],
        help="Render as multi-speaker dialogue chunks or retryable per-segment files.",
    )
    audio_render_parser.add_argument(
        "--parts-dir",
        help="Directory for per-segment MP3 parts when --mode segments is used.",
    )
    audio_render_parser.add_argument(
        "--manifest",
        help="Path to write a render manifest JSON.",
    )
    audio_render_parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate existing per-segment parts.",
    )
    audio_render_parser.add_argument(
        "--pause-style",
        default="none",
        choices=["none", "ssml"],
        help="How to apply pause metadata during segment rendering.",
    )

    audio_build_parser = subparsers.add_parser(
        "audio-build",
        help="Create an audio script and optionally render it in one command.",
    )
    audio_build_parser.add_argument("published_file", help="Published markdown path.")
    audio_build_parser.add_argument(
        "--script-output",
        required=True,
        help="Audio script JSON path to write.",
    )
    audio_build_parser.add_argument(
        "--output",
        required=True,
        help="MP3 output path to write.",
    )
    audio_build_parser.add_argument("--manifest", help="Render manifest JSON path.")
    audio_build_parser.add_argument("--dry-run", action="store_true")
    audio_build_parser.add_argument("--max-segments", type=int)
    audio_build_parser.add_argument("--max-segment-chars", type=int)
    audio_build_parser.add_argument(
        "--voice-profile",
        default="intended",
        choices=["intended", "free-check"],
    )
    audio_build_parser.add_argument("--intro")
    audio_build_parser.add_argument("--outro")
    audio_build_parser.add_argument("--pause-after-ms", type=int, default=450)
    audio_build_parser.add_argument("--pronunciations")
    audio_build_parser.add_argument("--output-format", default="mp3_44100_128")
    audio_build_parser.add_argument("--chunk-chars", type=int, default=1800)
    audio_build_parser.add_argument(
        "--mode",
        default="dialogue",
        choices=["dialogue", "segments"],
    )
    audio_build_parser.add_argument("--parts-dir")
    audio_build_parser.add_argument("--force", action="store_true")
    audio_build_parser.add_argument(
        "--pause-style",
        default="none",
        choices=["none", "ssml"],
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

        if args.command == "audio-script":
            script = create_audio_script(
                Path(args.published_file),
                output_path=Path(args.output),
                max_segments=args.max_segments,
                max_segment_chars=args.max_segment_chars,
                intro_text=args.intro,
                outro_text=args.outro,
                pause_after_ms=args.pause_after_ms,
                pronunciation_path=Path(args.pronunciations)
                if args.pronunciations
                else None,
                voice_profile=args.voice_profile,
            )
            print(
                f"Audio script written to {args.output} "
                f"({len(script.segments)} segments)"
            )
            return 0

        if args.command == "audio-render":
            manifest = render_audio_script(
                Path(args.script),
                output_path=Path(args.output),
                dry_run=args.dry_run,
                output_format=args.output_format,
                chunk_chars=args.chunk_chars,
                mode=args.mode,
                parts_dir=Path(args.parts_dir) if args.parts_dir else None,
                manifest_path=Path(args.manifest) if args.manifest else None,
                force=args.force,
                pause_style=args.pause_style,
            )
            print(json.dumps(manifest, indent=2))
            return 0

        if args.command == "audio-build":
            manifest = build_and_render_audio(
                Path(args.published_file),
                script_path=Path(args.script_output),
                output_path=Path(args.output),
                dry_run=args.dry_run,
                max_segments=args.max_segments,
                max_segment_chars=args.max_segment_chars,
                intro_text=args.intro,
                outro_text=args.outro,
                pause_after_ms=args.pause_after_ms,
                pronunciation_path=Path(args.pronunciations)
                if args.pronunciations
                else None,
                voice_profile=args.voice_profile,
                output_format=args.output_format,
                chunk_chars=args.chunk_chars,
                mode=args.mode,
                parts_dir=Path(args.parts_dir) if args.parts_dir else None,
                manifest_path=Path(args.manifest) if args.manifest else None,
                force=args.force,
                pause_style=args.pause_style,
            )
            print(json.dumps(manifest, indent=2))
            return 0
    except ConfigError as exc:
        parser.exit(1, f"{exc}\n")
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
