---
name: release
description: >-
  Closes a Heimdall Guardian version end to end: SemVer bump in pyproject.toml and
  __init__.py, an English Keep a Changelog entry (marking breaking changes), uv lock, full
  QA with pre-commit and the real-engine test suites, an English commit message, and the
  macOS app build with read-only DMG verification. Use when finishing a change that ships,
  when asked to "bump the version", "cut a release", "update the changelog" or "build the
  DMG".
---

# Closing a version

Every change that ships bumps the version and gets a changelog entry. The version lives in
**two places** and a test enforces they match and that the version has an entry.

## When to use

- You finished a feature/fix/docs change and it must be delivered.
- You were asked to bump the version, write the changelog, run the full QA or build the
  installer.

## Steps

1. **Choose the number (SemVer, since 1.0.0).**
   - first number for **incompatible changes** (CLI flags removed or renamed, a stored-data
     or configuration change that needs action, a dropped platform);
   - middle number for **new features** (new stack, new rules, new commands, new UI);
   - last number for **fixes**, small corrections and tool/dependency bumps.
   - Releases are cut by pushing a `vX.Y.Z` tag: `release.yml` checks it matches
     `pyproject.toml` and creates a draft release (see CONTRIBUTING).
2. **Bump both files** with the same string:
   - `pyproject.toml` -> `[project] version`
   - `src/heimdall_guardian/__init__.py` -> `__version__`
   `tests/unit/test_core.py::test_version_is_the_same_everywhere_and_logged` fails if they
   differ or if `## [X.Y.Z]` is missing from `CHANGELOG.md`. The installer takes the
   number from `pyproject.toml`.
3. **Write the `CHANGELOG.md` entry, in English** (older entries stay in Spanish; do not
   translate them). Insert it above the previous one:
   ```markdown
   ## [0.16.0] - YYYY-MM-DD

   ### Added
   - ...
   ### Changed
   - **Breaking:** ... (what stops working and what the user must do)
   ### Fixed
   - ...
   ```
   Keep a Changelog sections: Added, Changed, Deprecated, Removed, Fixed, Security. Mark
   incompatibilities in bold (`**Breaking:**`; the Spanish entries use `**Incompatible:**`).
   State user impact (e.g. "project history starts over; the previous one is archived"),
   not internals. Use the real date.
4. **Lock file:** `uv lock` (the `uv-lock` hook runs `uv lock --check` and fails if
   `uv.lock` is stale). Needed whenever dependencies or the project version change.
5. **Documentation parity:** if you changed `README.md`, `CONTRIBUTING.md`, `SECURITY.md` or
   `THIRD-PARTY-NOTICES.md`, update the matching `*.es.md`. `NOTICE` carries both languages.
   If a tool/dependency changed, update `THIRD-PARTY-NOTICES.md` (+ `.es.md`) and
   `licenses/`.
6. **QA must be green:**
   ```bash
   pre-commit run --all-files                                   # the global install, NOT `uv run pre-commit`
   HDL_REQUIRE_RULE_ENGINE=1 uv run pytest tests/integration tests/rules
   ```
   The hooks (file hygiene, `uv lock --check`, ruff check + format, strict mypy, pytest with
   coverage >= 75 %) run on every commit and push; CI runs the same hooks. `pre-commit`
   only sees files in git, so `git add` new files first. Integration tests skip when a
   binary is missing locally (`make tools` installs them into `tools/bin/`).
7. **Commit** with a short Conventional-Commits message **in English**, ending with the
   attribution lines your environment asks for:
   ```
   feat: version 0.16.0, <one-line summary>
   fix: <what was broken>
   docs: <what changed>
   chore: version 0.4.1, Trivy 0.76.0 and OSV-Scanner 2.7.0
   ```
   Only commit/push when the requester asked you to.
8. **Installer (macOS), when the delivery includes it:**
   ```bash
   make app    # build/macos/ + dist/HeimdallGuardian-<version>-<arch>.dmg; needs Flutter and Xcode
   ```
   Verify the DMG without modifying it:
   ```bash
   diskutil image attach --readOnly --mountOptions nobrowse --mountPoint /tmp/hdl-dmg dist/HeimdallGuardian-<version>-*.dmg
   ls /tmp/hdl-dmg            # "Heimdall Guardian.app" and the Applications shortcut
   diskutil eject /tmp/hdl-dmg
   ```
   Only the current version's DMG should remain in `dist/`. The app is ad-hoc signed
   (no Developer ID/notarization yet), so Gatekeeper needs the documented right-click open.
   Test anything that launches a program with a minimal PATH:
   `env -i HOME=$HOME PATH=/usr/bin:/bin ...`.

## Checklist before finishing

- [ ] Version identical in `pyproject.toml` and `src/heimdall_guardian/__init__.py`.
- [ ] `CHANGELOG.md` entry in English, dated, breaking changes marked.
- [ ] `uv lock` run; `uv.lock` committed.
- [ ] README/CONTRIBUTING/SECURITY/THIRD-PARTY-NOTICES and their `.es.md` in sync.
- [ ] `pre-commit run --all-files` green (new files already `git add`-ed).
- [ ] `HDL_REQUIRE_RULE_ENGINE=1 uv run pytest tests/integration tests/rules` green.
- [ ] Commit message in English.
- [ ] If an installer was built: DMG mounted read-only, contents checked, detached.

## Common pitfalls

- Bumping only one of the two version locations, or forgetting the changelog heading
  (`## [X.Y.Z]` must match exactly).
- Running `uv run pre-commit`: it is not a project dependency; use the global `pre-commit`.
- Running pre-commit before `git add`: it never sees untracked files, so a green run can hide
  problems.
- Treating skipped tests as passing: without the rule engine or binaries they skip locally
  and then fail in CI (`HDL_REQUIRE_RULE_ENGINE`).
- `make app` failing because `build/macos` is open in Finder or has bad permissions (fixed
  in 0.7.1/0.4.1: it retries and cleans first); close Finder windows if it still complains.
- Hand-editing the Xcode project: the script patches the macOS 11 -> 12 deployment target
  for Xcode 27 itself.
- Mixing languages in the changelog: new entries are English; do not rewrite history.
- Not mentioning that old stored data is archived when the change alters the database
  schema or stored codes (`baseline.db.v1.bak`, `config.toml.v1.bak`).
