# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[SemVer](https://semver.org/). Before 1.0.0, a change in the middle number could include breaking changes.

## [1.0.0] - 2026-11-24

First public version. Heimdall Guardian analyzes source code for security problems on your
own computer, read-only and without sending code anywhere: secrets, vulnerable
dependencies (also libraries copied into the project), insecure code with its own rules
for seven stacks, configuration, access control (an endpoint inventory) and an optional
local AI review. It comes as a desktop app for macOS, Windows and Linux and as the `hdl`
command for automation, sharing databases and history between them.

From here on the version follows SemVer strictly: the middle number for new features, the
last one for fixes, the first one for incompatible changes.

### Changed
- Test fixtures no longer store provider-shaped fake secrets (Stripe, GitHub, Google):
  they carry placeholders that the rule tests fill in their temporary copy, so hosting
  services do not block a push for them.
- Package classifier: "Development Status :: 4 - Beta".

## [0.45.1] - 2026-11-23

### Fixed
- With Flet 1.1, the interface served in a browser (`hdl ui --web`) stayed on the loading
  screen in some browsers: Flet picked its WebAssembly renderer. It now uses CanvasKit.
  The desktop app is not affected.

## [0.45.0] - 2026-11-23

### Changed
- Opengrep 2.0.0 (was 1.31.0), OSV-Scanner 2.7.1 (was 2.7.0) and Trivy 0.76.2 (was
  0.76.0), pinned with their SHA-256 (OSV and Trivy from their published checksums;
  Opengrep publishes none, so the hash of the download, equal to GitHub's digest). Own
  rules give exactly the same counts; existing vulnerability databases keep working.
- Opengrep 2.0 started honouring `.semgrepignore` files of the analyzed code, which would
  let analyzed code hide findings: Heimdall turns that off
  (`--x-ignore-semgrepignore-files`).
- Rule validation with the engine (`hdl rules`, own rule files) gives up after two minutes
  with a clear message instead of waiting for a stuck process.

### Fixed
- Tools packed as an archive with libraries next to the program (Opengrep 2.0 on Windows:
  the executable plus its DLLs) are installed with those libraries (`extra` patterns in
  `tools/tools.toml`), never outside the tool's folder.

## [0.44.0] - 2026-11-23

Dependencies brought up to date, and a way to keep them there.

### Added
- `make outdated` (`tools/check_outdated.py`) lists outdated Python dependencies (project,
  extras and groups, marking major jumps), pinned tools and GitHub Actions in one report;
  `--strict` exits 1 when something is outdated.
- `make upgrade` (`tools/try_upgrade.py`, `PACKAGE=name` for one) upgrades the lock, moves
  the app's Flet pin with it, runs the full QA and the real-engine tests, and restores
  `pyproject.toml` and `uv.lock` if anything fails.
- Dependabot opens weekly pull requests for `uv` and GitHub Actions (patch and minor
  grouped, majors apart); CI tests each one.

### Changed
- Flet 1.1.3 (was 1.0.4), pillow 13, ruff 0.17, fpdf2 2.9, pydantic 2.14.4, PyYAML 6.0.4,
  mypy 2.4.1, pytest 9.2, mkdocs-material 9.8 and minor updates.
- Every GitHub Action in the workflows is pinned by commit SHA (with its version as a
  comment), so Dependabot updates them explicitly.

## [0.43.0] - 2026-11-23

Release automation for the command line, and a check for newer versions of Heimdall.

### Added
- `hdl version` prints the version; `hdl version --check` asks GitHub for the latest
  release and says whether yours is current, with the release page and, for a command
  installed with `install_hdl.py`, how to update it. "About" in the app has a "Check for
  updates" button. Nothing is checked unless you ask; without a published release or
  without network it says so calmly. `hdl tools --news` lists Heimdall too.
- `.github/workflows/release.yml`: pushing a `vX.Y.Z` tag checks that it matches the
  project version, runs the full QA, builds the command-line wheel and archive with
  `SHA256SUMS`, and creates a **draft** release with the changelog section as notes. The
  owner reviews it, attaches tested installers and publishes. Publishing to PyPI (trusted
  publishing) runs only when the repository variable `PUBLISH_PYPI` is `true`.
- `tools/changelog_section.py` prints one version's changelog section.
- CONTRIBUTING explains how to cut a release.

## [0.42.1] - 2026-11-23

### Fixed
- The app stored the command-line installer as a `.py`, which the app build compiles to
  bytecode for its own Python: the user's Python could not run it. It is now stored as
  text and copied to a temporary `.py` when used.
- The app build could take a newer Flet than the one the project is tested with (the
  build template must match it): it is pinned to the version in `uv.lock`, and a test
  checks they agree.

## [0.42.0] - 2026-11-23

The desktop app offers the `hdl` command, and servers without a desktop get a
command-only archive.

### Added
- The first time the app opens, it asks whether you also want the `hdl` command for the
  terminal (once; after the guided tour). Settings has a "Command line" section that says
  whether it is installed and where, and installs or uninstalls it. It uses your Python
  3.12 or newer; if none is found, it says so and links to python.org. The first
  installation needs internet for the command's dependencies.
- The app carries the command-line installer and wheel inside (`_bundle/cli/`), so the
  command installed from the app matches the app's version.
- `make cli-archive` writes `dist/heimdall-guardian-cli-<version>.tar.gz` (installer, wheel
  and a short README) for servers; the Linux build writes it too.

### Changed
- `make app` builds the command-line wheel before the platform build. Running the
  platform build scripts directly needs `make cli-wheel` first.

## [0.41.0] - 2026-11-23

The `hdl` command can be installed on its own, on your Python, sharing everything with the
desktop app.

### Added
- `packaging/cli/install_hdl.py`: installs `hdl` with Python 3.12 or newer (from
  python.org). It checks the version (and explains the old `python3` that comes with
  Xcode), creates its own environment in the data folder (`<data>/cli/`), links `hdl` in
  `~/.local/bin` (on Windows, a shim on the user `PATH`) and says how to add the folder to
  the `PATH` if needed. `--uninstall` removes only the command: databases, history and
  settings stay.
- `hdl tools --install` downloads the pinned tools for this computer, checks their SHA-256
  and stores them in the data folder. If the app already extracted them there, the command
  reuses them; nothing is downloaded twice.
- `make cli-wheel` (`tools/build_cli_wheel.py`) builds the light command-line wheel (rules
  and legal files, no binaries).

### Changed
- **Breaking:** the graphical interface is now the optional extra `heimdall-guardian[ui]`.
  `pip install heimdall-guardian` installs only the command line; `hdl ui` without the
  extra explains how to get it. The desktop app is not affected.

## [0.40.0] - 2026-11-23

First step towards a global `hdl` command that shares everything with the desktop app.

### Added
- Database updates take an operating-system lock in the databases folder, so the app and
  the `hdl` command (or two windows) never download into it at the same time: the second
  one waits and says so, and gives up after 30 minutes with a clear message. Analyses that
  do not update the databases are not affected.
- `hdl tools`, `hdl databases` and the tool list in Settings show the data and databases
  folders in use, and whether `HDL_DATA_DIR` or `HDL_BASES_DIR` set them. The app and the
  command share that folder: databases, history and settings are stored once.
- On a computer with a desktop, `hdl` suggests the Heimdall Guardian app once (on the
  error output, only in an interactive terminal, never over SSH, in CI or when the app is
  installed; `HDL_NO_HINTS=1` turns it off).

## [0.39.0] - 2026-11-21

Two notices that could make a dependency check look clean when it was not, found in real
use.

### Added
- When a manifest has no lockfile next to it (`package.json`, `composer.json`,
  `pyproject.toml`, `Pipfile`, `setup.py`, `Gemfile`, `Cargo.toml`, `go.mod`,
  `pubspec.yaml`, `Podfile`, `Package.swift`, or a `requirements*.txt` not generated with
  pip-compile, `uv` or hashes), the report says that only its direct dependencies were
  checked: transitive ones are not resolved offline. It suggests generating a lockfile.
- `HDL_BASES_DIR` moves only the vulnerability databases, so an isolated `HDL_DATA_DIR`
  can reuse the usual ones.

### Changed
- The missing-database notices say where the databases were looked for and, when
  `HDL_DATA_DIR` is set without `HDL_BASES_DIR`, that this is the likely reason.

## [0.38.0] - 2026-11-21

SQL injection through a model layer was not reported: a controller passes request data
to a function or method, and that function builds the SQL. Found on a legacy PHP system
in production, where a real injection in report filters went unnoticed.

### Added
- `PHP-SQL-002` (high, medium confidence): a parameter of a function or method reaches
  the SQL text of `mysqli_query`, `mysql_query`, `pg_query`, `sqlsrv_query`, `odbc_exec`
  or `->query()` / `->exec()` / `->multi_query()` without a cast or escaping, including
  through elements of an array parameter, interpolation and SQL built in several steps.
  Casts and numeric functions, the drivers' escape functions, `quote()`, and helpers whose
  name says they escape or quote (`esc`, `db_escape`, `esc_like`...) count as
  sanitizers; prepared statements are not reported. Request superglobals inside the same
  function stay with `PHP-SQL-001`.

### Known limits
- Values that pass through other project helpers, or array elements escaped one by one
  and stored back into the same array, are still reported. Thin wrappers that receive the
  finished SQL as a parameter are reported too: the risk is at their callers.

## [0.37.1] - 2026-11-21

False positives of three rules, found on a legacy PHP system in production.

### Fixed
- `PHP-INC-001`: a path from a variable assigned `dirname(realpath(__FILE__))` (any
  nesting of `dirname()` and `realpath()` around `__FILE__` or `__DIR__`) and joined with
  literals is a fixed path.
- `PHP-XSS-001`: output after a literal `Content-Type: application/json` header (also
  `application/*+json` and `text/json`) is not HTML. `json_encode` echoed without that
  header is still reported.
- `NODE-XSS-002`: a string literal containing the other quote character, concatenations
  of literals only, and variables that hold only literals (or a ternary of literals) are
  not reported. With symbolic propagation the rule now also sees jQuery objects kept in a
  variable (`box = $("#id"); box.html(value)`), so it can report places it missed before.

### Known limits
- An include inside a helper function whose path comes from its own parameter is still
  reported: the rule cannot see the callers.
- Values taken from an array filled with literals, or built from `Date` getters, are still
  reported by `NODE-XSS-002`.

## [0.37.0] - 2026-11-21

JavaScript and PHP libraries copied into a project (not installed through a package
manager) were invisible to the dependency check, and their code filled the SAST results
with findings nobody would fix there. Found while analyzing a legacy PHP system in
production.

### Added
- Copied libraries are recognised by the version header or constant they carry: jQuery,
  jQuery UI, DataTables, Highcharts, Bootstrap, Moment.js, Lodash, elFinder, PHPMailer,
  PHPExcel, FPDF, TCPDF and NuSOAP (`core/vendored.py`). Their known vulnerabilities come
  from the local OSV database, offline, through a lockfile written in the run's temporary
  directory (never in the analyzed folder); each finding points at the copied file. The
  new tool appears as "Copied libraries" (`vendored`) in the annex.
- The report lists the libraries it recognised.

### Changed
- SAST findings inside a recognised library are set aside and declared in one limitation,
  instead of being reported or counted with the skipped folders. Secrets in those files are
  still reported. In the baseline they count as omitted, not fixed.
- Excluding copied libraries is no longer needed: leave them in so they are checked by
  version.

### Known limits
- A minified build that strips its banner is not recognised, nor elFinder's PHP connector.
  Highcharts modules and Bootstrap plugin files that print the core banner repeat the core
  package's findings.

## [0.36.0] - 2026-11-20

More results from analyzing a legacy PHP system in production: two remote code execution
paths were not reported, and several rules were noisy.

### Added
- `PHP-UPL-001` (critical): an uploaded file is stored with a path built from data the
  client controls (its original name, even through `basename()`, a form field or the
  `$_FILES` key used as the folder). An extension allowlist checked before the move, a
  folder confined with `realpath` and a prefix check, or a generated name are recognised.
- `PHP-CALL-001` (critical): a function, method or class whose name comes from the request
  is called (`$name(...)`, `call_user_func`, `new $class`, `$obj->$method()`), from
  `$_GET`, `$_POST`, `$_REQUEST`, `$_COOKIE` or `filter_input`. An allowlist check
  (`in_array`, `array_key_exists`, `isset($map[...])`) is recognised; `function_exists`
  and `is_callable` are not enough.
- `PHP-CONF-002` (medium): a production or debug flag hard-coded in PHP
  (`const PRODUCTION = false`, `define('DEBUG', true)`...): whatever `php.ini` says, code
  that turns on error display from that flag does so in production.
- `hdl scan --exclude-gitignored` skips, for that run, what git ignores in the analyzed
  folder (or what the root `.gitignore` lists outside a git repository). Manifests and
  lockfiles are still analyzed.

### Fixed
- `PHP-INC-001` no longer reports includes whose path is a variable set in the same scope
  from `dirname(__FILE__)`, `__DIR__`, a constant or a literal.
- `PHP-EXE-001` no longer reports commands where every variable goes through
  `escapeshellarg()` or `escapeshellcmd()`, even when concatenated with literals.
- `NODE-DES-001` only reports a bare `unserialize()` when the file loads a serialization
  package; browser helpers with that name are not reported.
- The `.env` part of `PHP-CONF-001` (credentials in a versioned `.env`) only applies when
  git tracks the file; findings on untracked files are left out and declared. Rules can
  declare this with `versioned_only` in their metadata.
- `--exclude path/to/file.js` (an existing file, no wildcard) now excludes that file; it
  was read as a folder name. As with file patterns, manifests are kept and secrets are
  still searched.
- The limitation about files left out by file patterns said "e.g. e.g.".

## [0.35.0] - 2026-11-20

### Changed
- The plain-PHP inventory reads `.htaccess` per file, not only per folder, from the
  analyzed root down to the file's folder (inner folders override outer ones, and the last
  applicable directive wins). It understands `<Files>`, `<Files ~>` and `<FilesMatch>`
  blocks, including allowlists that close a folder except a few named files,
  `Require all granted` / `Allow from all` overrides, and Apache 2.2 and 2.4 syntax inside
  `<IfModule>`. A file is not listed when access to it is denied or when PHP does not run
  in its folder (`php_flag engine off`, `RemoveHandler .php`, `RemoveType .php`,
  `SetHandler none`). Rewrite rules and server-level configuration are not evaluated.

