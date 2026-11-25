# Reviewing findings

## Finding detail

Open a finding and, under **For experts**, you will see the rule, the tool, the CWE and
OWASP category, the confidence, the exact location (`file:line`) and, when available,
**How to verify it** without running the foreign code. The same guidance appears on each
finding of the HTML report and in the [Rules catalog](rules/index.md).

## Accept a risk or mark a false positive

```bash
uv run hdl suppress <folder> HDL-2026-000012 --status accepted \
  --reason "Internal system, not exposed" --review 2027-01-31
```

- `--status` is `accepted` or `false_positive`.
- The justification is mandatory. When the review date passes, the finding counts again.
- The change shows up immediately in the latest analysis and its reports.
- `hdl suppressions <folder>` lists them and `hdl unsuppress <folder> <id>` removes one.

## Where to start

**Where to start** (in the app and in every report) groups the open findings by common
cause, worst first: one line per vulnerable package with the version that fixes all of its
findings, and one line per rule with how many findings and files it covers. AI suggestions
are not included.

## Folders to skip

By default dependency and output folders are skipped: `node_modules`, `venv`, `.venv`,
`vendor`, `bin`, `obj`, `dist`, `build`, `static/CACHE` and `migrations`.

- In the app: **Folders to skip**, remembered per project.
- On the command line: `--exclude generated` or `--include build`.
- For every project: `exclude_extra` and `include_extra` in [`config.toml`](configuration.md).

Files can be skipped by pattern too: any entry with `*`, `?` or `[` is a file pattern
(`--exclude '*.spec.ts'`, `docs/*.md`, or the **Files to skip** field). A pattern without
`/` matches the file name; with `/`, the whole path. Manifests and lockfiles
(`package.json`, `package-lock.json`...) are always analyzed, and secrets are searched in
every file.

Heimdall also *suggests* folders from the detected stack (`.next` and `coverage` in Node,
`Pods` and `DerivedData` in Swift, `.dart_tool` in Flutter...) and editor or AI-assistant
folders (`.context`, `.agents`, `.claude`, `.cursor`, `.idea`, `.vscode`). They appear at
the top of **Folders to skip** and in `--dry-run`; nothing is skipped until you save. When
receiving vendor code, the editor and assistant folders start unchecked, because code can
hide there. Folders listed in the project's `.gitignore` are suggested too, but
only as suggestions: what the analyzed code says never configures the analysis.

If the folder holds several separate projects (for example `api/`, `ios/` and
`backend/`, each with its own manifest and none at the root), the app lists them under the
folder name: analyze it all together, or click one to analyze it on its own. `--dry-run`
lists them as well.

Reports list what was not analyzed (omitted folders and files). Findings from earlier
runs that sit in a place you now skip are counted as *omitted*: they keep their status and
are never reported as fixed.

`hdl scan <folder> --dry-run` and **Preview** show which files are included.

## Baseline

Heimdall keeps a baseline per project: between one analysis and the next, each finding is
`new`, `persistent` or `fixed`. The fingerprint ignores the line number, so moving code does
not create new findings. Share a baseline with another person or team:

```bash
uv run hdl baseline <folder> --export .heimdall-baseline.json
uv run hdl baseline <other-folder> --import .heimdall-baseline.json
```

## SARIF in your editor

```bash
uv run hdl scan <folder> --output result.sarif
```

Editors and GitHub show SARIF results on the line of code.
