# Codex Instruction Lens

Explain which **project instruction files** Codex selects for a working directory, why an
override hides another file, and where a byte budget truncates the content.

[中文说明](docs/README.zh-CN.md) · [Compatibility](docs/COMPATIBILITY.md) ·
[Contributing](CONTRIBUTING.md)

An independent, local tool. Python 3.11+, no runtime dependencies, no model calls.
It does not read Codex credentials, config files or account instructions, or execute instructions.
This is an explicit-settings simulation of project document discovery, not a running-session audit.

## Try it

From a source checkout:

```sh
python -m pip install .
codex-instruction-lens .
```

The repository is public. To install the tagged source directly:

```sh
python -m pip install "git+https://github.com/Cerallin9029/One.git@v0.1.1"
codex-instruction-lens --version
```

The package has not been published to PyPI. Install from a checkout, not by package name alone.

Reproduce nested instructions using the bundled synthetic example:

```sh
codex-instruction-lens examples/monorepo/apps/api/src --root examples/monorepo
```

The report selects `examples/monorepo/AGENTS.md`, then
`examples/monorepo/apps/api/AGENTS.override.md`. The API's `AGENTS.md` is reported as
shadowed. Files in sibling directories are outside the search chain.

## Usage

```sh
# Structured report without instruction bodies
codex-instruction-lens path/to/workdir --json

# Simulate settings you pass to Codex
codex-instruction-lens . --max-bytes 16384 --fallback-file TEAM.md

# Show selected project text explicitly (JSON escaped)
codex-instruction-lens . --show-text

# Fail CI on empty files, truncation, skipped files, external symlinks or probe warnings
codex-instruction-lens . --fail-on-warning

# Simulate an untrusted project, or disable ancestor traversal
codex-instruction-lens . --untrusted
codex-instruction-lens . --no-root-search
```

`cwd` must be an existing directory. The default root is the nearest ancestor containing
`.git`, including a Git worktree's `.git` file. Without a marker, only `cwd` is searched.
`--root-marker NAME` replaces the default marker list; repeat it for multiple markers.
`--root PATH` is an explicit simulation override and must be an ancestor of `cwd`.

One regular file per directory wins: `AGENTS.override.md`, then `AGENTS.md`, then configured
fallback names in order. An **empty override still hides the standard file**. Nonempty
selected content consumes a shared project byte budget (default 32,768 bytes). UTF-8 cuts
are decoded with replacement, matching the referenced upstream single-environment loader.
Separators between files do not consume that budget.

JSON output has `schema_version: 1`, a pinned upstream reference, inputs, searched directories,
selected sources, shadowed paths, byte counts, status and `probe_errors` warnings for lower-priority
paths that could not be inspected. `--show-text` adds source bodies and
`combined_text`. Exit codes: `0` completed, `1` warnings with `--fail-on-warning`, `2` invalid
input or filesystem error. Warnings are inspection findings, not proof of incorrect instructions.

## Boundaries

The tool currently models **one trusted or explicitly untrusted local project environment**.
It does not load global/home instructions, config profiles, system policy, layered `.codex`
configuration, developer instructions, skills or MCP content. Pass relevant settings explicitly.
It resolves the working directory to its physical path; symlinked directory layouts can differ
from Codex's lexical paths. It cannot predict whether a model will follow the loaded instructions.

Default reports hide bodies but contain local paths. Review them before sharing. Symlinked
instruction files are followed, as in upstream; targets outside the root are reported.

Compatibility is tied to a source snapshot, not every Codex version. See the
[compatibility record](docs/COMPATIBILITY.md) for source links and inspection differences.

Maintainer validation against three pinned public repository snapshots is documented in
[the validation report](docs/VALIDATION.md). These checks are not external adoption evidence.

## Development

```sh
python -m pip install -e . ruff==0.11.13 build==1.2.2.post1
python -m unittest discover -s tests -v
python -m ruff check .
python -m ruff format --check .
python -m build
```

The CI matrix covers Linux (Python 3.11 and 3.13), macOS (3.12), and Windows (3.12).
MIT licensed. Not affiliated with or endorsed by OpenAI.
