---
name: rule-pack
description: >-
  Writes or extends Heimdall Guardian's own Opengrep rules for a stack
  (rules/heimdall/<stack>/<ID>.yaml), with bilingual metadata, positive and negative
  fixtures, exact expected counts and false-positive measurement. Use when asked to add,
  change, tune or review a SAST/config rule, a rule pack for a language or framework, or
  when a rule test in tests/rules fails.
---

# Writing Heimdall rules

Own rules are Opengrep (Semgrep format) YAML files, **one rule per file**, named after the
rule ID. They are the core of the project's value; a noisy rule costs more than it brings.

## When to use

- Adding a rule or a whole pack for a stack (`rules/heimdall/<stack>/`).
- Changing a rule's pattern, severity, texts or fixtures.
- A test in `tests/rules/` fails, or a rule produces false positives on real code.

Optional help: the external skills `semgrep-rule-creator` and `semgrep-rule-variant-creator`
from trailofbits/skills (CC-BY-SA-4.0) can draft patterns. They are not copied into this
repo, and **this repo's conventions below prevail** over anything they suggest (ID scheme,
bilingual metadata, fixtures layout, English severity codes).

## Steps

1. **Pick the ID.** `<PREFIX>-<TAG>-<NNN>`, e.g. `DJ-SQL-001`, `NODE-JWT-002`, `KT-STO-001`.
   Existing prefixes: `DJ`, `NET`, `PHP`, `NODE`, `DART`, `SWIFT`, `KT`. The **second segment**
   decides category and module (`classify` in `src/heimdall_guardian/adapters/opengrep.py`,
   table `_CATEGORY_BY_TAG`): `CONF` -> configuration / module CONF; `AUTH` and `IDOR` -> access
   control / module AUTHZ; anything else -> SAST / module SAST. Do not invent a tag that
   collides with those three unless you mean it.
2. **Create `rules/heimdall/<stack>/<ID>.yaml`** (a new stack folder is picked up
   automatically: the loader does `rglob`). The file name must equal the `id`
   (`tests/rules/test_rules.py` checks it). Copy a neighbour, e.g.
   `rules/heimdall/django/DJ-SQL-001.yaml` (pattern rule),
   `rules/heimdall/dart/DART-CONF-001.yaml` (regex with `paths`), or a `mode: taint` rule such
   as `rules/heimdall/php/PHP-SQL-001.yaml`.
3. **Fill the metadata.** Current state of the repo (enforced by `test_rule_has_complete_metadata`
   and `test_rule_has_spanish_texts`):
   - `cwe: "CWE-89"`; `owasp:` with a **2025** label from `core/owasp.py` (`CATEGORIES`),
     e.g. `"A05:2025 Injection"`, `"A02:2025 Security Misconfiguration"`. `A..:2021` labels
     are rejected (`test_nothing_in_src_or_rules_keeps_2021`).
   - `severity_hdl`: `critical | high | medium | low | info` and
     `confidence: high | medium | low` (the neutral stored codes). Use confidence `low`
     for heuristics.
   - Six texts: English is the base (`message` of the rule, `metadata.title`,
     `metadata.recommendation`) and Spanish goes in `message_es`, `title_es`,
     `recommendation_es`. Spanish uses "tú"/plain verbs; English is direct and second
     person. Missing Spanish falls back to English and is treated as a gap.
   - `severity:` (engine level: `ERROR`/`WARNING`/`INFO`) is separate from `severity_hdl`.
4. **Write the fixtures** in `tests/rules/fixtures/<ID>/positive/` and `.../negative/`
   (never next to the rule: the engine would read stray YAML as rules). The positive
   fixture holds each vulnerable shape; the negative one must hold **similar legitimate
   code** (parameterized query, constant URL, safe config), not just empty files. Fixture
   code is deliberately vulnerable and never run; secrets must be fake and must not have
   a valid token format.
5. **Record the exact count** in `tests/rules/expected.yaml` (`<ID>: N`, sorted by ID).
   `test_no_orphan_fixtures` requires the file's keys to equal the set of rules.
6. **CWE guide.** If the CWE is not in `_HINTED` in `src/heimdall_guardian/core/owasp.py`, add
   it there **and** add the catalog key `owasp.hint.CWE-NNN` to both
   `i18n/messages_en.py` and `i18n/messages_es.py`.
   `test_rules_use_2025_labels_and_every_cwe_has_a_hint` (tests/unit/test_owasp.py) fails
   otherwise.
7. **Coverage.** If this is the first rule pack for a stack, set `code_rules=True` in
   `src/heimdall_guardian/core/coverage.py` (`COVERAGE`) and update the README
   "Supported stacks" table and `README.es.md`. See the `stack-support` skill.
