# Cómo contribuir

[Read in English → CONTRIBUTING.md](CONTRIBUTING.md)

Gracias por querer mejorar Heimdall Guardian. Esta guía resume lo necesario para proponer
una regla, un extractor de endpoints u otro cambio. `CLAUDE.md` (en inglés) tiene la
arquitectura completa.

## Preparar el entorno

```bash
make setup                  # herramientas, dependencias y hooks de pre-commit
pre-commit run --all-files  # QA completo, el mismo que corre en cada commit y en la CI
```

`pre-commit` se usa desde la instalación global del equipo. Ruff, mypy y pytest corren
con `uv run`, para usar las versiones de `uv.lock`.

## Principios que no se negocian

Un cambio que viole alguno se rechaza aunque funcione.

1. **Solo lectura.** Nunca se escribe dentro de la carpeta analizada; resultados, línea
   base y caché viven en el directorio de datos de la aplicación.
2. **Nunca se ejecuta el código analizado.** Nada de `pip install`, `npm install`,
   `composer install`, `dotnet restore` ni scripts del proyecto: puede ser hostil. Las
   dependencias se analizan leyendo manifiestos y lockfiles.
3. **El código no sale de la red local.** El destino de la IA debe ser local o una red
   interna sobre HTTPS; se rechazan modelos y CLIs en la nube.
4. **Funciona sin internet.** Las herramientas van empaquetadas con versión y checksum
   fijos; las bases de vulnerabilidades se actualizan solo bajo demanda.
5. **Determinístico primero, IA después.** Cada hallazgo declara su origen. La IA nunca
   sube una severidad por sí sola ni cuenta para el dictamen sin confirmación humana.
6. **Trazabilidad.** Cada reporte registra el hash del código, el perfil, las versiones de
   las herramientas y de las reglas, la antigüedad de las bases y el modelo de IA.

Además, los secretos se enmascaran siempre en reportes, registros y fragmentos guardados,
y el código analizado nunca configura las herramientas (archivos `.gitleaks.toml`,
comentarios `nosec`, etcétera).

## Proponer una regla

Las reglas propias están en formato Opengrep (el de Semgrep), en
`rules/heimdall/<stack>/`, con **un archivo por regla** llamado como su ID
(`DJ-SQL-001.yaml`). El segundo tramo del ID decide la categoría: `CONF` va a
configuración, `AUTH` e `IDOR` a control de acceso y el resto a código inseguro.

Metadatos obligatorios en `metadata`:

- `cwe` y `owasp` (con la etiqueta de la edición vigente, por ejemplo
  `"A05:2025 Injection"`; las categorías están en `src/heimdall_guardian/core/owasp.py`),
- `severity_hdl` (`critical`, `high`, `medium`, `low` o `info`) y `confidence`
  (`high`, `medium` o `low`); son los códigos que se guardan,
- **los dos idiomas:** el inglés es el idioma base: el `message` propio de la regla y
  `title` y `recommendation` en `metadata`. El español va en `message_es`, `title_es` y
  `recommendation_es` (segunda persona). Una regla sin los campos en español cae al
  inglés: es un hueco, no un estilo.

Toma como modelo cualquier regla existente (por ejemplo
`rules/heimdall/django/DJ-SQL-001.yaml`). Después:

1. Crea los fixtures en `tests/rules/fixtures/<ID>/positive/` y `.../negative/`. Van ahí y
   no junto a la regla, porque el motor leería como reglas los YAML que hubiera al lado.
   El código de los fixtures es deliberadamente vulnerable y nunca se ejecuta.
2. Anota en `tests/rules/expected.yaml` cuántos hallazgos exactos da el fixture
   positivo. El negativo debe dar cero.
3. Si el CWE de la regla no tiene guía en `_HINTS` de `core/owasp.py`, considera agregar
   «Cómo verificarlo».
4. Comprueba que pasa con el motor real:

   ```bash
   HDL_REQUIRE_RULE_ENGINE=1 uv run pytest tests/rules -q
   ```

   Sin motor instalado, esas pruebas se omiten en local, pero fallan en la CI.

