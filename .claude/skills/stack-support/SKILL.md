---
name: stack-support
description: >-
  Adds support for a new language, framework or package ecosystem to Heimdall Guardian:
  stack detection, OSV database probe file, coverage table, README tables, and optionally
  an endpoint-inventory extractor with fixtures. Use when asked to "support
  Java/Go/Ruby/Rust/another stack", to detect a new manifest or lock file, or to add a
  web-framework extractor under authz/.
---

# Adding a stack

A stack is detected from file names and manifests only; **nothing is ever executed or
installed** (principle P2). Secrets, dependencies and configuration already apply to any
stack; what a new stack adds is detection, database coverage, and optionally rules and an
endpoint inventory.

## When to use

- A language/ecosystem is missing from `Stack` in `src/heimdall_guardian/core/detector.py`.
- A new lock file/manifest needs to be recognised or its vulnerability database fetched.
- A web framework needs an endpoint inventory (AUTHZ-001/AUTHZ-002).

## Steps

1. **Detector** (`core/detector.py`): add the member to `Stack` (enum order is the report
   order), then add the evidence rule: file name/suffix in `_more_stacks` for simple cases
   or in `detect()` when a manifest's content matters (use `_read`, which caps reads at
   256 KB). Evidence is the first file that reveals the stack. Do not detect from
   declaration-only or generated files if they cause false stacks (see TypeScript `.d.ts`
   handling). Add cases to `tests/unit/test_stack_coverage.py::test_detect_new_stacks`
   (parametrized `files -> Stack`) plus a negative case when ambiguity exists (e.g.
   `test_dart_without_flutter_is_not_flutter`).
2. **Coverage** (`core/coverage.py`): add a `StackCoverage(name, code_rules=..., endpoints=...)`
   entry to `COVERAGE`. `code_rules=False` makes the report state that only secrets,
   dependencies and configuration are reviewed. If the stack is nested in another (like
   Dart in Flutter), add it to `_COVERED_BY` so notes are not repeated.
   `test_every_language_stack_has_a_coverage_entry` enforces an entry per language stack.
3. **Vulnerability database probe** (`storage/bases.py`, `_PROBE_FILES`): add a minimal
   manifest/lock file with a known-vulnerable dependency, so `hdl databases --update` (and the
   "update databases" button) downloads that ecosystem's OSV database.
   - Verify with the **real** osv-scanner (`tools/bin/osv-scanner`, from `make tools`) on a
     temp folder containing only that file:
     ```bash
     d=$(mktemp -d); printf '%s' '<content>' > "$d/<file>"; c=$(mktemp -d)
     OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY=$c tools/bin/osv-scanner scan source --recursive \
       --format json --no-resolve --no-call-analysis=all --offline-vulnerabilities \
       --download-offline-databases "$d" > out.json
     ```
     (These are the flags `update_bases` uses; the database download needs internet and
     goes to the temp cache, not your data dir.) It must parse the file and find at least one vulnerability (exit 1
     means it found some, which is expected; the update step accepts `_OSV_OK = (0, 1)`).
   - Add the file to the shape check in
     `tests/unit/test_stack_coverage.py::test_probe_files_are_well_formed` (JSON/TOML/YAML
     parse or a content assertion).
   - If the ecosystem name is new, check `adapters/osv.py` (`_ECOSYSTEM_DB`) still extracts
     it from the "could not load db for X ecosystem" error.
4. **Docs**: add the row to the "Supported stacks" table in `README.md` **and**
   `README.es.md` (Secrets / Dependencies with the lock file / Configuration / Code rules /
   Endpoints). If the lock file is read only by Trivy and not OSV, say so (as for
   `Podfile.lock`). If a third-party tool or dependency was added, update
   `THIRD-PARTY-NOTICES.md` and `.es.md`.
5. **Rules** (optional): follow the `rule-pack` skill, then flip `code_rules=True`.
6. **Endpoint inventory** (only for server-side web frameworks; clients such as mobile
   apps have `endpoints=False`):
   - Create `src/heimdall_guardian/authz/<stack>.py` with a class exposing
     `extract() -> list[Endpoint]` and a `notes` list for what it could not read. `Endpoint`
     lives in `core/endpoints.py` (not in `adapters/`, to avoid an import cycle). Use `ast`
     (Python) or text analysis; never import or run the project.
   - Register it in `AuthzAdapter._extractors` (`authz/adapter.py`) keyed on `ctx.stacks`.
     A failing extractor is caught and reported as a limitation, not a crash.
   - Add an example project under `tests/fixtures/authz_<stack>/` (deliberately
     vulnerable, never run, fake credentials).
   - In `tests/unit/test_authz.py`, use the `inventory()` helper and compare the **full
     expected dictionary** `{(methods, path): (has_auth, writes)}`; `notes` must be empty
     and keys unique. Copy `test_node_inventory_matches_real_routes` as a model and add
     tests for prefixes, guards/middleware, and a scan that yields AUTHZ findings.
   - Texts the extractor produces go through the catalog (see `i18n-text`).
   - Set `endpoints=True` in `COVERAGE` and update the READMEs.
7. **Tests and QA**: `uv run pytest tests/unit/test_stack_coverage.py tests/unit/test_authz.py -q`,
   then `pre-commit run --all-files`. Bump the version and changelog (`release` skill; a new
   stack is a new feature, so the middle number goes up).

## Checklist before finishing

- [ ] `Stack` member, detection evidence, and tests (positive and ambiguity cases).
- [ ] `COVERAGE` (and `_COVERED_BY` if nested) updated.
- [ ] Probe file added and verified with the real osv-scanner; shape test updated.
- [ ] README.md and README.es.md "Supported stacks" rows updated.
- [ ] Extractor (if any) registered, fixture project added, full inventory compared exactly.
- [ ] Nothing in the new code runs, installs, compiles or imports the analyzed project.
- [ ] Version, `CHANGELOG.md`, `pre-commit run --all-files` green.

## Common pitfalls

- Detecting from content you did not cap or from files like `.d.ts`: false stacks, slow scans.
- Forgetting the probe file: the ecosystem's database is never downloaded and the report says
  its database is missing (the message names the ecosystem, one limitation per run).
- A probe whose dependency has no known vulnerability, so the tool never downloads the DB.
- Native folders of an app (`android/`, `ios/` in Flutter) triggering "no rules" notes for
  Android/Kotlin/Swift: handle with `_COVERED_BY`.
- Using `osv-scanner` without `--offline`-style flags in adapters: the adapter must keep
  `--offline`, `--no-resolve` and no call analysis, or it may reach the network or run build
  scripts (P2/P3). Do not copy the probe command's download flags into the scan adapter.
- Extractor inventory tests that only check counts: the dictionary must match exactly.
- Putting Endpoint in `adapters/`: causes an import cycle.
- Findings on build output (`bin/`, `obj/`, `build`, `dist`): excluded by default; a tool
  that reports them gets a limitation, not extra findings.
