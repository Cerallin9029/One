# Evidence ledger

Updated: 2026-10-02 (Asia/Shanghai). Record verifiable facts with links and dates.
Do not count author tests as external adoption or this plan as completed maintenance.

| Category | Verified state | Evidence |
| --- | --- | --- |
| GitHub control | Authenticated account owns `Cerallin9029/One`; push and admin permissions reported | GitHub connector profile and repository metadata read on 2026-10-02 |
| Starting state | Private repository, only initialization README | Base commit `cc99226ead7cfff7f52133d21323ee829824f00d` |
| Technical reference | Official Codex source and settings schema inspected | [Pinned source](https://github.com/openai/codex/blob/4cedd0caac89f9fdcb5ad385e8093da5363d91c2/codex-rs/core/src/agents_md.rs) |
| First implementation | Local source version 0.1.0 prepared | `src/instruction_lens/`, README, synthetic examples |
| Local validation | 20 regression tests passed on Linux / Python 3.12; lint and formatting passed; source and wheel built | `python -m unittest discover -s tests -v`, `python -m ruff check .`, `python -m ruff format --check .`, `python -m build` |
| Remote CI | Not verified yet | Add run URLs after completion |
| Public project | Not yet: repository is private | Verify visibility before claiming public OSS |
| GitHub Release | None | Do not equate package version with a published release |
| PyPI | Not published | No download statistics |
| External users/feedback | None observed or claimed | Add genuine attributable evidence when available |
| Application | Not submitted | Official live form and terms still require direct verification |

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
