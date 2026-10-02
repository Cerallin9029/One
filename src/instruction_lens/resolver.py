"""An explicit-input simulation of single-environment project doc discovery.

Behavior reference: openai/codex at 4cedd0caac89f9fdcb5ad385e8093da5363d91c2.
This module does not load account instructions, config files, or host policy.
"""

from __future__ import annotations

import os
import stat
from dataclasses import asdict, dataclass, field
from pathlib import Path

REFERENCE_SHA = "4cedd0caac89f9fdcb5ad385e8093da5363d91c2"
DEFAULT_MAX_BYTES = 32768


@dataclass(frozen=True)
class Source:
    path: str
    total_bytes: int
    read_bytes: int
    status: str
    shadowed: list[str]
    outside_root: bool
    text: str = field(repr=False)


@dataclass(frozen=True)
class Report:
    cwd: str
    root: str
    root_reason: str
    max_bytes: int
    consumed_bytes: int
    candidate_filenames: list[str]
    searched_directories: list[str]
    sources: list[Source]
    trusted: bool

    def to_dict(self, *, show_text: bool = False) -> dict:
        result = asdict(self)
        result["schema_version"] = 1
        result["reference_sha"] = REFERENCE_SHA
        result["scope"] = "single-environment project documents; explicit settings"
        if not show_text:
            for source in result["sources"]:
                del source["text"]
        else:
            result["combined_text"] = self.combined_text
        return result

    @property
    def combined_text(self) -> str:
        return "\n\n".join(s.text for s in self.sources if s.status in {"loaded", "truncated"})

    @property
    def has_warnings(self) -> bool:
        return any(
            s.status in {"empty", "truncated", "skipped-budget"} or s.outside_root
            for s in self.sources
        )


def _filename(value: str) -> str:
    """Validate native filenames before probing (Windows paths are stricter)."""
    if (
        not value
        or value in {".", ".."}
        or "/" in value
        or "\0" in value
        or (os.name == "nt" and ("\\" in value or ":" in value))
    ):
        raise ValueError("candidate and marker names must be non-empty native filenames")
    return value


def _is_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.stat().st_mode)
    except FileNotFoundError:
        return False


def _root_for(cwd: Path, markers: list[str]) -> tuple[Path, str]:
    if not markers:
        return cwd, "parent traversal disabled"
    for directory in (cwd, *cwd.parents):
        for marker in markers:
            try:
                (directory / marker).stat()
            except OSError:
                continue
            return directory, f"nearest ancestor with {marker}"
    return cwd, "no root marker found; cwd only"


def inspect(
    cwd: Path,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    fallback_filenames: tuple[str, ...] = (),
    root_markers: tuple[str, ...] = (".git",),
    root: Path | None = None,
    trusted: bool = True,
) -> Report:
    if max_bytes < 0:
        raise ValueError("max_bytes must be non-negative")
    cwd = cwd.expanduser().resolve(strict=True)
    if not cwd.is_dir():
        raise ValueError("cwd must be an existing directory")
    names = list(dict.fromkeys(["AGENTS.override.md", "AGENTS.md", *fallback_filenames]))
    names = [_filename(name) for name in names]
    markers = [_filename(marker) for marker in root_markers]
    if root is None:
        project_root, reason = _root_for(cwd, markers)
    else:
        project_root = root.expanduser().resolve(strict=True)
        if not project_root.is_dir() or not cwd.is_relative_to(project_root):
            raise ValueError("root must be cwd or one of its ancestor directories")
        reason = "explicit root override"
    directories = [cwd]
    while directories[-1] != project_root:
        directories.append(directories[-1].parent)
    directories.reverse()
    sources: list[Source] = []
    remaining = max_bytes
    if trusted:
        for directory in directories:
            candidates = [directory / name for name in names if _is_file(directory / name)]
            if not candidates:
                continue
            chosen, *shadowed = candidates
            outside_root = not chosen.resolve().is_relative_to(project_root)
            if remaining == 0:
                total = chosen.stat().st_size
                data = b""
                status = "skipped-budget"
                text = ""
            else:
                with chosen.open("rb") as stream:
                    total = os.fstat(stream.fileno()).st_size
                    data = stream.read(remaining)
                text = data.decode("utf-8", errors="replace")
                if not text.strip():
                    status = "empty"
                else:
                    status = "truncated" if total > len(data) else "loaded"
                    remaining -= len(data)
            sources.append(
                Source(
                    str(chosen),
                    total,
                    len(data),
                    status,
                    [str(path) for path in shadowed],
                    outside_root,
                    text,
                )
            )
    return Report(
        str(cwd),
        str(project_root),
        reason,
        max_bytes,
        max_bytes - remaining,
        names,
        [str(directory) for directory in directories] if trusted else [],
        sources,
        trusted,
    )
