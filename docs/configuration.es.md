# Configuración

Heimdall Guardian lee `config.toml` de su directorio de datos:

| Sistema | Directorio de datos |
|---|---|
| macOS | `~/Library/Application Support/Heimdall/` |
| Windows | `%APPDATA%\Heimdall\` |
| Linux | `$XDG_DATA_HOME/Heimdall/` (o `~/.local/share/Heimdall/`) |

La app y el comando `hdl` comparten esta carpeta: las bases, el historial y los ajustes se descargan y guardan una sola vez. `hdl tools` muestra dónde está.

`HDL_DATA_DIR` mueve todo el directorio y `HDL_CONFIG` solo el archivo.
`HDL_BASES_DIR` mueve solo las bases de vulnerabilidades (`bases/`, unos 2 GB): sirve para
usar un `HDL_DATA_DIR` aislado en pruebas o corridas sueltas y reutilizar tus bases. Créalo con los
valores por omisión y mira dónde está:

```bash
uv run hdl config --init
```

Los mismos ajustes están en la aplicación, en **Ajustes**. Las claves están en inglés; un
archivo de una versión anterior con claves en español no se lee (renómbralo o bórralo y crea
uno nuevo).

## Archivo por omisión

```toml
[general]
default_profile = "standard"
language = ""                 # "en", "es" o "" (seguir el sistema)

[exclusions]
paths = ["node_modules", "venv", ".venv", "vendor", "bin", "obj", "dist", "build", "static/CACHE", "migrations"]
exclude_extra = []            # más carpetas por omitir, en todos los proyectos
include_extra = []            # carpetas de la lista base que sí quieres analizar
max_file_size_kb = 1024

[databases]
alert_age_days = 7            # avisar cuando las bases tengan más días que esto

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

## Secciones

- **`[general]`**: el perfil por omisión y el idioma de la interfaz.
- **`[exclusions]`**: carpetas que no se analizan. Las de la lista base siempre aplican; usa
  `include_extra` para analizar una. `max_file_size_kb` solo descarta binarios: un archivo
  de texto grande se analiza y se declara como aviso.
- **`[databases]`**: a partir de cuántos días los reportes marcan las bases como viejas.
- **`[rules]`**: `extra_dirs`, carpetas con tus propias reglas, ver
  [Tus propias reglas](custom-rules.md).
- **`[llm]`** y **`[[llm.destinations]]`**: la revisión con IA opcional, ver
  [IA local](local-ai.md). Los nombres de modelo nunca van fijos: escríbelos como los lista
  tu motor. Los tokens van en el llavero del sistema (`hdl llm --save-token`), nunca en este
  archivo.

Las carpetas por omitir de cada proyecto se guardan aparte en el directorio de datos y se
editan en **Carpetas por omitir** en la aplicación o con `--exclude` / `--include`.
