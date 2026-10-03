# v0.1.1 release notes

This patch fixes three reproducible loader problems:

- A huge `--max-bytes` value no longer causes an uncaught native-integer overflow when loading
  a small file. Reads use bounded chunks.
- U+001C–U+001F now remain content, matching Rust whitespace rules and preserving byte-budget
  accounting for deeper instructions.
- An inaccessible lower-priority candidate no longer prevents loading a valid override.
  The report records a `probe_errors` warning. Failures before selection still produce exit 2.

The package requires Python 3.11+ and no runtime dependencies. Install a release wheel or the
tagged source, then run `codex-instruction-lens .`. Default reports continue to omit bodies.

See `docs/VALIDATION.md` for maintainer checks against three pinned public repository snapshots.
These are tool validation, not external adoption or evidence of actual Codex binary parity.
The product still models one project environment with explicit settings; global/account
instructions and configuration layers are outside its scope.

Release publication is tracked in `docs/EVIDENCE.md`; these prepared notes alone do not prove
that a release has been published.
