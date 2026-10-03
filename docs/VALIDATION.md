# Reproducible public-project validation

This is **maintainer validation**, using real public instruction files as fixtures. It is
not external adoption, a recommendation from those maintainers, or parity verified by
running a Codex binary. The projects were selected for existing AI/developer instruction
files; no project instructions are executed and no maintainers are contacted.

The [developer helper](../scripts/validate_public_projects.py) runs the installed Lens CLI
with `--json`, independently derives the expected source chain from each pinned Git tree,
and compares file sizes, read sizes, statuses, shadowed paths and consumed byte counts.
It first checks the exact checkout commit and requires the relevant working files to
match their pinned Git blobs. It uses only Python's standard library plus Git, and imports
no Lens resolver code.

The checked-in [report](validation/public-projects.json) contains repository-relative paths,
commit and blob IDs, source links, counts and statuses. It contains no absolute local
paths or instruction bodies. Reports use the default 32,768-byte budget and an explicit
128-byte constrained budget. Source text is not requested from the CLI.

| Public repository | Pinned commit | Inspected cwd | Selected file size | Default result | 128-byte result |
| --- | --- | --- | --- | --- | --- |
| [agentsmd/agents.md](https://github.com/agentsmd/agents.md) | `d001185d792eb6402a58e4cbef1c228b309ec25d` | `.` | 2,031 bytes | Loaded in full | Truncated to 128 bytes |
| [astral-sh/uv](https://github.com/astral-sh/uv) | `ba5833f0988962079e75894490f576c7f8cccf49` | `.` | 2,432 bytes | Loaded in full | Truncated to 128 bytes |
| [openai/codex](https://github.com/openai/codex) | `8f7a0f7a878199c6886600370e5be6bd37ca38a3` | `codex-rs/tui/src/bottom_pane` | 564 bytes | Loaded in full | Truncated to 128 bytes |

Each inspected source chain selects one `AGENTS.md`. The Codex case also checks traversal
through five directories from the repository root to cwd. These cases do not cover every
precedence, whitespace, symlink, trust or encoding rule; the synthetic regression suite
covers additional edge cases. The Codex repository fixture commit and Lens's modeled
loader reference commit serve different purposes and need not match.

## Reproduce

Start from a Lens source checkout and install it into a Python 3.11+ environment:

```sh
python -m pip install -e .
```

Prepare these directory names beneath a directory of your choice. These commands fetch
the exact commits and materialize only tracked instruction files. They use Git's
non-cone sparse checkout so the project source trees do not need to be checked out.
The remote may still transfer other Git objects, depending on its filter support.

```sh
mkdir -p /tmp/lens-public-projects

git init /tmp/lens-public-projects/agents-md
git -C /tmp/lens-public-projects/agents-md remote add origin https://github.com/agentsmd/agents.md.git
git -C /tmp/lens-public-projects/agents-md fetch --depth=1 --filter=blob:none origin d001185d792eb6402a58e4cbef1c228b309ec25d
git -C /tmp/lens-public-projects/agents-md sparse-checkout set --no-cone -- AGENTS.md AGENTS.override.md
git -C /tmp/lens-public-projects/agents-md -c core.autocrlf=false checkout --detach FETCH_HEAD

git init /tmp/lens-public-projects/uv
git -C /tmp/lens-public-projects/uv remote add origin https://github.com/astral-sh/uv.git
git -C /tmp/lens-public-projects/uv fetch --depth=1 --filter=blob:none origin ba5833f0988962079e75894490f576c7f8cccf49
git -C /tmp/lens-public-projects/uv sparse-checkout set --no-cone -- AGENTS.md AGENTS.override.md
git -C /tmp/lens-public-projects/uv -c core.autocrlf=false checkout --detach FETCH_HEAD

git init /tmp/lens-public-projects/codex
git -C /tmp/lens-public-projects/codex remote add origin https://github.com/openai/codex.git
git -C /tmp/lens-public-projects/codex fetch --depth=1 --filter=blob:none origin 8f7a0f7a878199c6886600370e5be6bd37ca38a3
git -C /tmp/lens-public-projects/codex sparse-checkout set --no-cone -- AGENTS.md AGENTS.override.md
git -C /tmp/lens-public-projects/codex -c core.autocrlf=false checkout --detach FETCH_HEAD

python scripts/validate_public_projects.py --checkouts /tmp/lens-public-projects
```

Sparse patterns without a slash match those filenames at every depth. The Codex fixture
therefore includes its nested `codex-rs/tui/src/bottom_pane/AGENTS.md`. Run the final Python
command from the Lens checkout, using the same Python environment used for installation.
The checkout commands disable automatic CRLF conversion so working bytes match Git blobs.
It exits nonzero if a fixture is missing or modified, a commit is different, or the CLI
differs from the Git-derived expectations. Successful validation overwrites the body-free
report only after all six runs pass. Use `--output /tmp/lens-validation.json` to choose an
alternative destination.

Refreshing these fixtures requires an intentional change to the helper's pins and a new
validation run. A future upstream change is not silently substituted for the recorded
source. Running the helper does not establish that any third party uses Lens.
