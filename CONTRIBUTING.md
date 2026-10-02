# Contributing

Start with a reproducible problem: a minimal directory tree, explicit options, expected
selection and actual report. Use synthetic instruction bodies and redact personal paths.
For behavior claims, link a pinned upstream source or a reproducible Codex release result.

Install the development tools listed in README, run the regression suite, lint and formatting
checks, and build the package. Keep the runtime dependency-free and filesystem operations
read-only. Add a regression for a behavioral fix, not for documentation-only edits.

Open a focused PR explaining the user-visible change and validation. Configuration import,
context comparisons and broader parity are roadmap candidates; discuss their scope before
adding a large feature. Maintainer: [@Cerallin9029](https://github.com/Cerallin9029).