## [0.34.0] - 2026-11-20

Findings from analyzing a legacy PHP system in production showed that the plain-PHP
endpoint inventory missed unauthenticated AJAX and upload handlers and reported files that
only define classes.

### Changed
- **Breaking (results):** the plain-PHP inventory decides from each file's top-level code,
  not from its folder name. A file is an endpoint when, outside class and function bodies,
  it reads request input (`$_GET`, `$_POST`, `$_FILES`...), produces output or has inline
  HTML, or when it does work on load (method calls, calls to functions that are not
  configuration). Handlers inside `lib/`, `includes/`, `config/` and similar folders are
  now listed; files that only define classes, functions or constants are not, even if a
  method echoes or the file ends with `?>`.
- Scheduled or maintenance scripts placed in the web root (they run code on load with no
  session check) are listed with their own evidence, and writing files (`fopen` for
  writing, `file_put_contents`, `move_uploaded_file`, `mkdir`, `unlink`, `->save(`...)
  counts as a write, so they become AUTHZ-001.
- A file is not listed when it only runs from the command line (`php_sapi_name()` or
  `PHP_SAPI` compared with `'cli'`, `defined('STDIN')`) or when an `.htaccess` in its
  folder or a parent denies the whole folder (`Require all denied`, `Deny from all` outside
  a `<Files>` block).
