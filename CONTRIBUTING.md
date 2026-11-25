# Contributing

[Leer en español → CONTRIBUTING.es.md](CONTRIBUTING.es.md)

Thank you for wanting to improve Heimdall Guardian. This guide summarizes what you need to
propose a rule, an endpoint extractor or another change. `CLAUDE.md` has the
full architecture.

## Setting up the environment

```bash
make setup                  # tools, dependencies and pre-commit hooks
pre-commit run --all-files  # full QA, the same that runs on every commit and in CI
```

`pre-commit` is used from the machine's global installation. Ruff, mypy and pytest run
with `uv run`, to use the versions in `uv.lock`.

## Non-negotiable principles

A change that violates any of them is rejected even if it works.

1. **Read-only.** Nothing is ever written inside the analyzed folder; results, baseline
   and cache live in the app's data directory.
2. **The analyzed code is never run.** No `pip install`, `npm install`, `composer
   install`, `dotnet restore` or project scripts: it may be hostile. Dependencies are
   analyzed by reading manifests and lock files.
3. **Code does not leave the local network.** The AI destination must be local or an
   internal network over HTTPS; cloud models and CLIs are rejected.
4. **It works offline.** The tools ship with pinned versions and checksums; vulnerability
   databases are updated only on demand.
5. **Deterministic first, AI second.** Every finding declares its origin. The AI never
   raises a severity on its own nor counts toward the verdict without human confirmation.
6. **Traceability.** Every report records the code hash, the profile, the tool and rule
   versions, the age of the databases and the AI model.

In addition, secrets are always masked in reports, logs and stored snippets, and the
analyzed code never configures the tools (`.gitleaks.toml` files, `nosec` comments, and
so on).

## Proposing a rule

