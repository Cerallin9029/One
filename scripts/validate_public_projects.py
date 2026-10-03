#!/usr/bin/env python3
"""Validate the installed CLI against pinned public instruction-file blobs.

This developer helper uses Git plus Python's standard library. It does not run
Codex, contact a service, execute project instructions, or save their bodies.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True)
class Project:
    checkout: str
    repository: str
    commit: str
    cwd: str = "."


PROJECTS = (
    Project("agents-md", "agentsmd/agents.md", "d001185d792eb6402a58e4cbef1c228b309ec25d"),
    Project("uv", "astral-sh/uv", "ba5833f0988962079e75894490f576c7f8cccf49"),
    Project(
        "codex",
        "openai/codex",
        "8f7a0f7a878199c6886600370e5be6bd37ca38a3",
        "codex-rs/tui/src/bottom_pane",
    ),
)
CANDIDATES = ("AGENTS.override.md", "AGENTS.md")
DEFAULT_BUDGET = 32768
CONSTRAINED_BUDGET = 128
# Rust char::is_whitespace uses Unicode White_Space, rather than Python's
# additional U+001C..U+001F separators. No resolver code is imported here.
RUST_WHITESPACE = "\t\n\v\f\r \u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005"
RUST_WHITESPACE += "\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000"


def command(args: list[str], *, cwd: Path) -> bytes:
    result = subprocess.run(args, cwd=cwd, capture_output=True, check=False)
    if result.returncode:
        # Keep instruction bodies out of failures too: do not print subprocess output.
        raise ValueError(f"{args[0]} command failed with exit {result.returncode}")
    return result.stdout


def git(checkout: Path, *args: str) -> bytes:
    return command(["git", "-C", str(checkout), *args], cwd=checkout)


def relative(path: str, checkout: Path) -> str:
    try:
        return Path(path).relative_to(checkout).as_posix()
    except ValueError as error:
        raise ValueError("CLI reported a path outside the public checkout") from error


def selected_blobs(project: Project, checkout: Path) -> tuple[list[str], list[dict]]:
    head = git(checkout, "rev-parse", "HEAD").decode().strip()
    if head != project.commit:
        raise ValueError(f"{project.checkout}: HEAD must equal pinned commit {project.commit}")
    if not (checkout / ".git").exists():
        raise ValueError(f"{project.checkout}: checkout must contain its own .git marker")

    tree = {}
    for entry in git(checkout, "ls-tree", "-r", "-z", project.commit).split(b"\0"):
        if not entry:
            continue
        header, raw_path = entry.split(b"\t", 1)
        path = raw_path.decode("utf-8")
        if PurePosixPath(path).name in CANDIDATES:
            mode, kind, blob_sha = header.decode("ascii").split()
            if kind != "blob" or mode not in {"100644", "100755"}:
                raise ValueError(f"{project.checkout}: fixture requires regular instruction files")
            tree[path] = blob_sha

    cwd = PurePosixPath(project.cwd)
    directories = [*(parent.as_posix() for parent in reversed(cwd.parents)), cwd.as_posix()]
    if not (checkout / project.cwd).is_dir():
        raise ValueError(f"{project.checkout}: selected cwd is absent from the sparse checkout")
    sources = []
    for directory in directories:
        if directory != "." and (checkout / directory / ".git").exists():
            raise ValueError(f"{project.checkout}: unexpected nested .git marker")
        candidates = []
        for name in CANDIDATES:
            path = (PurePosixPath(directory) / name).as_posix()
            physical = checkout / path
            if path not in tree:
                if physical.exists() or physical.is_symlink():
                    raise ValueError(f"{project.checkout}: unpinned instruction file at {path}")
                continue
            data = git(checkout, "cat-file", "blob", tree[path])
            if physical.is_symlink() or not physical.is_file() or physical.read_bytes() != data:
                raise ValueError(
                    f"{project.checkout}: working file differs from pinned blob {path}"
                )
            candidates.append({"path": path, "git_blob_sha": tree[path], "data": data})
        if candidates:
            source = candidates[0]
            source["shadowed"] = [item["path"] for item in candidates[1:]]
            sources.append(source)
    return directories, sources


def expected_sources(blobs: list[dict], budget: int) -> tuple[list[dict], int]:
    remaining = budget
    sources = []
    for blob in blobs:
        data = blob["data"][:remaining]
        if remaining == 0:
            status = "skipped-budget"
        elif not data.decode("utf-8", errors="replace").strip(RUST_WHITESPACE):
            status = "empty"
        else:
            status = "truncated" if len(data) < len(blob["data"]) else "loaded"
            remaining -= len(data)
        sources.append(
            {
                "path": blob["path"],
                "total_bytes": len(blob["data"]),
                "read_bytes": len(data),
                "status": status,
                "shadowed": blob["shadowed"],
                "outside_root": False,
                "probe_errors": [],
            }
        )
    return sources, budget - remaining


def validate_run(
    project: Project,
    checkout: Path,
    directories: list[str],
    blobs: list[dict],
    *,
    constrained: bool,
) -> dict:
    args = [sys.executable, "-m", "instruction_lens", str(checkout / project.cwd), "--json"]
    budget = CONSTRAINED_BUDGET if constrained else DEFAULT_BUDGET
    if constrained:
        args.extend(["--max-bytes", str(budget)])
    report = json.loads(command(args, cwd=checkout))
    expected, consumed = expected_sources(blobs, budget)
    actual = []
    for source in report["sources"]:
        if "text" in source:
            raise ValueError("Default CLI JSON unexpectedly includes an instruction body")
        if source.get("probe_errors") != []:
            raise ValueError(f"{project.checkout}: CLI reported unexpected metadata probe errors")
        actual.append(
            {
                "path": relative(source["path"], checkout),
                "total_bytes": source["total_bytes"],
                "read_bytes": source["read_bytes"],
                "status": source["status"],
                "shadowed": [relative(path, checkout) for path in source["shadowed"]],
                "outside_root": source["outside_root"],
                "probe_errors": [],
            }
        )
    checks = (
        report["schema_version"] == 1,
        report["trusted"] is True,
        report["candidate_filenames"] == list(CANDIDATES),
        relative(report["cwd"], checkout) == project.cwd,
        relative(report["root"], checkout) == ".",
        [relative(path, checkout) for path in report["searched_directories"]] == directories,
        report["max_bytes"] == budget,
        report["consumed_bytes"] == consumed,
        "combined_text" not in report,
        actual == expected,
    )
    if not all(checks):
        raise ValueError(
            f"{project.checkout}: {budget}-byte CLI report differs from Git expectations"
        )
    for source, blob in zip(actual, blobs, strict=True):
        source["git_blob_sha"] = blob["git_blob_sha"]
        source["blob_url"] = (
            f"https://github.com/{project.repository}/blob/{project.commit}/{source['path']}"
        )
    return {
        "budget_mode": "constrained" if constrained else "default",
        "max_bytes": budget,
        "consumed_bytes": consumed,
        "cli_exit_code": 0,
        "selection_and_byte_counts_verified": True,
        "loader_reference_sha": report["reference_sha"],
        "searched_directories": directories,
        "sources": actual,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkouts", required=True, type=Path, help="parent of the three checkouts"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs/validation/public-projects.json",
    )
    args = parser.parse_args()
    try:
        checkouts = args.checkouts.expanduser().resolve(strict=True)
        version = (
            command([sys.executable, "-m", "instruction_lens", "--version"], cwd=checkouts)
            .decode()
            .strip()
        )
        projects = []
        for project in PROJECTS:
            checkout = (checkouts / project.checkout).resolve(strict=True)
            directories, blobs = selected_blobs(project, checkout)
            projects.append(
                {
                    "repository": project.repository,
                    "commit": project.commit,
                    "cwd": project.cwd,
                    "working_files_match_pinned_git_blobs": True,
                    "runs": [
                        validate_run(project, checkout, directories, blobs, constrained=constrained)
                        for constrained in (False, True)
                    ],
                }
            )
        artifact = {
            "schema_version": 1,
            "validation_kind": "maintainer-run public-repository fixtures",
            "cli_version": version,
            "actual_codex_binary_parity_verified": False,
            "external_adoption_claimed": False,
            "projects": projects,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1
    print("Verified 3 pinned public checkouts and 6 CLI reports; saved a body-free JSON report.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
