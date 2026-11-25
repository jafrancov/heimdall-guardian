# Componentes de terceros

[Read in English → THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)

Heimdall Guardian orquesta herramientas de otros proyectos. No las modifica.

## Ejecutables que se distribuyen con el instalador

Las versiones y los SHA-256 exactos están fijados en [`tools/tools.toml`](tools/tools.toml);
`tools/fetch_tools.py` los descarga de las publicaciones oficiales y verifica el hash.

| Herramienta | Versión | Licencia | Código fuente |
|---|---|---|---|
| Opengrep | 2.1.0 | LGPL-2.1 ([texto](licenses/LGPL-2.1.txt)) | https://github.com/opengrep/opengrep |
| Gitleaks | 8.30.1 | MIT ([texto](licenses/MIT-gitleaks.txt)) | https://github.com/gitleaks/gitleaks |
| Trivy | 0.76.2 | Apache-2.0 ([texto](LICENSE)) | https://github.com/aquasecurity/trivy |
| OSV-Scanner | 2.7.1 | Apache-2.0 ([texto](LICENSE)) | https://github.com/google/osv-scanner |

**Opengrep (LGPL-2.1).** Se incluye como ejecutable independiente, tal como lo publica
su proyecto, y Heimdall Guardian lo invoca como un proceso aparte. Puedes sustituirlo
por otra versión o por una compilada por ti: define `HDL_OPENGREP_BIN` con su ruta. El
código fuente correspondiente a la versión incluida está en la etiqueta `v2.0.0` de su
repositorio.

## Bibliotecas de Python

Se instalan como dependencias; cada una conserva su licencia.

| Biblioteca | Licencia | Para qué se usa |
|---|---|---|
| Bandit | Apache-2.0 | Análisis de código Python |
| Flet | Apache-2.0 | Interfaz de escritorio |
| Pydantic | MIT | Validación de la salida de los modelos de IA |
| PyYAML | MIT | Leer tus propias reglas |
| Jinja2 | BSD-3-Clause | Reporte HTML |
| openpyxl | MIT | Reporte Excel |
| fpdf2 | LGPL-3.0 ([texto](licenses/LGPL-3.0.txt), que remite a la [GPL-3.0](licenses/GPL-3.0.txt)) | Reporte PDF |
| keyring | MIT | Token del destino de IA en el llavero del sistema |

La aplicación de escritorio se construye con Flet, que incluye el motor y el framework de
Flutter (BSD-3-Clause) y sus dependencias transitivas. Cada una conserva su licencia; consulta
los avisos que publican Flet y Flutter (<https://github.com/flet-dev/flet>,
<https://github.com/flutter/flutter>) y la pantalla de licencias de la aplicación construida.

## Bases de datos de vulnerabilidades

No se distribuyen con el proyecto. Trivy y OSV-Scanner las descargan de sus fuentes
(Aqua Security y OSV.dev) cuando se usa `--update-databases` (o `--actualizar-bases`), bajo los términos de cada
fuente.

## Reglas

Las reglas de `rules/heimdall/` son propias de este proyecto y se publican con su misma
licencia. Usan el formato de reglas de Semgrep/Opengrep, pero no copian reglas de sus
registros.

## Ideas tomadas de otros proyectos

El modo de vista previa, las exclusiones aditivas y el consenso entre modelos se
inspiran en [`daniel-rrapi/heimdall`](https://github.com/daniel-rrapi/heimdall) (MIT).
No se copió código de ese proyecto.

## Elementos gráficos

Los elementos gráficos de HEIMDALL fueron desarrollados mediante un proceso creativo
asistido por herramientas de inteligencia artificial, con decisiones de selección,
adaptación y definición de identidad realizadas durante el desarrollo del proyecto. Su
utilización y protección estarán sujetas a los derechos efectivamente reconocidos por la
legislación aplicable.
