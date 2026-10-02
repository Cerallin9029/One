# Project maintenance

This is a Python 3.11+ standard-library CLI for explaining Codex project instruction discovery.
Keep runtime dependencies empty. Make behavior changes against a pinned upstream source and
update `docs/COMPATIBILITY.md`. Do not claim to reproduce host instructions or all Codex config.

Install with `python -m pip install -e .`. Validate substantive changes with
`python -m unittest discover -s tests -v`, `python -m ruff check .` and
`python -m ruff format --check .`. Use synthetic fixtures, never private user instructions.

Follow `docs/OSS_PLAN.zh-CN.md` for long-term priorities. Keep `docs/EVIDENCE.md` factual:
author tests, public releases and genuine external use are distinct. Do not create activity
solely to increase commit, issue, star or release counts. Application terms need a fresh
official read before submission; do not copy personal form fields into repository files.
