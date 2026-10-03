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
# Unicode White_Space, as used by Rust str::trim(). Python str.strip() additionally
# treats U+001C..U+001F as whitespace, which would change loaded text and byte budgets.
_INSTRUCTION_WHITESPACE = (
    "\u0009\u000a\u000b\u000c\u000d\u0020\u0085\u00a0\u1680"
    "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"
    "\u2028\u2029\u202f\u205f\u3000"
)
_READ_CHUNK_BYTES = 64 * 1024


@dataclass(frozen=True)
class Source:
    path: str
    total_bytes: int
    read_bytes: int
    status: str
    shadowed: list[str]
    outside_root: bool
    text: str = field(repr=False)
    probe_errors: list[str] = field(default_factory=list)


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
            s.status in {"empty", "truncated", "skipped-budget"} or s.outside_root or s.probe_errors
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


def _candidates(directory: Path, names: list[str]) -> tuple[list[Path], list[str]]:
    selected: list[Path] = []
    errors: list[str] = []
    for name in names:
        candidate = directory / name
        try:
            if _is_file(candidate):
                selected.append(candidate)
        except OSError as error:
            if not selected:
                # A failure before selection can change the winning file, so preserve
                # the upstream failure instead of silently choosing a lower priority.
                raise
            errors.append(f"{candidate}: {error.strerror or type(error).__name__}")
    return selected, errors


def _read_prefix(stream, max_bytes: int) -> bytearray:
    # Python accepts arbitrarily large integers, but read(size) takes a native
    # signed integer. Bounded reads also avoid allocating an enormous buffer for
    # a small file when an oversized budget is supplied.
    data = bytearray()
    while len(data) < max_bytes:
        chunk = stream.read(min(max_bytes - len(data), _READ_CHUNK_BYTES))
        if not chunk:
            break
        data.extend(chunk)
    return data


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
            candidates, probe_errors = _candidates(directory, names)
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
                    data = _read_prefix(stream, remaining)
                text = data.decode("utf-8", errors="replace")
                if not text.strip(_INSTRUCTION_WHITESPACE):
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
                    probe_errors,
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
