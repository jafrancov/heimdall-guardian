"""Builds the command-line-only archive for servers without a desktop.

Usage:  python tools/build_cli_archive.py      (or `make cli-archive`, which builds the wheel first)

Writes `dist/heimdall-guardian-cli-<version>.tar.gz` with `install_hdl.py`, the light CLI wheel
from `dist/cli/` and a short README in English and Spanish. The Linux build calls the same
function; it works on any operating system.
"""

from __future__ import annotations

import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DIST = REPO / "dist"
CLI_WHEELS = DIST / "cli"
SCRIPT = REPO / "packaging" / "cli" / "install_hdl.py"
NAME = "heimdall-guardian-cli"

README = """\
Heimdall Guardian - command line only {version}
==============================================

English
-------
This archive installs the `hdl` command on a machine without the desktop app. You need
Python 3.12 or newer (https://www.python.org/downloads/); on Debian and Ubuntu also
`sudo apt install python3-venv`.

    python3 install_hdl.py --wheel {wheel}   # own virtual environment; links `hdl`
    hdl tools --install                      # downloads the analysis tools
    hdl databases --update                   # vulnerability databases
    hdl scan <folder> --profile standard --output report.html

Without --wheel the script installs the latest release from PyPI. To remove it:

    python3 install_hdl.py --uninstall       # databases, history and settings stay

Español (es-MX)
---------------
Este archivo instala el comando `hdl` en un equipo sin la app de escritorio. Necesitas
Python 3.12 o más nuevo (https://www.python.org/downloads/); en Debian y Ubuntu también
`sudo apt install python3-venv`.

    python3 install_hdl.py --wheel {wheel}   # entorno virtual propio; enlaza `hdl`
    hdl tools --install                      # descarga las herramientas de análisis
    hdl databases --update                   # bases de datos de vulnerabilidades
    hdl scan <carpeta> --profile standard --output reporte.html

Sin --wheel el script instala la última version de PyPI. Para quitarlo:

    python3 install_hdl.py --uninstall       # bases, historial y ajustes se quedan
"""


def project_version() -> str:
    data = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def archive_members(version: str, wheel: Path, script: Path = SCRIPT) -> dict[str, Path | None]:
    """Archive name -> source file (`None` for the generated README), in archive order."""
    root = f"{NAME}-{version}"
    return {
        f"{root}/install_hdl.py": script,
        f"{root}/{wheel.name}": wheel,
        f"{root}/README.txt": None,
    }


def make_cli_archive(
    version: str, wheel: Path, *, output: Path = DIST, script: Path = SCRIPT
) -> Path:
    """Writes the archive in `output` and returns its path."""
    if not wheel.is_file():
        raise FileNotFoundError(f"{wheel}: build it first with tools/build_cli_wheel.py")
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{NAME}-{version}.tar.gz"
    readme = README.format(version=version, wheel=wheel.name)
    with tempfile.TemporaryDirectory(prefix="heimdall-cli-") as tmp:
        readme_file = Path(tmp) / "README.txt"
        readme_file.write_text(readme, encoding="utf-8")

        def plain(info: tarfile.TarInfo) -> tarfile.TarInfo:
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if info.name.endswith(".py") else 0o644
            return info

        with tarfile.open(archive, "w:gz") as tar:
            for name, source in archive_members(version, wheel, script).items():
                tar.add(readme_file if source is None else source, arcname=name, filter=plain)
    return archive


def main() -> int:
    version = project_version()
    wheel = CLI_WHEELS / f"heimdall_guardian-{version}-py3-none-any.whl"
    try:
        archive = make_cli_archive(version, wheel)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"{archive.relative_to(REPO)}  {archive.stat().st_size / 1_048_576:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