The own rules are in Opengrep format (Semgrep's), in `rules/heimdall/<stack>/`, with
**one file per rule** named after its ID (`DJ-SQL-001.yaml`). The second segment of the ID
decides the category: `CONF` goes to configuration, `AUTH` and `IDOR` to access control
and the rest to insecure code.

Required `metadata`:

- `cwe` and `owasp` (with the label of the current edition, for example
  `"A05:2025 Injection"`; the categories are in `src/heimdall_guardian/core/owasp.py`),
- `severity_hdl` (`critical`, `high`, `medium`, `low` or `info`) and `confidence`
  (`high`, `medium` or `low`); these are the stored codes,
- **both languages:** English is the base language: the rule's own `message` plus
  `title` and `recommendation` in `metadata`. Spanish goes in `message_es`, `title_es`
  and `recommendation_es` (second person). A rule without the Spanish fields falls back
  to English, which is a gap, not a style.

Take any existing rule as a model (for example `rules/heimdall/django/DJ-SQL-001.yaml`).
Then:

1. Create the fixtures in `tests/rules/fixtures/<ID>/positive/` and `.../negative/`. They
   go there and not next to the rule, because the engine would read any YAML beside it as
   rules. The fixture code is deliberately vulnerable and is never run.
2. Record in `tests/rules/expected.yaml` how many exact findings the positive fixture
   gives. The negative one must give zero.
3. If the rule's CWE has no guide in `_HINTS` of `core/owasp.py`, consider adding "How to
   verify it".
4. Check that it passes with the real engine:

   ```bash
   HDL_REQUIRE_RULE_ENGINE=1 uv run pytest tests/rules -q
   ```

   Without the engine installed, those tests are skipped locally, but they fail in CI.

A rule with many false positives costs more than it brings: prefer narrow patterns and a
negative fixture that includes similar legitimate cases.

## Proposing an endpoint extractor

Each framework has its own extractor in `src/heimdall_guardian/authz/` (`django.py` with
`ast`; `dotnet.py`, `laravel.py`, `php.py` and `node.py` with text analysis) that returns
the endpoint inventory without running anything.

1. Create the extractor with `extract() -> list[Endpoint]` and the `notes` list to declare
   what it could not read, and register it in `authz/adapter.py`.
2. Add an example project in `tests/fixtures/authz_<stack>/`.
3. In `tests/unit/test_authz.py`, compare the full inventory against the expected routes:
   the dictionary must match exactly.
4. The text of the findings the extractor produces goes in both languages (see below).

## Language and visible text

Heimdall Guardian is bilingual (English and Spanish) and **English is the base language**.

- **Any new visible text** (interface, reports, CLI help, messages, adapter and AI texts)
  goes into the catalog: the key and its English text in
  `src/heimdall_guardian/i18n/messages_en.py` (the source), and its translation in
  `src/heimdall_guardian/i18n/messages_es.py`. Do not write visible strings in the code,
  in either language. Use `t()` (or `tn()` for plurals, with `.one` / `.other` keys) to
  read them.
- Keys must exist in both catalogs with the same placeholders. A missing translation falls
  back to English and then to the key.
- Values stored in the database and in JSON are neutral codes, not translated text
  (`CRÍTICA`, `NUEVO`, `likely_real`...); their labels are in the catalog.
- Rules need the six texts described above; findings of the endpoint inventory, the tool
  adapters and the AI also carry both languages.
- The tests that watch this live in `tests/unit/`: `test_i18n.py` (enum labels and
  catalogs), `test_i18n_messages.py` (same keys and placeholders in both catalogs, every
  key used in the code exists, no Spanish literals in the UI or in the checked modules),
  `test_i18n_core.py` (reports and stored messages in both languages),
  `test_i18n_findings.py` (rules, adapters, AI prompts and caches in both languages) and
  `test_cli_i18n.py` (the command line). Run them with `uv run pytest tests/unit -q -k
  i18n`.
- The authors' notice on the graphic elements (`palette.ART_NOTICE`) is legal text and
  stays in Spanish, as written, in the README, `NOTICE` and the "About" screen.
- Spanish text (es-MX) uses the second person ("tú") and plain verbs; English text is
  direct and in the second person too.

## Style and conventions

- **Code:** ruff (format and lint), strict mypy on `src/` and 75 % minimum coverage. UI
  logic goes in `ui/model.py` (no Flet, with tests); `ui/app.py` only assembles controls.
- **Configuration keys** (`config.toml`) are in English.
- **Public documentation site:** pages in `docs/` come in pairs too (`X.md` and `X.es.md`).
- **Version and changelog:** whoever delivers a change bumps the version (in
  `pyproject.toml` and in `src/heimdall_guardian/__init__.py`) and adds its entry to
  `CHANGELOG.md`, in Keep a Changelog format.
- **Public documentation** (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `THIRD-PARTY-NOTICES.md`) is in English, each with its Spanish version in `*.es.md`.
  When you change one, update the other. `NOTICE` carries both languages in one file.
- **Third-party dependencies and tools:** if you add or change one, update
  `THIRD-PARTY-NOTICES.md` (and its `.es.md`) and, if needed, `licenses/`.

## Commits

Short messages in the Conventional Commits style that the history uses (write them in
English):

```
feat: version 0.6.0, code rules and endpoint inventory for Node.js and TypeScript
fix: the Trivy database download failed from the app
docs: how to use local models with Ollama and which model to pick
chore: version 0.4.1, Trivy 0.76.0 and OSV-Scanner 2.7.0
```

Before sending your change, get `pre-commit run --all-files` green. The pull request template
has the full checklist.

## Documentation site and contributors

- The documentation site (`docs/`, `mkdocs.yml`) uses MkDocs Material. Its tools are in the
  `docs` dependency group (development only; they are not shipped in the installer).
  `make docs` regenerates the generated pages and builds the site with strict checks;
  `make docs-serve` gives a live preview. `mkdocs build` on its own needs
  `tools/build_rule_docs.py` to have run first (the generated pages are missing otherwise);
  `make docs` does both.
- The rules catalog, the OWASP page, the stacks page and (git-ignored) the CLI reference are
  generated by `tools/build_rule_docs.py`. After changing a rule, run `make docs` and commit
  the result: `tests/unit/test_rule_docs.py` fails if `docs/rules/` is out of date.
- Add yourself to [CONTRIBUTORS.md](CONTRIBUTORS.md) and
  [CONTRIBUTORS.es.md](CONTRIBUTORS.es.md) in the same pull request as your contribution.
- Everyone taking part is expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

Screenshots live in `docs/assets/screenshots/` (one per language, `NN-name-en.png` / `-es.png`); keep each one at 350 KB or less, since the pre-commit hook rejects files over 512 KB.

## Keeping dependencies current

- `make outdated` prints one report (it changes nothing and always exits 0; `--strict` exits
  1 if anything is outdated): Python packages you declare directly, the tools pinned in
  `tools/tools.toml` and the GitHub Actions in the workflows. Major jumps are marked. If
  the network is down it says so.
- `make upgrade` tries to move everything to the latest compatible versions (`make upgrade
  PACKAGE=ruff` for one). It backs up `pyproject.toml` and `uv.lock`, runs `uv lock
  --upgrade`, moves the `flet==` pins of `[tool.flet.*]` to the locked Flet, and runs
  `pre-commit run --all-files` plus the rule and integration tests. If a step fails it
  restores both files and shows the tail of the failing output; if all is green it lists the
  version changes. Then add a `CHANGELOG.md` entry.
- Dependabot opens weekly pull requests (`.github/dependabot.yml`): one for patch and
  minor updates and one per major, for Python and for GitHub Actions, which are pinned by
  commit SHA with the version in a comment.
- When Flet or pillow change, run `make app` and check the app and the DMG by eye: the
  window, the icon and the installer background are the parts a test cannot see. Tool
  updates still mean editing `tools/tools.toml` (version, URL and SHA-256 together).

## Building the installers

`make app` (or `uv run python tools/build_app.py`) builds the desktop app and its installer
for the system you run it on, and leaves them in `dist/`. It runs `tools/build_bundle.py`
first, then `flet build`. You must build on the target system: the bundle holds native
binaries.

| System | You need | Output in `dist/` |
|---|---|---|
| macOS | Flutter and Xcode | `HeimdallGuardian-<version>-arm64.dmg` |
| Windows | Flutter, Visual Studio with "Desktop development with C++", and [Inno Setup](https://jrsoftware.org/isinfo.php) 6 or 7 | `heimdall-guardian-<version>-windows-x64-setup.exe` |
| Linux | Flutter and `sudo apt install clang cmake ninja-build pkg-config libgtk-3-dev liblzma-dev libmpv-dev libasound2-dev libsecret-1-dev python3-venv` (`dpkg-deb` for the `.deb`; `python3-venv` so the app can install the `hdl` command) | `heimdall-guardian-<version>-linux-x64.tar.gz` and `heimdall-guardian_<version>_amd64.deb` |

You can also build all three without a local setup: in GitHub go to **Actions -> Build
installers -> Run workflow**. The files appear as artifacts of the run and expire after
7 days; nothing is published as a release.

**Which Flutter.** `flet build` needs the Flutter version its Flet release was tested with:
same major and minor number (Flet 1.1.3 asks for 3.47.x; a newer Flutter is rejected too).
To see the exact version, run `uv run python -c "import flet.version as v; print(v.flutter_version)"`.
It looks first in `~/flutter/<version>/` (`%USERPROFILE%\flutter\<version>\` on Windows)
and then for the `flutter` on the PATH. When neither fits, it prints "Flutter SDK not found
or invalid version installed" and offers to download that version into `~/flutter/<version>/`
(around 1-2 GB, once). That copy lives apart from yours, so your own Flutter and your other
projects are untouched. Accepting the download is the recommended path, which is why we
suggest `~/flutter/<version>/` as the place for Flutter on every system, rather than the
different folders the Flutter and Flet guides give per system.

If you use Flutter for other work: before Flet asks, the build script prints a notice when
the download is about to happen. The download does not upgrade, downgrade or replace your
Flutter and does not change your PATH, so your other projects keep their version. What it
shares with your Flutter is the package cache (`~/.pub-cache`, or `%LOCALAPPDATA%\Pub\Cache`
on Windows) and the user-wide Flutter settings, where Flet only turns on desktop support for
the current system. To keep full control, answer `n` and put a Flutter with the required
major and minor version on the PATH or in `~/flutter/<version>/` yourself. The build scripts skip the
`flutter doctor` summary Flet prints after a failure (its PATH warnings read like the cause
but are not) and print a short hint instead: the real error is in the first red lines.

The installers are not signed, so each system warns the first time:

- **macOS (Gatekeeper):** the signature is ad hoc. In **Applications**, right-click the
  app, choose **Open** and confirm.
- **Windows (SmartScreen):** click **More info** and then **Run anyway**.
- **Linux:** `sudo apt install ./heimdall-guardian_<version>_amd64.deb`, or extract the
  `.tar.gz` and run the binary inside its `app/` folder.

### Building on Windows

Windows does not ship `make`. Every target in the `Makefile` only calls a Python script, so
in PowerShell run the scripts directly with `uv run`.

Install once, then open a new PowerShell so it picks up the new PATH:

- Python 3.12 or later and [uv](https://docs.astral.sh/uv/):
  `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.
- Flutter, in the version Flet asks for (see **Which Flutter** above). You can skip
  installing it yourself: `flet build` offers to download it the first time.
- Visual Studio 2022 or 2026 (Community is enough) with the **Desktop development with C++**
  workload, which brings the MSVC build tools, the Windows SDK and the C++ CMake tools that
  Flutter needs. Without them the build stops with "Unable to find suitable Visual Studio
  toolchain"; `flutter doctor -v` lists what is missing.
- **Developer Mode** turned on (Settings -> System -> For developers, or
  `start ms-settings:developers`): Flutter needs symlinks to build with plugins and stops with
  "Building with plugins requires symlink support" without it.
- [Inno Setup](https://jrsoftware.org/isinfo.php) 6 or 7 (or `choco install innosetup`). If
  `ISCC.exe` is not on the PATH, the script also looks in the `Inno Setup 7` and
  `Inno Setup 6` folders under `C:\Program Files (x86)`, `C:\Program Files` and, for an
  install without administrator rights, `%LOCALAPPDATA%\Programs`.

Then, from the repository folder:

| `make` target | PowerShell equivalent |
|---|---|
| `make tools` | `uv run python tools/fetch_tools.py` |
| `make setup` | `uv run python tools/fetch_tools.py`, then `uv sync` |
| `make app` | `uv run python tools/build_app.py` |
| `make test` | `uv run pytest --cov` |

`uv run python tools/build_app.py --dry-run` only prints which script would run. On Windows
`build_app.py` builds the CLI wheel and then runs `tools/build_windows.py`, which bundles the
rules and binaries, runs `flet build windows` and compiles
`packaging/windows/heimdall-guardian.iss` with Inno Setup. The installer lands in
`dist\heimdall-guardian-<version>-windows-x64-setup.exe`.

If it fails:

- **"Inno Setup (ISCC.exe) was not found"**: install Inno Setup, or add the folder that
  holds `ISCC.exe` to the PATH (for this session only:
  `$env:Path += ";C:\path\to\Inno Setup 7"`).
- **`flet build` errors**: usually Flutter or the Visual Studio C++ workload is missing; run
  `flutter doctor -v`.
- **Path too long**: enable long paths in Windows (`LongPathsEnabled`) or clone the
  repository into a short path such as `C:\dev\hg`.

## Cutting a release

Releases are cut from a tag; `.github/workflows/release.yml` does the rest and leaves a
**draft** that you publish by hand.

1. Bump the version in `pyproject.toml` and `src/heimdall_guardian/__init__.py`, add its
   entry to `CHANGELOG.md` and run `uv lock` (see the `release` skill for the full QA).
2. Merge to `main`, then tag and push: `git tag vX.Y.Z && git push origin vX.Y.Z`. The
   workflow fails if the tag and the `pyproject.toml` version differ.
3. The workflow runs the same QA as CI, builds the light CLI wheel and the server archive,
   and creates a draft GitHub release with the wheel, `install_hdl.py`, the archive,
   `SHA256SUMS` and the changelog section of that version as notes. You can preview the notes
   with `uv run python tools/changelog_section.py X.Y.Z`.
4. Review the draft. Build the desktop installers (Actions -> Build installers), test them on
   real machines and attach them to the draft yourself: they are never attached
   automatically.
5. Publish the release.

**Optional: PyPI.** The `pypi` job uses trusted publishing (no token stored) and only runs if
the repository variable `PUBLISH_PYPI` is `true`. One-time setup: on pypi.org create the
project `heimdall-guardian` (or a "pending publisher"), add a trusted publisher with this
GitHub repository, workflow `release.yml` and environment `pypi`, create the `pypi`
environment in the repository settings (a required reviewer is a good idea) and set the
variable. Only the light wheel is uploaded; there is no sdist because it would not carry the
generated `_bundle/`.

## Vulnerabilities in Heimdall Guardian

Do not open a public issue: follow [SECURITY.md](SECURITY.md).
