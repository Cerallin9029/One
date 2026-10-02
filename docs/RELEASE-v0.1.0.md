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

Repository visibility is now public and verified. The `v0.1.0` tag exists, and installing
that tagged source in a fresh virtual environment succeeds. A GitHub Release has not yet
been created. The package is not on PyPI.

## Release workflow

`.github/workflows/release.yml` builds a version tag, checks that it matches package metadata,
runs regressions and lint, tests the built wheel, and attaches a wheel, source archive and
SHA-256 checksums to a GitHub Release. Publication happens after all assets upload; failed
uploads leave a draft that can be retried. A published release is left unchanged on reruns.

Future stable `vMAJOR.MINOR.PATCH` tag pushes trigger this workflow. For the existing `v0.1.0`
tag (created before the workflow existed), run the Release workflow manually from the
repository's Actions tab after this workflow is merged into main. Select `main` as the
workflow branch and `v0.1.0` as the tag input. The workflow checks out the tag's exact source.

The release workflow has not yet run. A private repository's release remains accessible only
to people with repository access; release creation does not make the repository public.
