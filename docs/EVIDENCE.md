# Evidence ledger

Updated: 2026-10-03 (Asia/Shanghai). Record verifiable facts with links and dates.
Do not count author tests as external adoption or this plan as completed maintenance.

| Category | Verified state | Evidence |
| --- | --- | --- |
| GitHub control | Authenticated account owns `Cerallin9029/One`; push and admin permissions reported | GitHub connector profile and repository metadata read on 2026-10-02 |
| Starting state | Private repository, only initialization README | Base commit `cc99226ead7cfff7f52133d21323ee829824f00d` |
| Technical reference | Official Codex source and settings schema inspected | [Pinned source](https://github.com/openai/codex/blob/4cedd0caac89f9fdcb5ad385e8093da5363d91c2/codex-rs/core/src/agents_md.rs) |
| First implementation | Source version 0.1.0 integrated into main | [Merged PR #1](https://github.com/Cerallin9029/One/pull/1), merge commit `50a0482aca87a095bcece29a5c0182ffe435fe48` |
| Local validation | 20 regression tests passed on Linux / Python 3.12; lint and formatting passed; source and wheel built | `python -m unittest discover -s tests -v`, `python -m ruff check .`, `python -m ruff format --check .`, `python -m build` |
| Remote CI | All four jobs passed: Linux Python 3.11/3.13, macOS Python 3.12, Windows Python 3.12 | [CI run for PR #1](https://github.com/Cerallin9029/One/actions/runs/37030452457) at source commit `cd6a17f3eb5ec2cc15ec4f4850e9ce37cf13d399` |
| Public project | Repository is public, verified on 2026-10-03 | [Repository](https://github.com/Cerallin9029/One), GitHub API returned `private: false`, `visibility: public` |
| Tagged source installation | `v0.1.0` installed from GitHub into a fresh virtual environment; CLI returned `0.1.0` on 2026-10-03 | `python -m pip install git+https://github.com/Cerallin9029/One.git@v0.1.0`, `codex-instruction-lens --version` |
| GitHub Release | None | Do not equate package version with a published release |
| PyPI | Not published | No download statistics |
| External users/feedback | None observed or claimed | Add genuine attributable evidence when available |
| Application | Not submitted | Official live form and terms still require direct verification |

Next publication/official-verification work: [maintainer planning issue #2](https://github.com/Cerallin9029/One/issues/2).
On 2026-10-03 the maintainer requested manual, irregular continuation. The previously created
scheduled task was disabled. Future project work starts when the maintainer requests it;
the 12-week roadmap is a reference for stages, not an automatic execution schedule.

Implementation and initial tests were built with Codex at the maintainer's request.
The maintainer has not yet independently reviewed the first implementation.

## Feedback record format

For genuine feedback, record date, source URL or authorized summary, concrete use/problem,
reproduction, resolution PR/release, and outcome. Separate externally reported findings from
maintainer-created reproduction cases. Track negative or absent demand as well as successes.

## Application fact boundary

The project is new. It has no established adoption, broad usage or external contributor history
to claim. Future application text must retain that fact unless new evidence changes it.
Keep private identity fields out of this file and public application drafts.
