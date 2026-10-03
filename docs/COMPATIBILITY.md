# Compatibility record

Reference inspected on 2026-10-02:

- Repository commit: `4cedd0caac89f9fdcb5ad385e8093da5363d91c2`.
- [Project discovery and loading](https://github.com/openai/codex/blob/4cedd0caac89f9fdcb5ad385e8093da5363d91c2/codex-rs/core/src/agents_md.rs).
- [Upstream regression tests](https://github.com/openai/codex/blob/4cedd0caac89f9fdcb5ad385e8093da5363d91c2/codex-rs/core/src/agents_md_tests.rs).
- [Settings schema](https://github.com/openai/codex/blob/4cedd0caac89f9fdcb5ad385e8093da5363d91c2/codex-rs/core/config.schema.json).
- [Official guide](https://developers.openai.com/codex/guides/agents-md) (link from the upstream repository; not fetched in this environment).

## Modeled behavior

Nearest project root marker, cwd-only behavior without a marker, root-to-cwd ordering,
one regular file per directory, override precedence, ordered fallback files, empty selected
files, shared raw-byte budget, UTF-8 replacement decoding, symlinked instruction files,
and explicitly supplied untrusted mode.

The schema's `project_doc_max_bytes` default is 32,768. In the source, nonempty project
text consumes the byte budget; whitespace-only selected text is omitted without reducing
the remaining budget. An empty override is still the selected file, with no fallback to
the same directory's ordinary `AGENTS.md`. Separators are added after loading.

## Deliberate inspection differences and limits

- Inputs are explicit. Actual Codex merges configuration layers and evaluates trust, host,
  permissions and environment state; Lens does not infer those settings.
- Only one project environment is modeled. The referenced loader can share its budget
  across multiple selected environments and label their provenance.
- Global/account/thread/internal instructions are host-provided and omitted here.
- Lens resolves cwd/root directory symlinks to physical paths. Upstream discovery does not
  canonicalize paths at that point. Compare physical directory layouts or pass an explicit root.
- Lens reports shadowed files and budget-skipped sources for diagnosis, probing more metadata
  than the loader. With a zero budget, Codex avoids project discovery; Lens still reports
  which sources would be selected, without reading bodies.
- Invalid fallback names are rejected with exit 2 instead of silently ignored. Validation follows
  native path conventions: slash/NUL and dot names are invalid everywhere; Windows also rejects
  backslash/colon. Lens also requires simple native filenames for root markers.
- Lens only opens the selected file up to its remaining byte budget in bounded chunks, rather
  than reading the full file before truncation. Files should remain stable during inspection;
  concurrent edits can make size counts inconsistent.
- Discovery still inspects lower-priority candidates for diagnostics. Failures after selecting
  a valid source are recorded in its `probe_errors` warning list; failures before selection
  remain errors. This preserves the winning source even when a shadowed path is inaccessible.
- Whitespace-only detection uses Unicode White_Space, matching Rust's `str::trim()` rather than
  Python's broader whitespace classification. U+001C–U+001F remain content and consume budget.
- No actual Codex binary integration test has run yet. Tests verify the documented rules
  with synthetic cases; they do not establish compatibility with every release or platform.

Any change to selection or budget semantics must update this record and add a focused regression.
Future parity work should pin a Codex release and compare its loader against the same fixtures.

## 0.1.1 corrections

Reproductions found in maintainer review showed that v0.1.0 could overflow on a byte budget
above the native signed integer size, discard separator control characters as whitespace,
or fail on a shadowed self-referencing symlink despite a valid override. Focused regressions
now cover each case, including the distinction between selected and shadowed metadata errors.
