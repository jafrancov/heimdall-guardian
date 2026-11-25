# Third-party components

[Leer en español → THIRD-PARTY-NOTICES.es.md](THIRD-PARTY-NOTICES.es.md)

Heimdall Guardian orchestrates tools from other projects. It does not modify them.

## Executables shipped with the installer

Exact versions and SHA-256 hashes are pinned in [`tools/tools.toml`](tools/tools.toml);
`tools/fetch_tools.py` downloads them from the official releases and verifies the hash.

| Tool | Version | License | Source code |
|---|---|---|---|
| Opengrep | 2.1.0 | LGPL-2.1 ([text](licenses/LGPL-2.1.txt)) | https://github.com/opengrep/opengrep |
| Gitleaks | 8.30.1 | MIT ([text](licenses/MIT-gitleaks.txt)) | https://github.com/gitleaks/gitleaks |
| Trivy | 0.76.2 | Apache-2.0 ([text](LICENSE)) | https://github.com/aquasecurity/trivy |
| OSV-Scanner | 2.7.1 | Apache-2.0 ([text](LICENSE)) | https://github.com/google/osv-scanner |

**Opengrep (LGPL-2.1).** It is included as a standalone executable, as published by its
project, and Heimdall Guardian invokes it as a separate process. You can replace it with
another version or one you built yourself: set `HDL_OPENGREP_BIN` to its path. The source
code corresponding to the included version is at the `v2.0.0` tag of its repository.

## Python libraries

They are installed as dependencies; each keeps its own license.

| Library | License | What it is used for |
|---|---|---|
| Bandit | Apache-2.0 | Python code analysis |
| Flet | Apache-2.0 | Desktop interface |
| Pydantic | MIT | Validating the output of the AI models |
| PyYAML | MIT | Reading your own rules |
| Jinja2 | BSD-3-Clause | HTML report |
| openpyxl | MIT | Excel report |
| fpdf2 | LGPL-3.0 ([text](licenses/LGPL-3.0.txt), which refers to the [GPL-3.0](licenses/GPL-3.0.txt)) | PDF report |
| keyring | MIT | AI destination token in the system keychain |

The desktop application is built with Flet, which bundles the Flutter engine and framework
(BSD-3-Clause) and their transitive dependencies. Each keeps its own license; see the notices
that Flet and Flutter publish (<https://github.com/flet-dev/flet>,
<https://github.com/flutter/flutter>) and the licenses screen of the built application.

## Vulnerability databases

They are not distributed with the project. Trivy and OSV-Scanner download them from their
sources (Aqua Security and OSV.dev) when `--update-databases` is used, under the terms of
each source.

## Rules

The rules in `rules/heimdall/` are this project's own and are published under the same
license. They use the Semgrep/Opengrep rule format, but do not copy rules from their
registries.

## Ideas taken from other projects

The preview mode, additive exclusions and consensus between models are inspired by
[`daniel-rrapi/heimdall`](https://github.com/daniel-rrapi/heimdall) (MIT). No code was
copied from that project.

## Graphic elements

The notice below is the author's legal text and is kept in Spanish, as written:

Los elementos gráficos de HEIMDALL fueron desarrollados mediante un proceso creativo
asistido por herramientas de inteligencia artificial, con decisiones de selección,
adaptación y definición de identidad realizadas durante el desarrollo del proyecto. Su
utilización y protección estarán sujetas a los derechos efectivamente reconocidos por la
legislación aplicable.

*Courtesy translation, with no legal value of its own:* The graphic elements of HEIMDALL
were developed through a creative process assisted by artificial intelligence tools, with
selection, adaptation and identity-definition decisions made during the development of the
project. Their use and protection will be subject to the rights effectively recognized by
the applicable law.
