# v0.1.0 release notes (prepared; not a published GitHub Release)

Codex Instruction Lens explains project instruction selection for a local working directory.
It shows the root-to-cwd chain, override precedence, hidden candidate files, empty selected
content and byte-budget truncation. JSON reports hide instruction bodies by default;
`--show-text` includes them. The core needs Python 3.11+ and no runtime dependencies.

Install from an accessible source checkout with `python -m pip install .`.
Run the bundled example:

```sh
codex-instruction-lens examples/monorepo/apps/api/src --root examples/monorepo
```

20 regression tests pass locally and the four-job Linux/macOS/Windows CI matrix passed for
the implementation in PR #1. The wheel was installed and tested in a separate virtual environment.

This alpha models one project's documents with explicit settings and a pinned upstream source.
It does not inspect running sessions, Codex config layers or account/global instructions.
See `docs/COMPATIBILITY.md` for behavior boundaries and symlink/metadata differences.

Publication checklist: verify public repository visibility, tag the tested source, create the
GitHub Release, and test anonymous source installation. The package is not on PyPI.
