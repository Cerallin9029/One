# Changelog

## 0.1.1 — loader robustness

- Read selected files in bounded chunks so oversized budgets do not overflow Python's native
  `read(size)` argument or request an enormous buffer for a small file.
- Match Rust Unicode whitespace rules so U+001C–U+001F remain instruction content and consume
  the correct byte budget.
- Preserve valid overrides when lower-priority candidate metadata fails; record a probe warning
  while keeping pre-selection access errors fatal.
- Include a reproducible, body-free maintainer validation report for three pinned public repositories.

## 0.1.0 — initial implementation

- Explain root-to-cwd project instruction discovery and per-directory precedence.
- Report empty overrides, shadowed sources, truncation and budget-skipped files.
- Provide JSON reports, opt-in instruction bodies and CI-oriented warning exit codes.
- Include synthetic nested-project examples and upstream compatibility boundaries.

This entry describes the source version. A GitHub release and PyPI publication are tracked
separately in the evidence ledger.