- An include protects a file only if the included file, resolved inside the analyzed tree,
  checks the session; the name of the file is used only when it cannot be resolved, and
  only whole words (`auth`, `login`, `session`, `guard`...). Before, any include whose
  name contained "verifica" counted as an access check.
- HTTP basic authentication (`$_SERVER['PHP_AUTH_USER']`, `HTTP_AUTHORIZATION`) counts as
  an access check, with its own evidence text.

## [0.33.0] - 2026-11-04

### Added
- AI sink review (T4) covers two more kinds of risky operation: unsafe deserialization
  (`AI-DESER-001`) and XML parsing that may resolve external entities (`AI-XXE-001`), with
  new candidate rules for PHP, Node, Django and .NET (`*-CAND-006`, `*-CAND-007`).
- T4 now reviews Kotlin, Swift and Dart code: candidate rules `KT-CAND-001..004`,
  `SWIFT-CAND-001..003` and `DART-CAND-001..004` (SQL, commands, file paths, outbound URLs
  and WebView loads), and the AI context finds functions and callers in those languages.
  The sink prompt names mobile sources of untrusted input (intent extras, deep links, data
  from other apps, WebView messages).

### Fixed
- Two identical risky lines in one file (the same `rawQuery(sql, null)` in two functions)
  were merged into one candidate, so the second was never reviewed. Candidates are now
  kept per line.