Una regla con muchos falsos positivos cuesta más de lo que aporta: prefiere patrones
estrechos y un fixture negativo que incluya los casos legítimos parecidos.

## Proponer un extractor de endpoints

Cada framework tiene un extractor propio en `src/heimdall_guardian/authz/` (`django.py`
con `ast`; `dotnet.py`, `laravel.py`, `php.py` y `node.py` con análisis de texto) que
devuelve el inventario de endpoints sin ejecutar nada.

1. Crea el extractor con `extract() -> list[Endpoint]` y la lista `notes` para declarar lo
   que no pudo leer, y regístralo en `authz/adapter.py`.
2. Agrega un proyecto de ejemplo en `tests/fixtures/authz_<stack>/`.
3. En `tests/unit/test_authz.py`, compara el inventario completo contra las rutas
   esperadas: el diccionario debe coincidir exactamente.
4. El texto de los hallazgos que produce el extractor va en los dos idiomas (ver abajo).

## Idioma y texto visible

Heimdall Guardian es bilingüe (inglés y español) y **el inglés es el idioma base**.

- **Todo texto visible nuevo** (interfaz, reportes, ayuda de la CLI, mensajes, textos de
  adaptadores y de la IA) va al catálogo: la clave y su texto en inglés en
  `src/heimdall_guardian/i18n/messages_en.py` (la fuente), y su traducción en
  `src/heimdall_guardian/i18n/messages_es.py`. No escribas cadenas visibles en el código, en
  ningún idioma. Léelas con `t()` (o `tn()` para plurales, con claves `.one` / `.other`).
- Las claves deben existir en ambos catálogos con los mismos marcadores. Una traducción
  faltante cae al inglés y luego a la clave.
- Lo que se guarda en la base y en el JSON son códigos neutros, no texto traducido
  (`CRÍTICA`, `NUEVO`, `likely_real`...); sus etiquetas están en el catálogo.
- Las reglas llevan los seis textos descritos arriba; los hallazgos del inventario de
  endpoints, de los adaptadores y de la IA también llevan ambos idiomas.
- Las pruebas que lo vigilan están en `tests/unit/`: `test_i18n.py` (etiquetas de los
  enumerados y catálogos), `test_i18n_messages.py` (mismas claves y marcadores en ambos
  catálogos, toda clave usada en el código existe, sin literales en español en la interfaz
  ni en los módulos revisados), `test_i18n_core.py` (reportes y mensajes guardados en
  ambos idiomas), `test_i18n_findings.py` (reglas, adaptadores, prompts y cachés de la IA en
  ambos idiomas) y `test_cli_i18n.py` (la línea de comandos). Ejecútalas con
  `uv run pytest tests/unit -q -k i18n`.
- El aviso de los autores sobre los elementos gráficos (`palette.ART_NOTICE`) es texto
  legal y se queda en español, tal cual, en el README, `NOTICE` y «Acerca de».
- El texto en español (es-MX) va en segunda persona («tú») y con verbos llanos; el texto en
  inglés es directo y también en segunda persona.

## Estilo y convenciones

- **Código:** ruff (formato y lint), mypy estricto sobre `src/` y cobertura mínima de 75 %.
  La lógica de la interfaz va en `ui/model.py` (sin Flet, con pruebas); `ui/app.py` solo
  arma controles.
- **Claves de configuración** (`config.toml`): en inglés.
- **Sitio de documentación:** las páginas de `docs/` también van en pares (`X.md` y `X.es.md`).
- **Versión y registro de cambios:** quien entrega un cambio sube la versión (en
  `pyproject.toml` y en `src/heimdall_guardian/__init__.py`) y agrega su entrada a
  `CHANGELOG.md`, en formato Keep a Changelog.
- **Documentación pública** (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `THIRD-PARTY-NOTICES.md`): está en inglés y cada una tiene su versión en español en
  `*.es.md`. Al cambiar una, actualiza la otra. `NOTICE` lleva ambos idiomas en un solo
  archivo.
- **Dependencias y herramientas de terceros:** si agregas o cambias una, actualiza
  `THIRD-PARTY-NOTICES.md` (y su `.es.md`) y, si hace falta, `licenses/`.

## Commits

