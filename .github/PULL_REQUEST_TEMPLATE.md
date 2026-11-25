## What changes and why

<!-- Short description. Link the issue if there is one. -->

## Checklist

- [ ] `pre-commit run --all-files` is green (global pre-commit install, not `uv run pre-commit`).
- [ ] Tests added or updated. For rules: fixtures in `tests/rules/fixtures/<ID>/{positive,negative}/`, the count in `tests/rules/expected.yaml`, and `HDL_REQUIRE_RULE_ENGINE=1 uv run pytest tests/rules -q` passes.
- [ ] Visible text is in both languages (`messages_en.py` and `messages_es.py`; rules carry `*_es` fields).
- [ ] Public docs updated in both languages (`X.md` and `X.es.md`); `make docs` passes if you touched the docs or the rules.
- [ ] `CHANGELOG.md` entry in English, and the version bumped in `pyproject.toml` and `src/heimdall_guardian/__init__.py` (if the change ships).
- [ ] The principles still hold: read-only, the analyzed code is never run, no code leaves the local network, works offline.
- [ ] I added myself to `CONTRIBUTORS.md` and `CONTRIBUTORS.es.md` (optional but welcome).