### Changed
- **Breaking (stored data):** the fingerprint of an AI sink finding includes its
  enclosing function, so two of them on identical lines are told apart. Sink findings
  from 0.31 and 0.32 appear once as new.
- AI prompts version 7: cached answers from earlier versions are not reused.

## [0.32.0] - 2026-11-04

### Changed
- AI endpoint review (T2) now sees the code that decides access: the real handler (for
  Laravel, Node and .NET it is found from the route, for example `UserController@show` in
  its controller), the route declaration with its group middleware, and up to three
  project functions the handler calls (a repository query, a policy). Everything is sent
  without comments, with secrets masked and within the destination's line budget.
- An AI IDOR or flow suggestion is only created when the handler's code was found and the
  review does not say ownership is checked; the prompt now asks for "low" when the code
  that would decide is not shown. Reviews are still stored on every endpoint, with the
  handler file and line they read.
- AI prompts version 6: cached endpoint answers from earlier versions are not reused.

## [0.31.0] - 2026-11-04

### Added
- AI sink review (T4): 20 new candidate rules (`PHP-CAND`, `NODE-CAND`, `DJ-CAND`,
  `NET-CAND`) mark risky operations (SQL built from data, OS commands, file paths,
  outbound URLs, redirects) with a broad pattern. They are never reported on their own:
  the local AI receives the function that contains each one, without comments and with
  secrets masked, plus up to two callers, and decides whether user input reaches it
  unprotected. Only a high risk that is reachable becomes an AI finding (`AI-SQL-001`,
  `AI-EXEC-001`, `AI-PATH-001`, `AI-SSRF-001`, `AI-REDIR-001`), at most MEDIUM and outside
  the verdict until a person confirms it. Candidates next to an already reported finding
  are skipped.
- Optional `model_sinks` per AI destination; it falls back to `model_triage`.
- The result says how many risk points the AI reviewed and how many possible problems it
  found beyond the rules; the HTML and PDF reports show whether the input is reachable and
  which input reaches it.

### Changed
- **Breaking (AI behavior):** the per-run AI budget is spent in a new order: sink review
  first (up to 60 %), then endpoints, then triage. Triage no longer reviews findings whose
  rule already has high confidence. A run takes the same number of AI queries as before.
- AI prompts version 5: the triage prompt now defines `likely_real`, `likely_false` and
  `uncertain`, and the sink prompt defines "reachable"; cached AI answers from earlier
  versions are not reused.
- AI destinations have a `reasoning` option (`"off"` by default, `"on"` to let reasoning
  models think first; checkbox in Settings). With `"off"` the request carries
  `reasoning_effort: "none"` so "thinking" models answer directly instead of spending the
  token limit on hidden reasoning; a runtime that rejects the field is not asked again.
  With `"on"` the reply limit is at least 4096 tokens.
- The result counts replies cut off for length, and when fewer than half of at least three
  AI replies are usable it adds a limitation suggesting `reasoning = "off"`.

## [0.30.0] - 2026-11-03

### Added
- Your own rules: folders of Opengrep rules (`[rules] extra_dirs` in `config.toml`, or
  "Your own rules" in Settings) are added to the built-in ones. Each file is checked
  before the analysis (YAML, ID format, no clash with built-in or reserved IDs, required
  metadata with an OWASP 2025 label, then `opengrep validate`); a file with errors is
  skipped and the run says why. A folder inside the analyzed project is ignored.
- `hdl rules --check [--dir PATH]` (alias `reglas`) checks rule folders without
  analyzing; it exits 1 when something is invalid. Settings has a "Check rules" button.
- Runs record the user rule files and IDs they used (`user_rules` in the run JSON), and
  those files change the rules version.
- "Your own rules" documentation page.

### Changed
- PyYAML is now a runtime dependency (it reads your rules).

## [0.29.2] - 2026-11-03