Mensajes breves, con el estilo de Conventional Commits que usa el historial (escríbelos en
inglés):

```
feat: version 0.6.0, code rules and endpoint inventory for Node.js and TypeScript
fix: the Trivy database download failed from the app
docs: how to use local models with Ollama and which model to pick
chore: version 0.4.1, Trivy 0.76.0 and OSV-Scanner 2.7.0
```

Antes de enviar tu cambio, deja en verde `pre-commit run --all-files`. La plantilla del pull
request tiene la lista completa.

## Sitio de documentación y contribuidores

- El sitio de documentación (`docs/`, `mkdocs.yml`) usa MkDocs Material. Sus herramientas
  están en el grupo de dependencias `docs` (solo desarrollo; no viajan en el instalador).
  `make docs` regenera las páginas generadas y construye el sitio con verificación estricta;
  `make docs-serve` da una vista previa en vivo. `mkdocs build` por sí solo requiere haber
  corrido antes `tools/build_rule_docs.py` (si no, faltan las páginas generadas); `make docs`
  hace ambas cosas.
- El catálogo de reglas, la página de OWASP, la de stacks y (ignorada por git) la referencia
  de la línea de comandos las genera `tools/build_rule_docs.py`. Después de cambiar una regla,
  corre `make docs` y sube el resultado: `tests/unit/test_rule_docs.py` falla si `docs/rules/`
  está desactualizado.
- Agrégate a [CONTRIBUTORS.es.md](CONTRIBUTORS.es.md) y [CONTRIBUTORS.md](CONTRIBUTORS.md) en el
  mismo pull request de tu contribución.
- Se espera que todas las personas participantes sigan el
  [Código de conducta](CODE_OF_CONDUCT.es.md).

Las capturas de pantalla viven en `docs/assets/screenshots/` (una por idioma, `NN-nombre-en.png` / `-es.png`); mantén cada una en 350 KB o menos, porque el hook de pre-commit rechaza archivos de más de 512 KB.

## Mantener las dependencias al día

- `make outdated` imprime un solo reporte (no cambia nada y siempre sale con 0; `--strict`
  sale con 1 si algo está desactualizado): los paquetes de Python que declaras de forma
  directa, las herramientas fijadas en `tools/tools.toml` y los GitHub Actions de los
  workflows. Marca los saltos de versión mayor. Si no hay red, lo dice.
- `make upgrade` intenta llevar todo a las últimas versiones compatibles (`make upgrade
  PACKAGE=ruff` para una sola). Respalda `pyproject.toml` y `uv.lock`, ejecuta `uv lock
  --upgrade`, mueve los pines `flet==` de `[tool.flet.*]` al Flet bloqueado y corre
  `pre-commit run --all-files` más las pruebas de reglas y de integración. Si un paso falla
  restaura ambos archivos y muestra el final de la salida que falló; si todo pasa, lista los
  cambios de versión. Después agrega una entrada en `CHANGELOG.md`.
- Dependabot abre pull requests semanales (`.github/dependabot.yml`): uno para las
  actualizaciones menores y de parche y uno por cada versión mayor, para Python y para los
  GitHub Actions, que se fijan por SHA de commit con la versión en un comentario.
- Cuando cambian Flet o pillow, ejecuta `make app` y revisa a ojo la app y el DMG: la
  ventana, el ícono y el fondo del instalador son lo que una prueba no ve. Actualizar una
  herramienta sigue siendo editar `tools/tools.toml` (versión, URL y SHA-256 juntos).

## Generar los instaladores

`make app` (o `uv run python tools/build_app.py`) construye la aplicación de escritorio y su
instalador para el sistema donde lo ejecutas, y los deja en `dist/`. Primero corre
`tools/build_bundle.py` y luego `flet build`. Hay que construir en el sistema de destino: el
paquete lleva binarios nativos.

