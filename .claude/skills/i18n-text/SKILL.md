---
name: i18n-text
description: >-
  Adds or changes user-visible text in Heimdall Guardian following its bilingual (English
  base, Spanish translation) catalog rules: stable keys in messages_en.py and
  messages_es.py, t()/tn()/label()/render()/msg(), stored messages as {code, params},
  bilingual rule metadata and AI prompts. Use when writing UI strings, CLI help, report
  text, limitations, finding texts, error messages or AI prompts, or when a test_i18n* /
  test_cli_i18n test fails.
---

# Visible text and i18n

English is the base language; Spanish (es-MX) is its translation. **No visible string is
written inline in code**, and no translated text is ever persisted.

## When to use

- Any new or changed text shown to a user: interface, reports (HTML/PDF/Excel/SARIF), CLI
  help and output, errors, limitations, verdict criteria, finding titles/recommendations,
  AI prompts and summaries.
- A test named `test_i18n*`, `test_cli_i18n` or the "no Spanish literals" tests fails.

## The pieces (`src/heimdall_guardian/i18n/`)

- `messages_en.py` (source) and `messages_es.py` (translation): `MESSAGES` dicts with stable
  dotted keys (`ui.welcome.title`, `core.coverage.note`, `owasp.hint.CWE-89`). Same keys,
  same `{placeholders}` in both.
- `t(key, lang=None, **params)`: text now, in the current language (falls back to English,
  then to the key). `tn(key, count, ...)` for plurals: define `key.one` and `key.other`;
  `{count}` is available.
- `label(value, kind, lang, variant=...)` (`i18n/catalog.py`): visible label of a stored code
  (severity, status, category, origin, confidence, verdict). Enum values are neutral ASCII
  codes (`critical`, `new`, `accepted`, `likely_real`); their labels are in the catalog.
- `msg(code, **params)` creates a stored structured message `{"code": ..., "params": {...}}`
  (a `Message` dict); `render(item, lang=None)` turns it (or plain tool text) into text in
  the current language. Params are data only, never already-translated strings.
  `texts_of(...)` and `text_of(item, field, lang)` handle per-language finding texts.
- Language resolution: `--lang`/`HDL_LANG`, then `config.toml`, then the system language
  (macOS preferred language), then Spanish. `set_language`, `set_override`.

## Steps

1. **Add the key** to `messages_en.py` with the English text, and the Spanish text to
   `messages_es.py`, same placeholders. Group keys by prefix (`ui.`, `cli.`, `core.`,
   `report.`, `authz.`, `owasp.`...). Never reuse a key for different text; never rename a
   key that is stored in data.
2. **Use it:** `t("...")` when displayed immediately. For anything **saved** (limitations,
   adapter details, verdict criteria, errors that end up in a run), store
   `msg("code", param=value)` and call `render()` at display time, so a regenerated report
   or a language switch uses the current language.
3. **Never freeze text at import.** No module-level strings or constants holding visible
   text (`test_owasp_and_coverage_have_no_visible_constants_frozen_at_import`); use
   functions that call `t()` when asked.
4. **Spanish style:** second person ("tú"), plain verbs, no sustained capitals; a button
   says what it does; no text names a dependency. English is direct, second person.
   Stored codes (`critical`, `high` in rule metadata) are declarations, not display text.
5. **Rules:** each rule carries English `message`, `title`, `recommendation` and
   Spanish `message_es`, `title_es`, `recommendation_es` (see `rule-pack`).
   Findings from the endpoint inventory, tool adapters and AI go through `texts_of`/`msg`,
   so both languages are stored; `text_of` picks the current one. The fingerprint must not
   depend on the language.
6. **AI prompts** (`src/heimdall_guardian/llm/prompts.py`): one table per language, `_EN` and
   `_ES`, collected in `_TEXTS`. Both keep the injection guard, the fence marks and the
   JSON schema; the model's answer codes are neutral English (`likely_real`,
   `likely_false`, `uncertain`; `high`/`medium`/`low`/`none`). The AI cache key includes
   the language. Spanish is only allowed inside its own table.
7. **Legal text** `palette.ART_NOTICE` stays verbatim in Spanish (allow-listed).
8. **Tests to run** (fast loop, then the whole suite):
   ```bash
   uv run pytest tests/unit -q -k i18n
   uv run pytest tests/unit/test_cli_i18n.py -q
   ```
   What they guard:
   - `tests/unit/test_i18n.py`: enum values are neutral codes, every value has a label in
     every language, both catalogs share keys, fallback to English, old-schema DB archived.
   - `tests/unit/test_i18n_messages.py`: same keys and placeholders in both catalogs
     (`test_catalogs_have_same_keys_and_placeholders`), every key used in code exists
     (`test_every_key_used_in_the_code_exists`, `test_message_keys_built_at_runtime_exist`),
     plural pairs, language priority, config validation, and the no-Spanish-literals tests
     for `ui/` and for core/report/storage/adapters/authz/cli/llm modules
     (`_ALLOWED_LITERALS` lists justified exceptions; `test_every_allowed_literal_still_exists`).
   - `tests/unit/test_i18n_core.py`: stored messages are `{code, params}`, reports in both
     languages from the same payload, regenerated reports use the current language, no
     frozen constants.
   - `tests/unit/test_i18n_findings.py`: rules, adapters, authz and AI texts in both
     languages, fingerprints independent of language, prompts and per-language AI cache.
   - `tests/unit/test_cli_i18n.py`: help and output in the chosen language, English names
     with Spanish aliases.
9. **Verify visually** in the web UI (isolated data, never your real history):
   ```bash
   HDL_DATA_DIR=$(mktemp -d) uv run python -m heimdall_guardian.ui --web --port 8551 --lang en
   ```
   `.claude/launch.json` serves it on 8551; `HDL_UI_FOLDER=<folder>` opens a folder on start.
   Open it, switch language in **Settings -> Language / Idioma** and confirm the text changes
   live without losing the open folder or result. Check both languages, long strings and
   the report preview.
10. Document and ship: `release` skill (changelog in English).

## Checklist before finishing

- [ ] Keys exist in both `messages_en.py` and `messages_es.py` with identical placeholders.
- [ ] No visible literal in code, templates or prompts outside the catalog tables.
- [ ] Saved text uses `msg(...)`; display uses `render(...)`/`t(...)`; labels use `label(...)`.
- [ ] Nothing visible is computed at import time.
- [ ] Rules and findings carry both languages; fingerprints unaffected.
- [ ] `uv run pytest tests/unit -q -k i18n` and `tests/unit/test_cli_i18n.py` are green.
- [ ] Checked in the UI in both languages.
- [ ] Public docs updated in English and `*.es.md`.

## Common pitfalls

- Storing the translated sentence in the database/JSON: it then reads in the wrong language
  after a switch or a `hdl report` regeneration. Store `{code, params}`.
- Passing already-translated text as a `msg` param: wrong when rendered in another language.
- Adding a key in only one catalog, or with different `{placeholders}`.
- Building keys at runtime without a test that proves they exist
  (`test_message_keys_built_at_runtime_exist`).
- Module-level constants with visible text (frozen at import).
- Translating the stored codes (`CRÍTICA`, `NUEVO`, `likely_real`) or the config keys (they
  are English and stable).
- Letting the language leak into the fingerprint, which makes a switch create "new" findings.
- Rebuilding the whole left panel on a language change in the UI: causes flicker; follow the
  existing refresh helpers (see CLAUDE.md "No flicker").
- Writing "partial" i18n: either both languages or neither.