8. **Run the real engine:**
   ```bash
   HDL_REQUIRE_RULE_ENGINE=1 uv run pytest tests/rules -q
   HDL_REQUIRE_RULE_ENGINE=1 uv run pytest tests/unit/test_owasp.py -q
   ```
   Without the engine those tests are skipped locally but **fail in CI**. The engine is
   found via `HDL_OPENGREP_BIN`, then `tools/bin/opengrep` (`make tools`), then PATH; Semgrep
   on PATH is an accepted substitute. The adapter runs with `--jobs 1`: in parallel,
   `mode: taint` rules lose findings non-deterministically. Do not remove it without
   re-measuring.
9. **Measure false positives on real, healthy code**, read-only (never write inside the
   analyzed folder; analyze a copy or use the CLI, which keeps results in the data dir):
   ```bash
   HDL_DATA_DIR=$(mktemp -d) uv run hdl scan /path/to/real/project --profile standard \
     --output /tmp/out.json
   ```
   Inspect every hit of your rule. Each false positive becomes a negative-fixture case or
   a narrower pattern. Report the numbers (hits, true, false) in the PR/commit message.
10. **Check overlaps** with other rules: `grep -rn` the same sink across
    `rules/heimdall/**`. Where a rule would duplicate another, exclude the case in one
    (see the comments in `rules/heimdall/swift/SWIFT-CONF-001.yaml`, which leaves
    `NSAllowsArbitraryLoads` to `DART-CONF-001`). `test_rule_detects_positive_fixture` counts
    only the rule that owns the fixture, so overlaps do not fail tests: you must look.
11. **Version and changelog** for a delivered change: see the `release` skill.

## Known engine limits (design around them)

- **String interpolation** in patterns is unreliable for template/f-strings in some
  languages: test each form (`f"..."`, `%`, `.format`, `+`) as separate patterns, as
  `DJ-SQL-001` does.
- **`"http://..."` literals**: URL-looking strings are matched poorly by AST patterns. Use
  `languages: [regex]` with `pattern-regex` and exclude safe hosts in the regex itself
  (see `rules/heimdall/kotlin/KT-NET-001.yaml`).
- **Capitalized constructors** (`Foo(...)` in Kotlin/Swift/Dart/C#) can be parsed as types
  or calls depending on the grammar; verify with the fixture rather than assuming.
- **TypeScript type annotations** can break a JS pattern: write patterns that tolerate
  `: Type` or add a TS variant (`languages: [typescript]`).
- **Manifests and config files** (`AndroidManifest.xml`, `Info.plist`, `build.gradle`) have
  no grammar: use `languages: [regex]` and restrict with
  `paths: include:` (and `exclude:` for debug/test variants), as in `DART-CONF-001`.
- **Taint** (`mode: taint`) is the right tool for source-to-sink flows but is where
  `--jobs` matters; give it a positive fixture with at least two flows.
- Tests, `build/`, `dist/` are excluded from SAST by default; the rule test copies fixtures
  to a temp folder so the path does not contain `tests/`.

## Quality bar

- Prefer fewer false positives over coverage. Narrow patterns beat broad ones.
- Heuristic or context-dependent rules get `confidence: BAJA` (or MEDIA) and a severity to
  match; severity `CRÍTICA` needs a clear, directly exploitable pattern.
- The recommendation must say what to do instead, with a short example when useful.
- Never reference third-party products by name in user-facing text beyond the technology the
  rule is about.

## Checklist before finishing

- [ ] ID follows `<PREFIX>-<TAG>-<NNN>`; file name equals `id`.
- [ ] All metadata present, OWASP 2025 label, severity/confidence in English codes.
- [ ] Six texts (es and en) written.
- [ ] Positive and negative fixtures exist; negative has similar legitimate code.
- [ ] `tests/rules/expected.yaml` updated with the exact count.
- [ ] CWE has a guide in `_HINTED` and in both catalogs.
- [ ] `core/coverage.py` and README tables updated if the stack gained its first rules.
- [ ] `HDL_REQUIRE_RULE_ENGINE=1 uv run pytest tests/rules -q` is green.
- [ ] False positives measured on real healthy code; overlaps checked.
- [ ] Version bumped and changelog entry added (`release` skill); `pre-commit run --all-files`
      is green.

## Common pitfalls

- Putting the fixtures next to the rule: the engine reads their YAML as rules.
- Forgetting `expected.yaml`, or leaving a fixture without its rule (orphan check).
- Missing Spanish fields: the rule silently falls back to English (a gap).
- Using a 2021 OWASP label, or a CWE without a guide.
- Removing `--jobs 1` or testing taint rules only once: results vary under parallelism.
- Counting on the engine locally while it is not installed: the tests skip and CI fails.
- Adding a rule that the endpoint inventory already supersedes (`SUPERSEDED_RULES` in
  `core/runner.py`): where `authz` evaluated a handler, the overlapping rule is dropped.
- Real-looking tokens in fixtures: secret scanners and push protection flag them; use
  clearly fake values or generate them at test time.
