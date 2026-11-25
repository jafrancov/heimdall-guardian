# Configuration

Heimdall Guardian reads `config.toml` from its data directory:

| System | Data directory |
|---|---|
| macOS | `~/Library/Application Support/Heimdall/` |
| Windows | `%APPDATA%\Heimdall\` |
| Linux | `$XDG_DATA_HOME/Heimdall/` (or `~/.local/share/Heimdall/`) |

The app and the `hdl` command share this folder: databases, history and settings are downloaded and stored once. `hdl tools` prints where it is.

`HDL_DATA_DIR` moves the whole directory and `HDL_CONFIG` moves only the file.
`HDL_BASES_DIR` moves only the vulnerability databases (`bases/`, about 2 GB): useful to
keep an isolated `HDL_DATA_DIR` for tests or one-off runs and still reuse your databases. Create it
with defaults and see where it is:

```bash
uv run hdl config --init
```

The same settings are available in the app under **Settings**. Keys are in English; a file
from an earlier version with Spanish keys is not read (rename or delete it and create a new
one).

## Default file

```toml
[general]
default_profile = "standard"
language = ""                 # "en", "es" or "" (follow the system)

[exclusions]
paths = ["node_modules", "venv", ".venv", "vendor", "bin", "obj", "dist", "build", "static/CACHE", "migrations"]
exclude_extra = []            # more folders to skip, for every project
include_extra = []            # folders from the default list that you do want analyzed
max_file_size_kb = 1024

[databases]
alert_age_days = 7            # warn when the databases are older than this

[llm]
enabled = true
active_destination = "laptop"
fallback_destination = "none"
allowed_hosts = []
internal_ca = ""
temperature = 0.1
max_targets_per_run = 150
timeout_per_target_s = 120

[[llm.destinations]]
name = "laptop"
url = "http://localhost:11434/v1"
runtime = "ollama"
requires_token = false
context_tokens = 32768
model_triage = "<unset>"
model_endpoints = "<unset>"
model_summary = "<unset>"
model_consensus = "<unset>"
reasoning = "off"
```

## Sections

- **`[general]`**: the default profile and the interface language.
- **`[exclusions]`**: folders that are not analyzed. The built-in defaults always apply;
  use `include_extra` to analyze one of them. `max_file_size_kb` only discards binaries:
  a large text file is analyzed and declared as a notice.
- **`[databases]`**: after how many days the reports flag the vulnerability databases as old.
- **`[rules]`**: `extra_dirs`, folders with your own rules, see
  [Your own rules](custom-rules.md).
- **`[llm]`** and **`[[llm.destinations]]`**: the optional AI review, see
  [Local AI](local-ai.md). Model names are never hard-coded: write them as your runtime lists
  them. Tokens go in the system keychain (`hdl llm --save-token`), never in this file.

Per-project folders to skip are stored separately in the data directory and edited from
**Folders to skip** in the app or with `--exclude` / `--include`.
