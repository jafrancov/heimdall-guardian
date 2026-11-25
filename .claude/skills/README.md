# Project skills

Claude Code skills for contributing to Heimdall Guardian. Each lives in
`<name>/SKILL.md` and is loaded on demand when its description matches the task.

| Skill | Use it to |
|---|---|
| `rule-pack` | Write or extend the project's own Opengrep rules: metadata, fixtures, expected counts, engine tests, false-positive measurement. |
| `stack-support` | Add a language/ecosystem: detector, OSV probe file, coverage, README tables, optional endpoint extractor. |
| `release` | Close a version: SemVer bump, English changelog, `uv lock`, QA, commit, macOS app and DMG check. |
| `i18n-text` | Add or change visible text: catalogs, `t()`/`msg()`/`render()`, stored messages, bilingual rules and prompts. |

Optional external helpers (not vendored; CC-BY-SA-4.0, trailofbits/skills):
`semgrep-rule-creator` and `semgrep-rule-variant-creator`. The conventions in `rule-pack`
prevail over them.

The authoritative references remain `CLAUDE.md` and `CONTRIBUTING.md`.
