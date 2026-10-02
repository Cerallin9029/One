"""Command-line interface; instruction bodies are opt-in."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .resolver import DEFAULT_MAX_BYTES, inspect


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="codex-instruction-lens",
        description="Explain Codex project instruction selection with explicit settings.",
        epilog="Does not read Codex config, global instructions, or a running session.",
    )
    result.add_argument("cwd", nargs="?", type=Path, default=Path.cwd())
    result.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    result.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    result.add_argument("--fallback-file", action="append", default=[], metavar="NAME")
    roots = result.add_mutually_exclusive_group()
    roots.add_argument("--root", type=Path, help="explicit ancestor root for simulations")
    roots.add_argument("--root-marker", action="append", metavar="NAME")
    roots.add_argument("--no-root-search", action="store_true", help="inspect cwd only")
    result.add_argument("--untrusted", action="store_true", help="skip project instructions")
    result.add_argument("--json", action="store_true", help="print schema version 1 JSON")
    result.add_argument("--show-text", action="store_true", help="include instruction bodies")
    result.add_argument("--fail-on-warning", action="store_true", help="exit 1 on warnings")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    markers = () if args.no_root_search else tuple(args.root_marker or [".git"])
    try:
        report = inspect(
            args.cwd,
            max_bytes=args.max_bytes,
            fallback_filenames=tuple(args.fallback_file),
            root_markers=markers,
            root=args.root,
            trusted=not args.untrusted,
        )
    except (OSError, ValueError, RuntimeError) as error:
        # Filesystem errors include paths but never file contents.
        if args.json:
            print(json.dumps({"schema_version": 1, "error": str(error)}, ensure_ascii=True))
        else:
            print(f"codex-instruction-lens: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report.to_dict(show_text=args.show_text), indent=2, ensure_ascii=True))
    else:
        # Escape user-controlled paths and content in the metadata view to avoid terminal controls.
        def safe(value: str) -> str:
            return json.dumps(value, ensure_ascii=True)

        print(f"CWD: {safe(report.cwd)}")
        print(f"Root: {safe(report.root)} ({safe(report.root_reason)})")
        print(f"Project budget: {report.consumed_bytes}/{report.max_bytes} bytes")
        print("Scope: project docs only; settings supplied explicitly")
        if not report.trusted:
            print("Project instructions skipped: untrusted mode")
        elif not report.sources:
            print("No project instruction files selected")
        for source in report.sources:
            print(
                f"  {source.status}: {safe(source.path)} "
                f"({source.read_bytes}/{source.total_bytes} bytes read)"
            )
            for path in source.shadowed:
                print(f"    shadowed: {safe(path)}")
            if source.outside_root:
                print("    warning: symlink target is outside project root")
        if args.show_text:
            print("\nCombined project text (JSON escaped):")
            print(safe(report.combined_text))
    return 1 if args.fail_on_warning and report.has_warnings else 0