| Sistema | Necesitas | Salida en `dist/` |
|---|---|---|
| macOS | Flutter y Xcode | `HeimdallGuardian-<versión>-arm64.dmg` |
| Windows | Flutter, Visual Studio con "Desarrollo para el escritorio con C++" e [Inno Setup](https://jrsoftware.org/isinfo.php) 6 o 7 | `heimdall-guardian-<versión>-windows-x64-setup.exe` |
| Linux | Flutter y `sudo apt install clang cmake ninja-build pkg-config libgtk-3-dev liblzma-dev libmpv-dev libasound2-dev libsecret-1-dev python3-venv` (`dpkg-deb` para el `.deb`; `python3-venv` para que la app pueda instalar el comando `hdl`) | `heimdall-guardian-<versión>-linux-x64.tar.gz` y `heimdall-guardian_<versión>_amd64.deb` |

También puedes construir los tres sin preparar nada en local: en GitHub ve a **Actions ->
Build installers -> Run workflow**. Los archivos aparecen como artefactos de la ejecución y
caducan a los 7 días; no se publica nada como versión.

**Qué Flutter.** `flet build` necesita la versión de Flutter con la que se probó su versión de
Flet: el mismo número principal y menor (Flet 1.1.3 pide 3.47.x; un Flutter más nuevo también
se rechaza). Para ver la versión exacta, ejecuta
`uv run python -c "import flet.version as v; print(v.flutter_version)"`. Busca primero en
`~/flutter/<versión>/` (`%USERPROFILE%\flutter\<versión>\` en Windows) y luego el `flutter`
del PATH. Si ninguno sirve, muestra "Flutter SDK not found or invalid version installed" y
ofrece descargar esa versión en `~/flutter/<versión>/` (entre 1 y 2 GB, una sola vez). Esa
copia queda aparte de la tuya, así que tu Flutter y tus otros proyectos no cambian. Aceptar
la descarga es lo recomendado; por eso sugerimos `~/flutter/<versión>/` como lugar para
Flutter en todos los sistemas, en vez de las carpetas distintas que dan las guías de Flutter
y de Flet para cada sistema.

Si usas Flutter para otros proyectos: antes de que Flet pregunte, el script de construcción
muestra un aviso cuando va a ocurrir la descarga. La descarga no actualiza, no regresa de
versión ni reemplaza tu Flutter, y no cambia tu PATH, así que tus otros proyectos conservan su
versión. Lo que comparte con tu Flutter es la caché de paquetes (`~/.pub-cache`, o
`%LOCALAPPDATA%\Pub\Cache` en Windows) y la configuración de Flutter del usuario, donde Flet
solo activa el soporte de escritorio del sistema actual. Para mantener el control total,
contesta `n` y pon tú mismo un Flutter con la versión principal y menor requerida en el PATH o
en `~/flutter/<versión>/`. Los scripts de construcción omiten el resumen de `flutter doctor`
que Flet muestra tras un fallo (sus avisos sobre el PATH parecen la causa, pero no lo son) y
en su lugar dan una pista breve: el error real está en las primeras líneas rojas.

Los instaladores no están firmados, así que cada sistema avisa la primera vez:

- **macOS (Gatekeeper):** la firma es ad hoc. En **Aplicaciones**, haz clic derecho en la
  app, elige **Abrir** y confirma.
- **Windows (SmartScreen):** pulsa **Más información** y luego **Ejecutar de todas formas**.
- **Linux:** `sudo apt install ./heimdall-guardian_<versión>_amd64.deb`, o extrae el
  `.tar.gz` y ejecuta el binario dentro de su carpeta `app/`.

### Construir en Windows

Windows no trae `make`. Cada objetivo del `Makefile` solo llama a un script de Python, así
que en PowerShell ejecuta los scripts directamente con `uv run`.

Instala esto una vez y luego abre un PowerShell nuevo para que tome el PATH actualizado:

- Python 3.12 o posterior y [uv](https://docs.astral.sh/uv/):
  `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.
- Flutter, en la versión que pide Flet (ver **Qué Flutter** arriba). Puedes no instalarlo
  tú: `flet build` ofrece descargarlo la primera vez.
- Visual Studio 2022 o 2026 (basta Community) con la carga de trabajo **Desarrollo para el
  escritorio con C++**, que trae las herramientas de compilación MSVC, el SDK de Windows y
  las herramientas de CMake para C++ que necesita Flutter. Sin ellas la construcción se
  detiene con "Unable to find suitable Visual Studio toolchain"; `flutter doctor -v` dice qué
  falta.
- El **modo de desarrollador** activado (Configuración -> Sistema -> Para programadores, o
  `start ms-settings:developers`): Flutter necesita enlaces simbólicos para construir con
  plugins y se detiene con "Building with plugins requires symlink support" sin él.
- [Inno Setup](https://jrsoftware.org/isinfo.php) 6 o 7 (o `choco install innosetup`). Si
  `ISCC.exe` no está en el PATH, el script también lo busca en las carpetas `Inno Setup 7` e
  `Inno Setup 6` dentro de `C:\Program Files (x86)`, `C:\Program Files` y, si se instaló
  sin permisos de administrador, `%LOCALAPPDATA%\Programs`.

Después, desde la carpeta del repositorio:

| Objetivo de `make` | Equivalente en PowerShell |
|---|---|
| `make tools` | `uv run python tools/fetch_tools.py` |
| `make setup` | `uv run python tools/fetch_tools.py` y luego `uv sync` |
| `make app` | `uv run python tools/build_app.py` |
| `make test` | `uv run pytest --cov` |

`uv run python tools/build_app.py --dry-run` solo muestra qué script ejecutaría. En Windows,
`build_app.py` construye el wheel del CLI y luego ejecuta `tools/build_windows.py`, que
empaqueta las reglas y los binarios, ejecuta `flet build windows` y compila
`packaging/windows/heimdall-guardian.iss` con Inno Setup. El instalador queda en
`dist\heimdall-guardian-<versión>-windows-x64-setup.exe`.

Si falla:

- **"Inno Setup (ISCC.exe) was not found"**: instala Inno Setup o agrega al PATH la carpeta
  que contiene `ISCC.exe` (solo para esta sesión:
  `$env:Path += ";C:\ruta\a\Inno Setup 7"`).
- **Errores de `flet build`**: casi siempre falta Flutter o la carga de trabajo de C++ de
  Visual Studio; ejecuta `flutter doctor -v`.
- **Ruta demasiado larga**: activa las rutas largas de Windows (`LongPathsEnabled`) o clona
  el repositorio en una ruta corta, como `C:\dev\hg`.

## Publicar una versión

Las versiones se publican desde una etiqueta; `.github/workflows/release.yml` hace el resto y
deja un **borrador** que publicas a mano.

1. Sube la versión en `pyproject.toml` y `src/heimdall_guardian/__init__.py`, añade su entrada
   en `CHANGELOG.md` y ejecuta `uv lock` (el skill `release` tiene el QA completo).
2. Integra en `main`, etiqueta y sube: `git tag vX.Y.Z && git push origin vX.Y.Z`. El flujo
   falla si la etiqueta y la versión de `pyproject.toml` no coinciden.
3. El flujo corre el mismo QA que CI, construye la wheel ligera de la línea de comandos y el
   archivo para servidores, y crea un borrador de versión en GitHub con la wheel,
   `install_hdl.py`, el archivo, `SHA256SUMS` y la sección del changelog de esa versión como
   notas. Puedes ver las notas antes con `uv run python tools/changelog_section.py X.Y.Z`.
4. Revisa el borrador. Construye los instaladores de escritorio (Actions -> Build installers),
   pruébalos en equipos reales y adjúntalos tú al borrador: nunca se adjuntan automáticamente.
5. Publica la versión.

**Opcional: PyPI.** El job `pypi` usa publicación de confianza (sin guardar tokens) y solo
corre si la variable del repositorio `PUBLISH_PYPI` vale `true`. Configuración única: en
pypi.org crea el proyecto `heimdall-guardian` (o un "pending publisher"), añade un publicador
de confianza con este repositorio de GitHub, el flujo `release.yml` y el entorno `pypi`, crea
el entorno `pypi` en los ajustes del repositorio (conviene exigir un revisor) y define la
variable. Solo se sube la wheel ligera; no hay sdist porque no llevaría el `_bundle/` generado.

## Vulnerabilidades en Heimdall Guardian

No abras un issue público: sigue [SECURITY.es.md](SECURITY.es.md) ([in English](SECURITY.md)).
