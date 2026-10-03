# Evidence ledger

Updated: 2026-10-03 (Asia/Shanghai). Record verifiable facts with links and dates.
Do not count author tests as external adoption or this plan as completed maintenance.

| Category | Verified state | Evidence |
| --- | --- | --- |
| GitHub control | Authenticated account owns `Cerallin9029/One`; push and admin permissions reported | GitHub connector profile and repository metadata read on 2026-10-02 |
| Starting state | Private repository, only initialization README | Base commit `cc99226ead7cfff7f52133d21323ee829824f00d` |
| Technical reference | Official Codex source and settings schema inspected | [Pinned source](https://github.com/openai/codex/blob/4cedd0caac89f9fdcb5ad385e8093da5363d91c2/codex-rs/core/src/agents_md.rs) |
| First implementation | Source version 0.1.0 integrated into main | [Merged PR #1](https://github.com/Cerallin9029/One/pull/1), merge commit `50a0482aca87a095bcece29a5c0182ffe435fe48` |
| Loader corrections | Three maintainer-reproduced failures fixed in version 0.1.1 | [Merged PR #4](https://github.com/Cerallin9029/One/pull/4), tagged merge commit `7f54bb3f02a2e9a74e1ba65327f7db2f2b71bd38` |
| Initial local validation | 20 regression tests passed on Linux / Python 3.12 for 0.1.0; lint and formatting passed; source and wheel built | `python -m unittest discover -s tests -v`, `python -m ruff check .`, `python -m ruff format --check .`, `python -m build` |
| 0.1.1 local validation | 27 regression tests passed on Linux / Python 3.12; lint and formatting passed; source and wheel built | Same commands above; three maintainer-reproduced edge cases are described in [the changelog](../CHANGELOG.md) |
| Real-project fixtures | Six CLI checks passed against pinned instruction files from three public repositories: default and 128-byte budgets | [Reproduction steps](VALIDATION.md) and [body-free report](validation/public-projects.json); this is maintainer testing, not external adoption or Codex-binary parity |
| Remote CI | All four jobs passed for the 0.1.1 changes: Linux Python 3.11/3.13, macOS Python 3.12, Windows Python 3.12 | [CI run for PR #4](https://github.com/Cerallin9029/One/actions/runs/37090394785) at source commit `805787cab1010c13f368702b5a212e4d81088b13` |
| Public project | Repository is public, verified on 2026-10-03 | [Repository](https://github.com/Cerallin9029/One), GitHub API returned `private: false`, `visibility: public` |
| Tagged source installation | `v0.1.0` installed from GitHub into a fresh virtual environment; CLI returned `0.1.0` on 2026-10-03 | `python -m pip install git+https://github.com/Cerallin9029/One.git@v0.1.0`, `codex-instruction-lens --version` |
| GitHub Release | v0.1.1 publicly published on 2026-10-03 with wheel, source archive and SHA256SUMS; tag-triggered workflow completed successfully | [Release](https://github.com/Cerallin9029/One/releases/tag/v0.1.1), [publication run](https://github.com/Cerallin9029/One/actions/runs/37090450148) |
| Published-asset verification | Downloaded both actual release packages, verified SHA-256, installed the wheel into a fresh environment, and repeated all six project checks with byte-identical report output | CLI returned `0.1.1`; [fixture expectations](validation/public-projects.json) |
| PyPI | Not published | No download statistics |
| External users/feedback | None observed or claimed | Add genuine attributable evidence when available |
| Application | Not submitted | Official live form and terms still require direct verification |

Next publication/official-verification work: [maintainer planning issue #2](https://github.com/Cerallin9029/One/issues/2).
On 2026-10-03 the maintainer requested manual, irregular continuation. The previously created
scheduled task was disabled. Future project work starts when the maintainer requests it;
the 12-week roadmap is a reference for stages, not an automatic execution schedule.

Implementation and initial tests were built with Codex at the maintainer's request.
The maintainer has not yet independently reviewed the first implementation.

## Published package checksums

Downloaded release assets matched the published `SHA256SUMS` on 2026-10-03:

```text
8c49a273fc5d2e8be4bc47e716955f6ef0fbee372c93e95412a97637a0506ab4  codex_instruction_lens-0.1.1-py3-none-any.whl
231c59a6e9f61e2efb60a6449c8d0cfd87c7723274670c9d505d91fe24b2be3b  codex_instruction_lens-0.1.1.tar.gz
```

The source archive includes the fixture report and reproduction helper. Version 0.1.0 remains
a source tag; no separate GitHub Release was created for it. Release publication establishes
public installation assets, not third-party usage or program eligibility.

## Feedback record format

For genuine feedback, record date, source URL or authorized summary, concrete use/problem,
reproduction, resolution PR/release, and outcome. Separate externally reported findings from
maintainer-created reproduction cases. Track negative or absent demand as well as successes.

## Application fact boundary

The project is new. It has no established adoption, broad usage or external contributor history
to claim. Future application text must retain that fact unless new evidence changes it.
Keep private identity fields out of this file and public application drafts.