### Fixed
- The "Python code" step (Bandit) no longer appears for projects without Python files.
- The code-rules step names the stacks it reviews ("PHP, Laravel and Node.js code
  (built-in rules)"), in the progress list and in "How it was analyzed".
- The "AI executive summary" and "Saving the result" steps showed their catalog key
  instead of their name.

## [0.29.1] - 2026-10-19

### Changed
- The macOS installer is assembled with `diskutil image` instead of `dmgbuild`, which
  relied on the deprecated `hdiutil`. The window looks the same (background, icon
  positions, Applications shortcut); `dmgbuild` is replaced by its own `ds-store` and
  `mac-alias` libraries as development dependencies.

## [0.29.0] - 2026-10-19

### Added
- "Where to start": open findings grouped by common cause and ordered by impact (worst
  severity, then how many it resolves). A vulnerable package becomes one action ("Update
  lodash to 4.17.21: resolves 40 findings in 3 files") and a rule becomes one line with its
  count. It is in the HTML, PDF and Excel reports and behind a button in the app. AI
  suggestions are not included.

### Changed
- The release checklist verifies the DMG with `diskutil image attach` / `diskutil eject`
  (`hdiutil attach` is deprecated).

## [0.28.0] - 2026-10-19

### Added
- Every run states what was not analyzed: how many folders and files were omitted and
  which ones, in the HTML, PDF and Excel reports, the command-line summary and "How it was
  analyzed" in the app.

### Fixed
- Findings in a folder or file skipped after an earlier run are now *omitted*: they keep
  their status and are counted apart, instead of being reported as fixed.

### Changed
- The macOS build gives Flet a copy of its template that already targets macOS 12, so
  the first `flet build` succeeds instead of failing and retrying.

## [0.27.0] - 2026-10-19

### Added
- A folder that holds several separate projects (their own manifest in a subfolder and
  none at the root) is recognized: the left panel lists them with their stacks and one
  click opens one as its own project; `hdl scan --dry-run` lists them too. Analyzing the
  whole folder together works as before.

## [0.26.0] - 2026-10-19

### Added
- Files can be skipped by pattern, not only folders: an entry with `*`, `?` or `[` in
  `--exclude`, `exclude_extra` or the new "Files to skip" field of "Folders to skip" is a
  file pattern (`*.spec.ts`, `docs/*.md`). Dependency manifests and lockfiles are never
  skipped by a pattern, secrets are still searched in every file, and the run declares
  how many files the patterns left out.

### Fixed
- Saving "Folders to skip" no longer drops saved entries that the dialog does not show
  (for example `.next` when it only exists three levels deep).

## [0.25.0] - 2026-10-19

### Added
- Folders listed in the analyzed project's root `.gitignore` are also suggested to skip
  (plain names and paths; globs and negations are ignored). It is read as plain text and
  only feeds suggestions: the tools still ignore `.gitignore`, and for vendor code these
  suggestions start unchecked.

## [0.24.0] - 2026-10-19

### Added
- Suggested folders to skip, from the detected stack (`.next`, `coverage`, `Pods`,
  `DerivedData`, `.dart_tool`, `.gradle`, `target`...) and from editor or AI-assistant
  folders (`.context`, `.agents`, `.claude`, `.cursor`, `.idea`, `.vscode`). They appear at
  the top of "Folders to skip" (the button says how many there are) and in
  `hdl scan --dry-run`. Nothing is skipped until the user saves; for vendor code, editor
  and assistant folders start unchecked.

## [0.23.0] - 2026-10-19

### Added
- The left panel lists the five most recent analyses, with a traffic-light dot and the
  date; one click opens that project and its last result. The color follows accepted
  risks without a new scan.

## [0.22.1] - 2026-10-19

### Fixed
- The application icon is drawn at 1024 px from the original art (`tools/app_icon.py`)
  instead of being enlarged from the 512 px copy, so it is sharp in the Dock, Finder and
  the Windows and Linux installers. Pillow is now an explicit development dependency.

## [0.22.0] - 2026-10-19

### Added
- Windows and Linux installers can be built: `make app` (`tools/build_app.py`) picks the
  script for the current system. Windows gets an Inno Setup installer (per-user by
  default, Start menu shortcut, uninstaller, English and Spanish); Linux gets a `.deb`
  and a `.tar.gz`. They have not been tested on real machines yet.
- "Build installers" GitHub Actions workflow, manual trigger only: it keeps the
  installers as private workflow artifacts for 7 days and publishes nothing.
- Pinned Windows x64 binaries of Opengrep, Gitleaks, Trivy and OSV-Scanner in
  `tools/tools.toml`, with their SHA-256; `tools/fetch_tools.py` reads `.zip` packages.
- CI runs the test suite on Windows and macOS as well.

### Changed
- Binary lookup uses the `.exe` name on Windows.
- CONTRIBUTING explains how to build the installers and how to get past Gatekeeper,
  SmartScreen or `apt` on first run.

## [0.21.1] - 2026-10-19

### Changed
- App-first documentation: the README and the site start with "Download and install"
  and "Your first analysis", a step-by-step walkthrough with screenshots in English and
  Spanish; the command line moved to "Automation and CI". New "Desktop app tour" page.
- Screenshots live in `docs/assets/screenshots/` and are kept at 350 KB or less.

## [0.21.0] - 2026-10-19

### Added
- First-run guided tour for people new to security: what the app does, what it does
  not do (it never changes, runs or sends your code) and how to read the result. It
  shows once and can be replayed from "About"; `[general] onboarding_seen` in
  `config.toml` remembers it.

## [0.20.0] - 2026-10-19

### Added
- Demo project in `examples/demo-project/`: a deliberately vulnerable "Corner Shop"
  (Django backend, Express API, Flutter app, Dockerfiles and old lockfiles) to try the
  scanner. It yields findings at every severity, several OWASP categories and endpoints
  with and without authentication. Never deploy or run it.
- Bandit findings now carry their OWASP Top 10:2025 category (mapped from the CWE).
- License texts for LGPL-3.0 and GPL-3.0 (fpdf2 ships in the installer) and a note on
  Flutter, bundled through Flet.
- CI and license badges in the README.

### Changed
- The whole changelog is in English, including earlier entries.
- Package metadata (description, classifiers and project URLs) ready for publishing.
- Comments and hook names in configuration files are in English.

## [0.19.0] - 2026-10-19

### Added
- Documentation site (MkDocs Material, English and Spanish) for GitHub Pages: getting
  started, configuration, local AI, what it checks (OWASP Top 10:2025), supported stacks,
  reviewing findings, CLI reference and changelog. `make docs` builds it and
  `make docs-serve` previews it; `.github/workflows/docs.yml` publishes it from `main`.
- Rules catalog generated from the rule files (`tools/build_rule_docs.py`): one page per
  rule in both languages with what it detects, how to fix it, why it matters and how to
  verify it. A test fails if the committed catalog is out of date.
- `CONTRIBUTORS.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1, linked), GitHub issue
  templates (bug, false positive, new rule) and a pull request checklist.

### Changed
- `CLAUDE.md` corrections: visible name, taglines, navigation labels, data directory and
  database size.

## [0.18.5] - 2026-10-18

### Added
- Integration tests with the real OSV-Scanner and Trivy binaries
  (`tests/integration/test_dependency_scanners_real.py`): they use a read-only clone
  of the locally downloaded databases, never download anything, and are skipped when
  the binary or the databases are missing.

## [0.18.4] - 2026-10-18

### Changed
- App icon uses the emblem without lettering (`Heimdall_logo_transparente.png`), which
  stays readable at Dock and Finder sizes.

## [0.18.3] - 2026-10-18

### Changed
- `CLAUDE.md` rewritten in English for external contributors, matching the current
  code, and pointing to the project skills in `.claude/skills/`.
- The internal design proposal is no longer part of the repository; references to its
  sections were removed from code comments.

## [0.18.2] - 2026-10-18

### Changed
- Test comments, docstrings and assertion messages are in English; expected Spanish
  output in tests is unchanged.

### Added
- A test (`tests/unit/test_english_source.py`) fails if Spanish shows up in comments or
  docstrings of `src/` or `tests/`, outside the Spanish catalog and fixtures.

## [0.18.1] - 2026-10-18

### Changed
- Source code comments, docstrings and developer-facing messages under `src/` and
  `tools/` are in English, keeping the reasoning behind each decision. Palette
  constants have English names (`NIGHT`, `GOLD`, `BRONZE`…). No behavior changes.

## [0.18.0] - 2026-10-18

### Changed
- **Breaking (rule format):** English is the primary language of every rule:
  `message`, `metadata.title` and `metadata.recommendation` are in English, and the
  Spanish translation lives in `message_es`, `title_es` and `recommendation_es`.
  `severity_hdl` and `confidence` use English codes (`critical`, `high`, `medium`,
  `low`, `info`). Patterns, IDs and classifications did not change.
- Rule test fixtures live in `positive/` and `negative/`, and the expected counts in
  `tests/rules/expected.yaml`.

## [0.17.0] - 2026-10-18

### Changed
- **Breaking:** everything that is stored or exported uses English names: enum members,
  the run dictionary and JSON report keys (`findings`, `summary`, `baseline`,
  `verdict`, `limitations`…), the AI response fields (`verdict`, `explanation`,
  `suggested_fix`…), profile codes (`quick`, `standard`, `full`, `vendor`, `custom`;
  the Spanish names are still accepted as input), threshold names and data files
  (`exclusions.json`, `verdict_thresholds.json`). AI findings are `AI-IDOR-001` and
  `AI-FLOW-001`.
- Old data is archived as `*.v<N>.bak`, never deleted, and the next run says so. Saved
  folder exclusions and verdict thresholds go back to their defaults, and the
  thresholds PIN must be set again.
- When the system language is neither English nor Spanish, the app now falls back to
  English.
- App icon made from the full "Heimdall Guardian" logo; the watermark is again the
  seal without lettering; installer icons reduced to 108 pt so the Applications
  folder fits its frame.

## [0.16.1] - 2026-10-18

### Changed
- App icon: plain black body with the standard macOS rounded-square shape and no gold
  outline, which macOS sometimes cropped.
- Reports use the `Heimdall_logo` emblem with the wordmark on its right; the watermark
  uses the corrected monochrome artwork.
- Installer: new Bifröst background with empty frames; the app and the Applications
  shortcut sit on them (window 836×470 pt, icons at 124 pt).

## [0.16.0] - 2026-10-18

### Added
- Project skills for contributors in `.claude/skills/`: `rule-pack`, `stack-support`,
  `release` and `i18n-text`.
- The macOS installer window shows the Bifröst artwork as background, with the app and
  the Applications shortcut placed over the drawn icons (built with `dmgbuild`).

### Changed
- New "Heimdall Guardian" artwork: sidebar logo, PDF cover (emblem and wordmark),
  watermark, "About" image and a new app icon with rounded corners and transparency.
- New window layout: the left panel keeps only the analysis options, with the logo
  fixed at the top, its own scroll and "Analyze" fixed at the bottom. "New analysis",
  "What it checks", "Settings" and "About" moved to a navigation bar above the main
  area; on narrow windows it shows icons with tooltips.

### Fixed
- Changelog dates for 0.12.0 to 0.15.0 (they said 2026-10-19).

## [0.15.0] - 2026-10-18

### Changed
- Public documentation is now in English: `README.md`, `CONTRIBUTING.md`,
  `SECURITY.md` and `THIRD-PARTY-NOTICES.md`, each with a Spanish version in `*.es.md`.
  `NOTICE` carries both languages. The artwork notice stays verbatim in Spanish, with a
  courtesy English translation that has no legal standing of its own.
- The changelog is written in English from this version on.
- The stated size of the vulnerability databases is now about 2 GB, which matches what
  is actually downloaded with every supported ecosystem.

### Fixed
- The README said the installer contains `Heimdall.app`; it contains
  `Heimdall Guardian.app`.

## [0.14.0] - 2026-10-18

### Added
- Every finding from the own rules, the endpoint inventory, the AI and the tools'
  recommendations carries its title, description and recommendation in English and
  Spanish, and is shown in the chosen language. What an external tool writes (a CVE
  description, Bandit's message) is shown as it is.
- The AI review is done in the chosen language: prompts in English or Spanish, with the
  same protections against injection. The executive summary is written in that language.

### Changed
- **Breaking:** the AI values are English codes (`likely_real`, `likely_false`,
  `uncertain`; `high`/`medium`/`low`/`none`) and the AI cache distinguishes the language,
  so the first analysis with AI queries the model again. Each project's history starts
  over; the previous one is archived.
- Switching language does not create "new" findings: the fingerprint does not depend on
  the language.

## [0.13.0] - 2026-10-18

### Added
- The reports (HTML, PDF, Excel and SARIF), the CLI and the core texts (OWASP, coverage
  per stack, limitations, verdict, thresholds, validation and AI errors) come out in the
  chosen language. A report regenerated with `hdl report` or opened in the app uses the
  current language, even if the analysis was done in another one.
- The CLI uses English names (`tools`, `databases`, `--profile`, `--output`,
  `--update-databases`, `--no-baseline`, `--ai`...). The Spanish names keep working as
  aliases, and the profiles accept `quick`, `standard`, `full`, `vendor` and `custom`.
- The AI progress ("revisando 3 de 9" / "reviewing 3 of 9") follows the language.

### Changed
- **Breaking:** limitations and own messages are stored as a code and data, not as text.
  Each project's history starts over; the previous one is archived as it already was.
- The reports and the CLI show the profile name ("Estándar") instead of its code
  ("estandar").

## [0.12.0] - 2026-10-18

### Added
- The interface is in English and Spanish. Choose the language in **Settings →
  Idioma / Language**; it applies immediately without losing the open folder or result.
  If you do not choose one, your system language is used (on macOS, the preferred one in
  Settings) or Spanish.
- `hdl --lang en|es` (alias `--idioma`) and the `HDL_LANG` variable set the language.

### Changed
- **Breaking:** the `config.toml` keys are in English (`[exclusions]`, `[databases]`,
  `enabled`, `active_destination`, `[[llm.destinations]]`, `model_summary`...; the README
  has the full map). A file with the previous keys is not read: the app starts with the
  default configuration and tells you, and when saving it backs up the old one as
  `config.toml.v1.bak`. Enter your AI servers again; if you use the same destination name,
  the keychain token still works.
- English as the base language of the text catalog; Spanish is its translation.
- Still in Spanish in both languages: reports, CLI, OWASP and coverage explanations,
  limitations, and the title and recommendation of each finding.

## [0.11.0] - 2026-10-18

### Changed
- First step of internationalization: the values that are stored and exported (severity,
  status, category, origin, confidence, verdict) are neutral English codes (`critical`,
  `new`, `accepted`...). What you see comes from a catalog of labels (`i18n/`) whose base
  language is English; for now it is shown in Spanish, as before.
- **Breaking:** each project's baseline starts over. The previous database is archived as
  `baseline.db.v1.bak` inside the data directory and the report says so. Baseline files
  exported with earlier versions can no longer be imported. The JSON and the SARIF carry
  the new codes.

## [0.10.0] - 2026-10-18

### Added
- Own code rules for Kotlin and Android (12): certificates and hostnames accepted without
  validation, sensitive data in `SharedPreferences` and DataStore, files readable by other
  apps, `http://` connections, `addJavascriptInterface` and WebView with file access,
  sensitive data in logs, weak cryptography, secrets in the code (also in
  `build.gradle`), hand-built SQL (SQLite and Room), mutable `PendingIntent`s and
  unprotected receivers, and exported components without permission or unencrypted
  traffic in `AndroidManifest.xml` and `network_security_config.xml`.

## [0.9.0] - 2026-10-18

### Added
- Own code rules for Swift and iOS (13): disabled TLS validation, sensitive data in
  `UserDefaults`, Keychain with weak accessibility, `http://` connections, WebView
  bridges and file access, `UIWebView`, sensitive data in logs, weak cryptography,
  secrets in the code, hand-built SQL (SQLite, GRDB, FMDB), transport security
  exceptions in `Info.plist`, `get-task-allow` and insecure deserialization with
  `NSKeyedUnarchiver`.

### Changed
- The native configuration rule (`AndroidManifest.xml` and `Info.plist`) no longer says
  "Flutter" in its title: it also applies to native apps.

## [0.8.0] - 2026-10-18

### Added
- Own code rules for Dart and Flutter (10): TLS certificates accepted without validation,
  tokens and passwords in unencrypted storage, `http://` connections, WebView with
  JavaScript and bridges into the app, sensitive data in logs, weak cryptography, secrets
  written in the code, hand-built SQL in sqflite and drift, and the native configuration
  (`AndroidManifest.xml` and `Info.plist`).

### Changed
- The visible name is "Heimdall Guardian" in the app, the reports (including SARIF), the
  CLI, the installer (`Heimdall Guardian.app`, `HeimdallGuardian-<version>-<arch>.dmg`)
  and the documentation. The `hdl` command, the data directory and the keychain do not
  change: your history, your acceptances and the AI token are still there. If you had
  `Heimdall.app`, you can delete it after installing the new one.
- In a Flutter app, the native folders (`android/`, `ios/`) no longer produce "no rules"
  notices for Android, Kotlin or Swift.

## [0.7.1] - 2026-10-18

### Fixed
- The app build failed if the `build/macos` folder was open in Finder (it recreates
  `.DS_Store` while the folder is being deleted): it now retries.

### Changed
- The name and trademarks note is generic: Heimdall Guardian is not affiliated with any
  company, product or brand with a similar name.

## [0.7.0] - 2026-10-18

### Added
- "What Heimdall checks", for non-technical readers: what OWASP is, the ten categories of
  the Top 10:2025 in plain language with an everyday example, how much Heimdall covers
  them (yes, partly or no) and how many findings there are in each. It is in the HTML,
  PDF and Excel reports, and in the app with the "What it checks" button.
- "For experts" in the detail of each finding: rule, tool, CWE, OWASP, confidence, exact
  location and how to verify it by hand. The HTML report also carries "How to verify it".
- In the README, how to review and adjust findings without writing rules, and
  `CONTRIBUTING.md` for proposing rules or extractors to the project.
- Note that Heimdall Guardian is not affiliated with Heimdal® or Heimdal Security A/S.

### Changed
- The classifications follow OWASP Top 10:2025 (previously 2021). Saved analyses are also
  shown with the new categories, without changing what was stored.

## [0.6.0] - 2026-10-18

### Added
- Own code rules for Node.js and TypeScript (16): SQL and NoSQL injection, command and
  code execution, file paths, SSRF, XSS on the server and in the browser, open redirect,
  badly validated JWTs or with a secret in the code, permissive CORS with credentials,
  insecure cookies and session, insecure deserialization and weak cryptography. They
  cover Express and NestJS.
- Endpoint inventory for Express (routes, routers mounted with a prefix across files,
  authentication middleware) and NestJS (controllers, guards per class, method or global,
  public decorators). Routes without authentication generate AUTHZ-001 and AUTHZ-002, as
  in the other stacks.

## [0.5.0] - 2026-10-18

### Added
- Detection of more stacks: TypeScript, Dart, Flutter, Swift, Kotlin, Android, Java, Go,
  Ruby and Rust (in addition to Python, Django, PHP, Laravel, .NET and Node.js).
- OSV databases for Go, crates.io, RubyGems, Pub (Dart/Flutter), Maven and Swift: their
  dependencies are checked with both sources. Update the databases to download them.
- The report says, per stack, which layers were checked: for stacks without own code
  rules it clarifies that only secrets, dependencies and configuration are checked.
- "Supported stacks" section in the README.

### Fixed
- If the OSV database of a single ecosystem was missing, the report said all the
  databases were missing. It now names the missing ecosystem.

## [0.4.1] - 2026-10-18

### Changed
- Tools updated: Trivy 0.76.0, OSV-Scanner 2.7.0 and Opengrep 1.31.0, with their SHA-256
  verified. The integration and rule tests pass with all three.

### Fixed
- The app build no longer fails when the previous output (`build/macos`) was left without
  permissions: it is cleaned before building. If `hdiutil` says "resource busy", it
  retries, and only the installer of the current version is left in `dist/`.

## [0.4.0] - 2026-10-18

### Added
- `hdl herramientas --novedades` (now `hdl tools --updates`): compares each tool's
  version with the latest published on GitHub or PyPI and gives the link to its notes. It
  only connects when asked, sends nothing of the code and downloads or changes nothing.
- In the README, what is updated and how often: the vulnerability databases every week;
  the rules and tools, with each Heimdall version.

## [0.3.0] - 2026-10-17

### Added
- Several AI configurations from the application: each with its own server and models
  (it can be the same server with other models). They are added, removed and tested
  separately in **Settings**, where you also choose which to use and which as a fallback.
- **AI for this analysis** in the left panel, when there is more than one: use another
  configuration for that analysis only.
- `hdl scan --ia NAME` (now `--ai`) for the same on the command line.

## [0.2.2] - 2026-10-16

### Changed
- The AI review of an endpoint that already has a finding (without authentication) is
  attached to that finding as a suggestion, instead of creating another one that repeats
  it. A separate AI suggestion is only created when the route does have authentication
  and the model sees a high risk (for example, that it does not validate that the record
  belongs to whoever queries it).
- The AI suggestion in a finding's detail also shows the suggested fix and, for
  endpoints, the risk of accessing other people's records and of skipping steps.

### Added
- "Executive summary with AI" and "Saving the result" steps in the progress, so it does
  not look stalled after the AI review.

## [0.2.1] - 2026-10-16

### Changed
- The AI assessment of findings no longer repeats those of endpoints without
  authentication (AUTHZ-001 and AUTHZ-002): those routes are reviewed by the endpoints
  task, which has more context. In projects with many controllers, the AI review makes
  noticeably fewer queries. If there is no model for endpoints, they are still assessed
  as before.

### Added
- AI progress query by query ("revisando 23 de 150") in the application and in
  `hdl scan`.
- Cancel during the AI review: it stops when the current query ends, instead of waiting
  for the whole review to finish.

### Fixed
- The list of previous analyses left the connection to each database open.

## [0.2.0] - 2026-10-16

### Added
- Remove a project from the history from the welcome screen (trash icon) or with
  `hdl forget <folder> --si` (now `--yes`). It deletes its analyses, baseline and
  acceptances; it does not touch the project folder or the reports already saved.
- Notice when a tool finds something in folders that are skipped (for example, `bin/` and
  `obj/` of .NET), with examples of where.
- Changelog and visible version in each update.

### Fixed
- Dialogs with little content no longer take up the whole height of the window.

### Changed
- The technical annex counts, per tool, the findings that reached the report, not their
  raw count; before it could say "872" and list none.
- The vulnerability database column says "not used" for the tools that do not work with
  one (Gitleaks, Opengrep, Bandit, inventory).
- Large files are always analyzed as long as they are text (styles, templates, source
  maps...); only binaries are skipped, and the notice says which.

## [0.1.0] - 2026-10-09

First version.

- Analysis of secrets (Gitleaks), dependencies (Trivy and OSV-Scanner), insecure code
  (Opengrep with 30 own rules and Bandit), configuration and endpoint inventory for
  Django/DRF, ASP.NET, Laravel and PHP.
- Baseline between analyses, risk acceptance and false positives with justification.
- Optional review with a local AI model.
