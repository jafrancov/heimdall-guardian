"""Mensajes visibles, español (traducción del inglés de `messages_en`)."""

from __future__ import annotations

MESSAGES: dict[str, str] = {
    "lang.error.unsupported": "Idioma no soportado: {value}. Opciones: {options}.",
    "core.ai.progress": "revisando {done} de {total}",
    "cli.description": (
        "Heimdall Guardian: análisis estático de seguridad de código, local y de solo lectura."
    ),
    "cli.help.help": "muestra esta ayuda y termina",
    "cli.help.version": "muestra la versión y termina",
    "cli.metavar.folder": "carpeta",
    "cli.metavar.name": "NOMBRE",
    "cli.metavar.folder_upper": "CARPETA",
    "cli.metavar.date": "AAAA-MM-DD",
    "cli.metavar.file_json": "ARCHIVO.json",
    "cli.metavar.file_targz": "ARCHIVO.tar.gz",
    "cli.arg.folder": "carpeta del proyecto (nunca se modifica)",
    "cli.arg.output": (
        "archivo de salida; el formato sale de la extensión ({formats}). Se puede repetir. Sin "
        "esta opción, JSON por la salida estándar"
    ),
    "cli.scan.help": "analiza una carpeta y genera el reporte",
    "cli.scan.profile": (
        "perfil de análisis: rapido, estandar, completo, proveedor o personalizado (por defecto: "
        "el de la configuración, o estandar)"
    ),
    "cli.scan.modules": "módulos del perfil personalizado, separados por comas: {modules}",
    "cli.scan.dry_run": "lista qué se analizaría, sin ejecutar ninguna herramienta",
    "cli.scan.update_databases": (
        "permite descargar las bases de vulnerabilidades antes de analizar"
    ),
    "cli.scan.exclude": (
        "carpeta, archivo o patrón de archivo que no se analiza en esta corrida (se puede "
        "repetir), "
        "p. ej. build, src/vendor/grande.js o '*.spec.ts'"
    ),
    "cli.scan.exclude_gitignored": (
        "omite también, en esta corrida, lo que git ignora en la carpeta (sin git, lo que el "
        ".gitignore de la raíz lista por nombre simple)"
    ),
    "cli.scan.include": "carpeta que sí se analiza aunque se omita por defecto (se puede repetir)",
    "cli.scan.ai": "configuración de IA que se usa en este análisis (por defecto: la activa)",
    "cli.scan.issuer": (
        "quién emite el dictamen (perfil proveedor); por defecto, el usuario del sistema"
    ),
    "cli.scan.no_baseline": "no compara con corridas anteriores ni guarda esta corrida",
    "cli.report.help": "regenera reportes de una corrida guardada",
    "cli.report.run": "número de corrida (por defecto: la última)",
    "cli.runs.help": "lista las corridas guardadas del proyecto",
    "cli.forget.help": "borra el historial de un proyecto (no toca su carpeta)",
    "cli.forget.yes": "confirma el borrado",
    "cli.suppress.help": "acepta el riesgo de un hallazgo o lo marca como falso positivo",
    "cli.suppress.id": "ID del hallazgo, p. ej. HDL-2026-000012",
    "cli.suppress.status": "aceptado o falso-positivo",
    "cli.suppress.reason": "justificación (obligatoria)",
    "cli.suppress.review": "fecha de revisión; al vencer, el hallazgo vuelve a contar",
    "cli.suppress.author": "quién decide (por defecto: el usuario del sistema)",
    "cli.unsuppress.help": "retira la supresión de un hallazgo",
    "cli.unsuppress.id": "ID del hallazgo",
    "cli.suppressions.help": "lista las supresiones vigentes",
    "cli.tools.help": "muestra las herramientas disponibles y su versión",
    "cli.tools.news": "consulta en internet si hay versiones más nuevas (no descarga nada)",
    "cli.thresholds.help": "consulta o cambia los umbrales del dictamen (requiere PIN)",
    "cli.thresholds.set_pin": "define o cambia el PIN",
    "cli.thresholds.log": "muestra los cambios hechos",
    "cli.thresholds.count_ai": "si las sugerencias de IA cuentan para el dictamen (si o no)",
    "cli.baseline.help": "exporta o importa la línea base del proyecto (hallazgos y supresiones)",
    "cli.baseline.export": "escribe la línea base en un archivo",
    "cli.baseline.import": "incorpora la línea base de un archivo",
    "cli.databases.help": "estado de las bases de vulnerabilidades; exportarlas o importarlas",
    "cli.databases.update": "descarga o actualiza las bases ahora",
    "cli.databases.export": "empaqueta las bases en un archivo",
    "cli.databases.import": "carga las bases desde un archivo",
    "cli.llm.help": "prueba la conexión con los destinos de IA",
    "cli.llm.destination": "nombre del destino (por defecto: el activo)",
    "cli.llm.save_token": "pide el token del destino y lo guarda en el llavero del sistema",
    "cli.ui.help": "abre la interfaz de escritorio",
    "cli.ui.web": "la sirve en un puerto local",
    "cli.ui.port": "puerto de --web (por defecto: uno libre)",
    "cli.config.help": "muestra dónde está la configuración",
    "cli.config.init": "crea el archivo si no existe",
    "cli.error": "Error: {error}",
    "cli.error.not_folder": "No es una carpeta: {path}",
    "cli.error.output_inside": "{option} no puede estar dentro de la carpeta analizada.",
    "cli.error.format": "Formato no soportado: {name}. Extensiones: {formats}.",
    "cli.error.modules_need_custom": "{modules} solo aplica con {profile} personalizado.",
    "cli.error.bad_profile": "Perfil desconocido: {value}. Opciones: {valid}.",
    "cli.error.bad_status": "Estado desconocido: {value}. Opciones: {valid}.",
    "cli.error.bad_yes_no": "Se esperaba si o no, no {value}.",
    "cli.plan.folder": "Carpeta:  {path}",
    "cli.plan.stack": "Stack:    {stacks}",
    "cli.plan.stack_none": "ninguno detectado",
    "cli.plan.profile": "Perfil:   {profile} ({modules})",
    "cli.plan.no_modules": "sin módulos",
    "cli.plan.pending": "          aún no disponibles: {modules}",
    "cli.plan.files": "Archivos: {count}",
    "cli.plan.gitignored": "Ignorado y omitido en esta corrida: {count} entradas ({source})",
    "cli.plan.gitignored_source.git": "git",
    "cli.plan.gitignored_source.gitignore": ".gitignore",
    "cli.plan.subprojects": "Esta carpeta tiene {count} proyectos: {names}.",
    "cli.plan.subprojects_hint": "Para analizar uno por separado: hdl scan {example}",
    "cli.plan.suggested": "Sugerida para omitir: {pattern} ({reason}), p. ej. {example}",
    "cli.plan.suggested_hint": (
        'Agrégalas con --exclude NOMBRE, o en la app en "Carpetas a omitir".'
    ),
    "core.presets.reason.stack": "Habitual en proyectos {stack}",
    "core.presets.reason.tool": "Carpeta de editor o asistente de IA",
    "core.presets.reason.gitignore": "Aparece en el .gitignore del proyecto",
    "cli.report.written": "Reporte:  {path}",
    "cli.summary.tool_line": "{name:<9} {status:<9} {count:>4} hallazgo(s)",
    "cli.summary.open": "Abiertos: {counts}",
    "cli.summary.run": "Corrida {run}: {counts}",
    "cli.summary.limitation": "Limitación: {text}",
    "cli.summary.verdict": "Dictamen: {outcome}",
    "cli.summary.criterion": "  {name}: {found} (máximo {limit}) {mark}",
    "cli.summary.exceeded": "REBASADO",
    "cli.summary.met": "cumple",
    "cli.progress.ai": "  IA: {status}",
    "cli.forget.confirm": (
        "Esto borra los análisis, la línea base y los riesgos aceptados del proyecto. Repite el "
        "comando con {option} para confirmar."
    ),
    "cli.forget.none": "Ese proyecto no tiene historial guardado.",
    "cli.forget.done": "Historial del proyecto borrado. La carpeta del proyecto no se modificó.",
    "cli.runs.none": "No hay corridas guardadas para este proyecto.",
    "cli.runs.counts": "(nuevos {new}, corregidos {fixed})",
    "cli.suppress.done": "{id}: {status}. Ya se refleja en la última corrida y en sus reportes.",
    "cli.unsuppress.done": "{id}: supresión retirada.",
    "cli.unsuppress.none": "{id} no tenía una supresión vigente.",
    "cli.suppressions.none": "No hay supresiones vigentes.",
    "cli.suppressions.review": ", revisar el {date}",
    "cli.tools.unknown_version": "versión desconocida",
    "cli.tools.not_installed": "no instalado",
    "cli.tools.database": "  (base: {date})",
    "cli.tools.install": (
        "descarga las herramientas fijadas (verificadas con SHA-256) en la carpeta de datos"
    ),
    "cli.tools.missing": (
        "\nFaltan herramientas: {names}.\nEjecuta `hdl tools --install` para descargarlas "
        "(unos 150 MB), o copia la carpeta de herramientas desde un equipo que tenga la app "
        "Heimdall Guardian."
    ),
    "cli.tools.install_no_manifest": ("Esta instalación no trae la lista de herramientas fijadas."),
    "cli.tools.install_no_platform": (
        "No hay herramientas fijadas para este sistema ({platform})."
    ),
    "cli.tools.install_start": "Instalando las herramientas en {path}",
    "cli.tools.install_downloaded": (
        "{name} {version}: descargada ({transferred}) e instalada ({size})"
    ),
    "cli.tools.install_present": "{name} {version}: ya estaba instalada ({size})",
    "cli.tools.install_done": ("Listo: {count} descargadas, {total} en total, en {path}"),
    "cli.tools.install_failed": (
        "No se pudieron instalar las herramientas: {error}\nSin internet, copia la carpeta "
        "{path} desde un equipo con la app Heimdall Guardian."
    ),
    "cli.ui.no_flet": (
        "La interfaz de escritorio no está instalada aquí. Instala la app Heimdall Guardian "
        'o agrégala a este comando con `pip install "heimdall-guardian[ui]"`.'
    ),
    "tools.install.only_https": "Solo se descargan URL https: {url}",
    "tools.install.no_member": "{member} no es un archivo dentro del paquete",
    "tools.install.unsafe_member": "{member} no es un nombre de archivo seguro dentro del paquete",
    "tools.install.hash_mismatch": (
        "{name} {version}: el SHA-256 no coincide; no se instala.\n"
        "  esperado: {expected}\n  obtenido: {actual}"
    ),
    "cli.tools.news_header": (
        "\nVersiones publicadas (consulta GitHub y PyPI; no envía nada de tu código):"
    ),
    "cli.tools.news_notes": "\nNotas de cada versión:",
    "cli.tools.news_pinned": (
        "\nCada herramienta va fijada con versión y SHA-256 para que el análisis sea "
        "reproducible, así que no se actualiza sola. Si usas el instalador, llegan con la "
        "siguiente versión de Heimdall Guardian. Si lo compilas tú: cambia versión, URL y hash en "
        "tools/tools.toml, corre las pruebas de integración y genera el instalador."
    ),
    "cli.llm.no_destination": "No existe el destino de IA {name} en la configuración.",
    "cli.llm.token_prompt": "Token de {name}: ",
    "cli.llm.token_saved": "Token de {name} guardado en el llavero del sistema.",
    "cli.llm.destination_line": "Destino:  {name} ({runtime}) {url}",
    "cli.llm.state_offline": "Estado:   sin conexión ({error})",
    "cli.llm.state_online": "Estado:   conectado, {count} modelo(s) disponibles",
    "cli.llm.model_line": "Modelo de {task}: {note}",
    "cli.llm.model_unset": "sin configurar",
    "cli.llm.model_missing": "  (no está entre los modelos del destino)",
    "cli.llm.test_system": "Responde en español, en una frase.",
    "cli.llm.test_user": "Di «conexión correcta».",
    "cli.llm.test_failed": "Prueba:   falló ({error})",
    "cli.llm.test_ok": "Prueba:   {text} en {seconds:.1f} s ({speed:.0f} tokens/s)",
    "cli.config.created": "Configuración creada: {path}",
    "cli.config.missing": "{path}  (no existe; se usan los valores por defecto)",
    "cli.config.exists": "{path}",
    "cli.thresholds.pin_current": "PIN actual: ",
    "cli.thresholds.pin_new": "PIN nuevo: ",
    "cli.thresholds.pin_repeat": "Repita el PIN nuevo: ",
    "cli.thresholds.pin_prompt": "PIN: ",
    "cli.thresholds.pin_saved": "PIN guardado.",
    "cli.thresholds.updated": "Umbrales actualizados; el cambio quedó en la bitácora.",
    "cli.thresholds.default": "  (propuesta: {value})",
    "cli.baseline.need_option": "Indique {export} o {import_}.",
    "cli.baseline.imported": "Importado: {findings} hallazgos y {suppressions} supresiones nuevas.",
    "cli.baseline.inside": "La línea base no se exporta dentro de la carpeta analizada.",
    "cli.baseline.exported": "Exportados {count} hallazgos a {path}.",
    "cli.databases.imported": "Bases importadas: {count} archivos.",
    "cli.databases.exported": "Bases exportadas a {path}: {count} archivos.",
    "cli.databases.location": "Ubicación: {path}",
    "cli.databases.dated": "{name:<9} base del {date}",
    "cli.lang.help": (
        "idioma de la interfaz: en o es (tiene prioridad sobre HDL_LANG y config.toml)"
    ),
    "lang.name.en": "Inglés",
    "lang.name.es": "Español",
    "config.notice.old_version": (
        "Tu archivo de configuración es de una versión anterior y no "
        "se cargó: {path}. Se usan los valores por defecto; renombra o "
        "borra el archivo y vuelve a guardar la configuración."
    ),
    "ui.window.title": "Heimdall Guardian",
    "ui.brand.tagline": "El guardián de tu código",
    "ui.brand.motto": "Vigilancia y prevención",
    "ui.brand.home_tip": "Volver a la bienvenida",
    "ui.nav.new_analysis": "Nuevo análisis",
    "ui.nav.new_analysis_tip": "Volver a la bienvenida (⌘N o Ctrl+N)",
    "ui.nav.coverage": "Qué revisa",
    "ui.nav.coverage_tip": "Las categorías de OWASP y qué cubre Heimdall Guardian",
    "ui.nav.settings": "Configuración",
    "ui.nav.settings_tip": "Configuración",
    "ui.nav.about": "Acerca de",
    "ui.nav.about_tip": "Acerca de Heimdall Guardian",
    "ui.common.cancel": "Cancelar",
    "ui.common.close": "Cerrar",
    "ui.common.save": "Guardar",
    "ui.question.depth": "Qué tan a fondo",
    "ui.question.which_folder": "¿Qué carpeta revisamos?",
    "ui.question.local_note": "Se analiza en este equipo. No se modifica ni se ejecuta.",
    "ui.question.no_stack": "sin stack reconocido",
    "ui.question.files_stacks": "{count} archivos · {stacks}",
    "ui.action.analyze": "Analizar",
    "ui.action.choose_folder": "Elegir carpeta",
    "ui.action.change_folder": "Cambiar carpeta",
    "ui.action.preview": "Vista previa",
    "ui.subprojects.title.one": "Esta carpeta tiene {count} proyecto",
    "ui.subprojects.title.other": "Esta carpeta tiene {count} proyectos",
    "ui.subprojects.help": "Analízala completa, o abre uno para analizarlo por separado.",
    "ui.subprojects.open_tip": "Abrir {name} como proyecto aparte",
    "ui.action.skip_folders": "Carpetas a omitir",
    "ui.action.skip_folders_suggested.one": "Carpetas a omitir ({count} sugerida)",
    "ui.action.skip_folders_suggested.other": "Carpetas a omitir ({count} sugeridas)",
    "ui.action.update_bases_on_scan": "Actualizar las bases al analizar",
    "ui.action.update_bases_now": "Actualizar las bases ahora",
    "ui.bases.downloading": "Descargando las bases…",
    "ui.bases.none": ("Aún no hay bases de vulnerabilidades: se descargan (alrededor de 2 GB)."),
    "ui.bases.updated_today": "Bases de vulnerabilidades actualizadas hoy.",
    "ui.bases.updated_ago.one": "Bases de vulnerabilidades actualizadas hace {count} día.",
    "ui.bases.updated_ago.other": "Bases de vulnerabilidades actualizadas hace {count} días.",
    "ui.bases.partial_failure": "No se actualizaron todas las bases. {detail}",
    "ui.bases.updated": "Bases de vulnerabilidades actualizadas.",
    "ui.ai.time_warning": (
        "Con IA el análisis puede tardar varios minutos: depende del "
        "modelo y de la capacidad de tu equipo."
    ),
    "ui.ai.choice_label": "IA para este análisis",
    "ui.custom.issuer": "Quién emite el dictamen",
    "ui.profile.steps": "Revisa: {steps}",
    "ui.profile.verdict_step": "Dictamen",
    "ui.profile.quick.name": "Rápido",
    "ui.profile.quick.desc": "Secretos, dependencias y configuración. Menos de 2 minutos.",
    "ui.profile.standard.name": "Estándar",
    "ui.profile.standard.desc": "Antes de liberar: agrega código inseguro y control de acceso.",
    "ui.profile.full.name": "Completo",
    "ui.profile.full.desc": "Auditoría: agrega historial de git y revisión con IA.",
    "ui.profile.vendor.name": "Entrega de proveedor",
    "ui.profile.vendor.desc": "Recepción de código de terceros, con dictamen.",
    "ui.profile.custom.name": "Personalizado",
    "ui.profile.custom.desc": "Tú eliges qué se revisa.",
    "ui.module.sec": "Secretos",
    "ui.module.sec_h": "Historial de git",
    "ui.module.dep": "Dependencias",
    "ui.module.conf": "Configuración",
    "ui.module.sast": "Código inseguro",
    "ui.module.authz": "Control de acceso",
    "ui.module.ai": "Revisión con IA",
    "ui.module.sbom": "Inventario (SBOM)",
    "ui.tool.gitleaks": "Secretos",
    "ui.tool.trivy": "Dependencias y configuración",
    "ui.tool.osv": "Dependencias (segunda fuente)",
    "ui.tool.vendored": "Bibliotecas copiadas",
    "ui.tool.opengrep": "Reglas de código propias",
    "ui.tool.opengrep_for": "Código {names} (reglas propias)",
    "ui.list.and": "{first} y {last}",
    "ui.tool.bandit": "Código Python",
    "ui.tool.authz": "Inventario de endpoints",
    "ui.tool.llm": "Revisión con IA",
    "ui.tool.summary": "Resumen ejecutivo con IA",
    "ui.tool.result": "Guardando el resultado",
    "ui.tool.unknown_version": "versión desconocida",
    "ui.tool.database": "{detail}, base del {date}",
    "ui.tool.not_installed": "no instalada",
    "ui.home.not_analyzed": "{name} aún no se ha analizado.",
    "ui.home.not_analyzed_hint": (
        "Elige qué tan a fondo y presiona Analizar. Con «Vista previa» "
        "ves qué archivos entran, sin ejecutar nada."
    ),
    "ui.home.path_hint": "o pega aquí la ruta de la carpeta",
    "ui.home.check.sec": "Contraseñas, llaves y tokens, también en el historial.",
    "ui.home.check.dep": "Librerías con fallas conocidas.",
    "ui.home.check.sast": "Inyección, XSS, comandos, criptografía débil.",
    "ui.home.check.authz": "Páginas y endpoints sin autenticación.",
    "ui.home.title": "Elige una carpeta y te digo qué tan seguro está su código.",
    "ui.home.subtitle": (
        "Dónde está cada problema, por qué importa y cómo corregirlo. "
        "Todo se analiza en este equipo: no se modifica ni se ejecuta "
        "nada."
    ),
    "ui.home.no_projects": "Aún no has revisado ningún proyecto.",
    "ui.home.watch_critical.one": (
        "Vigilas {count} proyecto; {critical} con problemas críticos abiertos."
    ),
    "ui.home.watch_critical.other": (
        "Vigilas {count} proyectos; {critical} con problemas críticos abiertos."
    ),
    "ui.home.watch_clear.one": (
        "Vigilas {count} proyecto; ninguno con problemas críticos abiertos."
    ),
    "ui.home.watch_clear.other": (
        "Vigilas {count} proyectos; ninguno con problemas críticos abiertos."
    ),
    "ui.recent.title": "Análisis recientes",
    "ui.recent.remove_tip": "Quitar del historial",
    "ui.recent.forget_title": "¿Quitar {name} del historial?",
    "ui.recent.forget_body": (
        "Se borran sus análisis guardados, su línea base y los riesgos "
        "aceptados o descartados. Los reportes que ya guardaste y la "
        "carpeta del proyecto no se tocan."
    ),
    "ui.recent.forget_irreversible": "No se puede deshacer.",
    "ui.recent.forgotten": "{name} se quitó del historial.",
    "ui.picker.choose": "Carpeta a analizar",
    "ui.scan.running": "Analizando {name}",
    "ui.scan.keep_working": "Puedes seguir trabajando; la carpeta no se toca.",
    "ui.scan.busy": "Hay un análisis en curso. Cancélalo antes de empezar otro.",
    "ui.scan.cancel_notice": (
        "Se cancela al terminar la herramienta o la consulta de IA en curso."
    ),
    "ui.scan.status.start": "analizando…",
    "ui.scan.status.done": "listo",
    "ui.scan.status.skipped": "no disponible",
    "ui.scan.status.error": "falló; se continúa sin ella",
    "ui.scan.status.in_progress": "en curso…",
    "ui.scan.cancelled": "Análisis cancelado. No se guardó nada.",
    "ui.scan.failed": "No se pudo completar el análisis: {error}",
    "ui.result.save_report": "Guardar reporte:",
    "ui.result.endpoints": "{count} endpoints, {open} sin autenticación",
    "ui.result.how": "Cómo se analizó",
    "ui.result.limitations.one": "{count} limitación de esta corrida",
    "ui.result.limitations.other": "{count} limitaciones de esta corrida",
    "ui.result.context": "{comparison} Analizado el {date} con el perfil {profile}.",
    "ui.result.search_hint": "Buscar por archivo, regla o texto",
    "ui.result.ai_summary": "Resumen redactado por IA ({model})",
    "ui.result.hide_suppressed": "Ocultar los {count} aceptados o descartados",
    "ui.result.show_suppressed": "Ver los {count} aceptados o descartados",
    "ui.result.stratum_tip": "Ver solo estos; otro clic los muestra todos",
    "ui.result.no_open": "Sin hallazgos abiertos",
    "ui.result.nothing_matches": "Nada coincide con lo que buscas.",
    "ui.severity_name.critical.one": "crítico",
    "ui.severity_name.critical.other": "críticos",
    "ui.severity_name.high.one": "alto",
    "ui.severity_name.high.other": "altos",
    "ui.severity_name.medium.one": "medio",
    "ui.severity_name.medium.other": "medios",
    "ui.severity_name.low.one": "bajo",
    "ui.severity_name.low.other": "bajos",
    "ui.severity_name.info.one": "informativo",
    "ui.severity_name.info.other": "informativos",
    "ui.verdict.critical.headline": "Todavía no está listo para liberarse.",
    "ui.verdict.critical.why": "Hay {critical}.",
    "ui.verdict.critical.why_high": "Hay {critical} y {high}.",
    "ui.verdict.high.headline": "Se puede corregir pronto, pero no hoy.",
    "ui.verdict.high.why": "No hay críticos; quedan {high} por atender.",
    "ui.verdict.rest.headline": "Sin problemas graves.",
    "ui.verdict.rest.why": "Quedan {count} de menor severidad para revisar con calma.",
    "ui.verdict.clean.headline": "No se encontró nada que corregir.",
    "ui.verdict.clean.why": ("Este análisis es estático: no sustituye una prueba de penetración."),
    "ui.delivery.not_approved": "La entrega no se puede recibir.",
    "ui.delivery.approved_with_observations": "La entrega se recibe con observaciones.",
    "ui.delivery.approved": "La entrega se puede recibir.",
    "ui.delivery.exceeds": "Rebasa: {criteria}.",
    "ui.delivery.criterion": "{name} ({found}, máximo {maximum})",
    "ui.delivery.mediums": "Quedan {count} hallazgos medios con compromiso de corrección.",
    "ui.delivery.within": "No rebasa ningún umbral del dictamen.",
    "ui.compare.first": "Primera corrida de este proyecto.",
    "ui.compare.since": "Desde la corrida {previous}: {parts}.",
    "ui.compare.new": "{count} nuevos",
    "ui.compare.fixed": "{count} corregidos",
    "ui.compare.persistent": "{count} siguen igual",
    "ui.compare.accepted": "{count} aceptados o descartados",
    "ui.finding.ai_suggestion": "sugerencia de IA · {state}",
    "ui.finding.what": "Qué pasa",
    "ui.finding.how_fix": "Cómo corregirlo",
    "ui.finding.classification": "Clasificación",
    "ui.finding.model": "Modelo: {model}",
    "ui.finding.accept": "Aceptar el riesgo",
    "ui.finding.false_positive": "Es un falso positivo",
    "ui.finding.recount": "Volver a contarlo",
    "ui.finding.recounted": "{id} vuelve a contar.",
    "ui.finding.saved": "{id} guardado. El resultado y los reportes ya lo reflejan.",
    "ui.finding.reason": "Justificación (obligatoria)",
    "ui.finding.review_date": "Revisar de nuevo el (AAAA-MM-DD, opcional)",
    "ui.finding.mark_false_positive": "Marcar como falso positivo",
    "ui.finding.unknown_user": "desconocido",
    "ui.expert.title": "Para expertos",
    "ui.expert.subtitle": "Regla, clasificación, ubicación exacta y cómo verificarlo",
    "ui.expert.rule": "Regla",
    "ui.expert.tool": "Herramienta",
    "ui.expert.cwe": "CWE",
    "ui.expert.owasp": "OWASP",
    "ui.expert.confidence": "Confianza",
    "ui.expert.location": "Ubicación",
    "ui.expert.verify": "Cómo verificarlo",
    "ui.ai.verdict.likely_real": "Probable real",
    "ui.ai.verdict.likely_false": "Probable falso",
    "ui.ai.verdict.uncertain": "Incierto",
    "ui.ai.level.high": "alta",
    "ui.ai.level.medium": "media",
    "ui.ai.level.low": "baja",
    "ui.ai.risk_level.high": "alto",
    "ui.ai.risk_level.medium": "medio",
    "ui.ai.risk_level.low": "bajo",
    "ui.ai.risk_level.none": "ninguno",
    "ui.ai.opinion": "{verdict} (confianza {level}).",
    "ui.ai.risk": "riesgo de {name}: {level}",
    "ui.ai.risk_name.idor": "acceso a registros ajenos",
    "ui.ai.risk_name.flow": "saltar o repetir pasos",
    "ui.ai.suggested_fix": "Corrección sugerida: {fix}",
    "ui.ai.reachable": "Alcanzable desde la entrada del usuario: {answer}",
    "ui.ai.reachable.yes": "sí",
    "ui.ai.reachable.no": "no",
    "ui.ai.reachable.unclear": "no está claro",
    "ui.ai.source": "Entrada: {source}",
    "ui.ai.risk_name.sink": "un ataque a través de esta operación",
    "ui.facts.ai_new_findings.one": (
        "La IA encontró {count} posible problema que las reglas "
        "solas no reportan; compruébalo antes de actuar."
    ),
    "ui.facts.ai_new_findings.other": (
        "La IA encontró {count} posibles problemas que las reglas "
        "solas no reportan; compruébalos antes de actuar."
    ),
    "ui.facts.ai_sinks_clear.one": (
        "La IA revisó {count} punto de riesgo y no encontró nada que añadir."
    ),
    "ui.facts.ai_sinks_clear.other": (
        "La IA revisó {count} puntos de riesgo y no encontró nada que añadir."
    ),
    "ui.how.title": "Cómo se analizó",
    "ui.how.profile": "Perfil {profile}: {modules}.",
    "ui.facts.ran": "Se ejecutó: {tools}.",
    "ui.facts.failed": "No se pudo ejecutar: {tools}.",
    "ui.facts.no_ai": "Sin revisión con IA: este perfil no la incluye.",
    "ui.facts.ai_ran": "Revisión con IA: modelo {model}. {detail}{summary}",
    "ui.facts.ai_summary_yes": " Redactó el resumen.",
    "ui.facts.ai_summary_no": " No redactó resumen.",
    "ui.facts.unnamed_model": "sin nombre",
    "ui.facts.ai_failed": "La revisión con IA no se ejecutó: {detail}.",
    "ui.facts.unavailable": "no disponible",
    "ui.limitations.title": "Limitaciones de esta corrida",
    "ui.endpoints.title": "Inventario de endpoints",
    "ui.endpoints.any_method": "cualquiera",
    "ui.endpoints.protected": "con autenticación",
    "ui.endpoints.unprotected": "sin autenticación",
    "ui.endpoints.unknown": "no determinado",
    "ui.folders.title": "Carpetas a omitir",
    "ui.folders.suggested_title": "Sugeridas para este proyecto",
    "ui.folders.suggested_help": (
        "Parecen salida de compilación, cachés o carpetas de herramientas. "
        "No se omite nada hasta que guardes."
    ),
    "ui.folders.vendor_note": (
        "Recibes código de un proveedor: las carpetas de editor, de asistente y del "
        ".gitignore empiezan sin marcar, porque ahí se puede esconder código."
    ),
    "ui.folders.patterns_label": "Archivos a omitir (patrones, separados por comas)",
    "ui.folders.patterns_hint": "p. ej. *.spec.ts, docs/*.md",
    "ui.folders.patterns_help": (
        "Los manifiestos y archivos de bloqueo como package.json siempre se analizan, y los "
        "secretos se buscan en todos los archivos."
    ),
    "ui.folders.choose_first": "Primero elige una carpeta.",
    "ui.folders.by_default": "{folder}   (se omite por defecto)",
    "ui.folders.none": "Esta carpeta no tiene subcarpetas.",
    "ui.folders.will_analyze": "Se analizarán {count} archivos.",
    "ui.folders.help": (
        "Marca las carpetas que no quieres que se analicen en este "
        "proyecto. Se recuerda para los siguientes análisis."
    ),
    "ui.preview.title": "Se analizarían {count} archivos",
    "ui.preview.modules": "Módulos: {modules}",
    "ui.preview.excluded": "No se incluyen: {folders}",
    "ui.settings.title": "Configuración",
    "ui.settings.analysis": "Análisis",
    "ui.settings.language": "Idioma / Language",
    "ui.settings.default_profile": "Perfil al abrir",
    "ui.settings.never_analyzed": "Carpetas que nunca se analizan: {folders}.",
    "ui.settings.extra_folders": (
        "Otras carpetas a omitir (separadas por coma, p. ej. legado, docs/viejo)"
    ),
    "ui.settings.user_rules": "Tus propias reglas",
    "ui.settings.user_rules_help": (
        "Carpetas con reglas de Opengrep en YAML que se suman a las incluidas. Se revisan antes "
        "de cada análisis; una regla con errores se omite y el resultado dice por qué."
    ),
    "ui.settings.user_rules_dirs": (
        "Carpetas de reglas (separadas por coma, p. ej. ~/heimdall-rules)"
    ),
    "ui.settings.user_rules_check": "Revisar reglas",
    "ui.settings.user_rules_checking": "Revisando...",
    "ui.settings.user_rules_none": "No hay carpetas de reglas.",
    "ui.settings.user_rules_ok.one": "{count} regla lista en {files} archivos",
    "ui.settings.user_rules_ok.other": "{count} reglas listas en {files} archivos",
    "ui.settings.user_rules_problem": "{file}: {detail}",
    "ui.settings.user_rules_more.one": "y {count} más",
    "ui.settings.user_rules_more.other": "y {count} más",
    "ui.settings.user_rules_no_engine": (
        "El motor de reglas no está disponible, así que solo se revisó la estructura."
    ),
    "ui.settings.ai_section": "Revisión con IA",
    "ui.settings.use_ai": "Usar la revisión con IA",
    "ui.settings.ai_help": (
        "Registra uno o varios servidores de IA, cada uno con sus "
        "modelos. Puede ser el mismo servidor con otros modelos."
    ),
    "ui.settings.tools": "Herramientas",
    "ui.settings.checking_versions": "Consultando las versiones…",
    "ui.cli.title": "Línea de comandos",
    "ui.cli.installed": "El comando hdl está instalado: {path}",
    "ui.cli.installed_version": "Versión instalada: {version}",
    "ui.cli.not_installed": "El comando hdl no está instalado.",
    "ui.cli.note": (
        "Comparte las bases de datos y el historial con esta app. Después de instalarlo, abre "
        "una terminal nueva para usarlo."
    ),
    "ui.cli.needs_internet": "La primera vez necesita internet para descargar lo que usa.",
    "ui.cli.install": "Instalar el comando hdl",
    "ui.cli.uninstall": "Desinstalar el comando hdl",
    "ui.cli.no_python": (
        "Instalar el comando necesita Python {minimum} o más nuevo, y no se encontró ninguno "
        "en este equipo."
    ),
    "ui.cli.download_python": "Descargar Python",
    "ui.cli.unavailable": (
        "Esta copia de la app no incluye el instalador del comando. Descarga install_hdl.py "
        "de la página de versiones del proyecto."
    ),
    "ui.cli.checking": "Buscando Python…",
    "ui.cli.running_install": "Instalando el comando. Puede tardar un minuto…",
    "ui.cli.running_uninstall": "Quitando el comando…",
    "ui.cli.result.installed_title": "El comando hdl está listo",
    "ui.cli.result.installed": "El comando está en {path}.",
    "ui.cli.result.reopen": "Abre una terminal nueva para usarlo.",
    "ui.cli.result.install_failed": "No se pudo instalar el comando",
    "ui.cli.result.uninstalled_title": "Se quitó el comando hdl",
    "ui.cli.result.uninstalled": "No se tocaron tus bases, historial ni ajustes.",
    "ui.cli.result.uninstall_failed": "No se pudo quitar el comando",
    "ui.cli.result.last_lines": "Las últimas líneas del instalador:",
    "ui.cli.result.no_output": "El instalador no imprimió nada.",
    "ui.cli.offer.title": "El comando hdl",
    "ui.cli.offer.body": (
        "¿Quieres también el comando hdl para la terminal? Te permite analizar desde la línea "
        "de comandos y automatizar, compartiendo bases de datos e historial con esta app."
    ),
    "ui.cli.offer.install": "Instalarlo",
    "ui.cli.offer.later": "Ahora no",
    "ui.cli.offer.later_note": "Si lo dejas para después, puedes hacerlo en Configuración.",
    "ui.settings.thresholds": "Umbrales del dictamen",
    "ui.settings.language_busy": "Cambia el idioma cuando termine el análisis.",
    "ui.settings.not_saved": "No se guardó: {error}",
    "ui.settings.saved": "Configuración guardada en {path}",
    "ui.thresholds.title": "Umbrales del dictamen",
    "ui.thresholds.help": (
        "Deciden si una entrega de proveedor se puede recibir. Cada "
        "cambio pide el PIN y queda registrado con usuario y fecha."
    ),
    "ui.thresholds.max_critical": "Críticos",
    "ui.thresholds.max_secrets": "Secretos",
    "ui.thresholds.max_unauth_write_endpoints": "Endpoints de escritura sin autenticación",
    "ui.thresholds.max_high": "Altos",
    "ui.thresholds.max_patchable_critical_deps": "Dependencias críticas con parche",
    "ui.thresholds.maximum": "Máximo: {label}",
    "ui.thresholds.count_ai": "Contar las sugerencias de IA",
    "ui.thresholds.pin": "PIN",
    "ui.thresholds.pin_new": "PIN nuevo (mínimo 6 caracteres)",
    "ui.thresholds.pin_repeat": "Repite el PIN nuevo",
    "ui.thresholds.pin_mismatch": "Los PIN no coinciden.",
    "ui.thresholds.invalid": "Valor no válido: {error}",
    "ui.thresholds.saved": "Umbrales guardados; el cambio quedó en la bitácora.",
    "ui.thresholds.changes": "Cambios registrados en la bitácora: {count}",
    "ui.coverage.title": "Qué revisa Heimdall Guardian",
    "ui.coverage.what_is": "Qué es OWASP",
    "ui.coverage.edition": "Las categorías siguen el OWASP Top 10:{year}.",
    "ui.coverage.yes": "Sí",
    "ui.coverage.partial": "En parte",
    "ui.coverage.no": "No",
    "ui.coverage.none_open": "Sin hallazgos abiertos",
    "ui.coverage.open.one": "{count} abierto",
    "ui.coverage.open.other": "{count} abiertos",
    "ui.coverage.example": "Por ejemplo: {example}",
    "ui.tour.indicator": "Paso {current} de {total}",
    "ui.tour.next": "Siguiente",
    "ui.tour.back": "Atrás",
    "ui.tour.skip": "Omitir",
    "ui.tour.start": "Empezar",
    "ui.tour.replay": "Ver la visita guiada",
    "ui.tour.what.title": "Qué hace Heimdall Guardian",
    "ui.tour.what.body": (
        "Revisa el código de una carpeta de tu equipo y te dice qué riesgos de seguridad "
        "tiene, ordenados por gravedad, con cómo corregir cada uno. Funciona sin internet, "
        "salvo para actualizar sus bases."
    ),
    "ui.tour.wont.title": "Qué no hace",
    "ui.tour.wont.body": (
        "No modifica tu carpeta, no ejecuta tu código y no lo envía a ningún lado: la IA es "
        "opcional y solo se ejecuta en tu equipo. No sustituye la revisión de una persona."
    ),
    "ui.tour.read.title": "Cómo leer el resultado",
    "ui.tour.read.body": (
        "La frase de arriba, con colores de semáforo, lo resume. Las bandas por gravedad "
        "filtran la lista, y cada hallazgo explica qué pasa y cómo corregirlo. Puedes "
        "aceptar un riesgo o marcar un falso positivo, siempre con una justificación."
    ),
    "ui.about.author": "Autor: {author}. Licencia Apache-2.0.",
    "ui.about.description": (
        "Análisis estático de seguridad de código, local y de solo "
        "lectura: revisa secretos, dependencias vulnerables, código "
        "inseguro y endpoints sin autenticación, y dice dónde está "
        "cada problema y cómo corregirlo."
    ),
    "ui.about.guarantees": (
        "Solo lee la carpeta elegida, nunca ejecuta su código y nada "
        "sale de tu red. No sustituye pruebas de penetración ni la "
        "revisión manual de la lógica de negocio."
    ),
    "ui.about.third_party": "Componentes de terceros",
    "ui.about.license_line": "{name}: licencia {license}",
    "ui.about.third_party_note": (
        "Se incluyen sin modificar; sus licencias completas acompañan a la aplicación."
    ),
    "ui.about.graphics": "Elementos gráficos",
    "ui.about.art_notice_original": "Aviso original, tal cual lo escribió su autor.",
    "ui.export.dialog_title": "Guardar reporte",
    "ui.export.inside_folder": (
        "El reporte no se guarda dentro de la carpeta analizada. Elige otro lugar."
    ),
    "ui.export.failed": "No se pudo guardar: {error}",
    "ui.export.saved": "Reporte guardado en {path}",
    "ui.settings.ai_reasoning": "Dejar que el modelo razone antes de responder (más lento)",
    "llm.limit.low_valid": (
        "El modelo respondió en un formato inutilizable en {invalid} de {asked} consultas "
        "({truncated} cortadas por longitud). Si es un modelo de razonamiento, pon "
        'reasoning = "off" en este destino, o sube sus límites.'
    ),
    "ui.aiedit.use": "Usar",
    "ui.aiedit.fallback": "Si no responde, usar",
    "ui.aiedit.add": "Agregar configuración de IA",
    "ui.aiedit.unnamed": "Sin nombre ({number})",
    "ui.aiedit.none": "Ninguna",
    "ui.aiedit.keep_one": "Deja al menos una configuración.",
    "ui.aiedit.testing": "Probando…",
    "ui.aiedit.connected": "Conectado. Modelos: {models}",
    "ui.aiedit.no_models": "ninguno",
    "ui.aiedit.no_connection": "Sin conexión: {error}",
    "ui.aiedit.name": "Nombre (p. ej. oficina)",
    "ui.aiedit.url": "Dirección del servidor",
    "ui.aiedit.remove_tip": "Quitar esta configuración",
    "ui.aiedit.test": "Probar conexión",
    "ui.aiedit.models_none": "sin modelos",
    "ui.aitask.triage": "Modelo para valorar hallazgos",
    "ui.aitask.endpoints": "Modelo para revisar endpoints",
    "ui.aitask.sinks": "Modelo para revisar operaciones riesgosas (opcional)",
    "ui.aitask.summary": "Modelo para el resumen",
    "ui.aitask.consensus": "Segundo modelo de contraste (opcional)",
    "ui.aiform.at_least_one": "Deja al menos una configuración de IA.",
    "ui.aiform.name_required": "Ponle nombre a la configuración {number}.",
    "ui.aiform.duplicate": "Hay dos configuraciones llamadas «{name}».",
    # --- I3-A: núcleo, reportes, almacenamiento, adaptadores e IA ---
    "core.error.not_a_folder": "No es una carpeta: {path}",
    "core.examples.few": "p. ej. {paths}",
    "core.examples.many": "p. ej. {paths} y otros",
    "core.limit.pending_modules": "Módulos aún no disponibles en esta versión: {names}.",
    "core.limit.partial_module": "Módulo {module} parcial: {reason}.",
    "core.limit.not_installed": "{tool} no está instalado: cobertura reducida en {affected}.",
    "core.limit.tool_failed": "{tool} falló: cobertura reducida en {affected}.",
    "core.limit.db_old": (
        "La base de vulnerabilidades de {tool} tiene {age} días: puede faltar lo publicado desde "
        "entonces. Actualícela con --actualizar-bases."
    ),
    "core.limit.ai_disabled": "IA desactivada: el análisis se hizo sin el módulo IA.",
    "core.limit.ai_unavailable": "IA no disponible ({detail}): el análisis continuó sin ella.",
    "core.tool.ai_stats": (
        "destino {destination}; {valid} de {asked} respuestas válidas; {cached} tomadas de caché; "
        "{sinks_reviewed} puntos de riesgo revisados, {sinks_found} posibles problemas."
    ),
    "core.tool.ai_stats_detail": (
        "destino {destination}; {valid} de {asked} respuestas válidas; {cached} tomadas de caché; "
        "{sinks_reviewed} puntos de riesgo revisados, {sinks_found} posibles problemas. {detail}"
    ),
    "core.tool.no_ai_config": "sin configuración de IA",
    "core.tool.not_installed": "no instalado",
    "core.coverage.note": (
        "{name}: se revisan secretos, dependencias y configuración; aún no hay {missing}."
    ),
    "core.coverage.missing_rules": "reglas de código propias",
    "core.coverage.missing_both": "reglas de código propias ni inventario de endpoints",
    "verdict.criterion.max_critical": "Hallazgos críticos",
    "verdict.criterion.max_secrets": "Secretos en el código o en el historial de git",
    "verdict.criterion.max_unauth_write_endpoints": ("Endpoints de escritura sin autenticación"),
    "verdict.criterion.max_patchable_critical_deps": (
        "Dependencias con vulnerabilidad crítica y versión corregida disponible"
    ),
    "verdict.criterion.max_high": "Hallazgos altos",
    "core.verdict.unknown_threshold": "Umbral desconocido: {names}.",
    "core.verdict.invalid_value": "Valor no válido para {name}: {value}.",
    "core.config.legacy": (
        "{path} es de una versión anterior (claves en español) y ya no se lee. Renómbralo o "
        "bórralo y crea uno nuevo con `hdl config --init` (o desde Configuración en la "
        "aplicación)."
    ),
    "core.config.no_ai_config": "No existe la configuración de IA {name}. Hay: {known}.",
    "core.config.unknown_option": "Opción desconocida en {where}: {names}.",
    "core.config.incomplete": "Sección {where} incompleta: {error}.",
    "core.config.unreadable": "No se pudo leer {path}: {error}",
    "core.config.unknown_section": "Sección desconocida en {file}: {names}.",
    "core.config.bad_language": (
        "Idioma no soportado en [general] language: {value}. Usa {first} o {second}, o déjalo "
        "vacío."
    ),
    "core.config.bad_reasoning": (
        'Razonamiento no admitido en el destino de IA {name}: {value}. Usa "off" u "on".'
    ),
    "core.profiles.custom_needs_module": "El perfil personalizado requiere al menos un módulo.",
    "core.profiles.unknown_profile": "Perfil desconocido: {profile}. Opciones: {valid}.",
    "core.profiles.unknown_module": "Módulo desconocido: {module}. Opciones: {valid}.",
    "storage.archived": (
        "Se archivó el historial de una versión anterior ({name}): esta corrida empieza una línea "
        "base nueva."
    ),
    "storage.archived_exclusions": (
        "Las carpetas omitidas guardadas de este proyecto usaban un formato anterior y se "
        "archivaron ({name}): vuelva a definirlas si las necesita."
    ),
    "storage.suppression_expired": (
        "La supresión de {id} venció el {date}: el hallazgo vuelve a contar."
    ),
    "storage.error.data_inside_folder": (
        "El directorio de datos de Heimdall Guardian está dentro de la carpeta analizada; elija "
        "una carpeta más específica."
    ),
    "storage.error.no_runs": "No hay corridas guardadas para este proyecto.",
    "storage.error.no_such_run": "No existe la corrida {run} en este proyecto.",
    "storage.error.no_such_finding": "No existe el hallazgo {id} en este proyecto.",
    "storage.error.bad_suppression_status": (
        "Una supresión solo puede ser ACEPTADO o FALSO_POSITIVO."
    ),
    "storage.error.justification_required": "La justificación es obligatoria.",
    "storage.error.bad_baseline_file": "No es un archivo de línea base válido: {error}",
    "storage.error.bad_baseline_format": "Formato de línea base no soportado: {format}.",
    "storage.error.digest_mismatch": (
        "La huella no coincide: el archivo fue modificado o está dañado."
    ),
    "storage.error.bad_imported_status": "Estado de supresión no válido: {status}.",
    "storage.error.imported_without_justification": (
        "Una supresión importada no trae justificación."
    ),
    "bases.error.nothing_to_export": (
        "No hay bases locales que exportar: use antes `hdl bases --actualizar`."
    ),
    "bases.error.bad_package": "El archivo no es un paquete de bases válido: {name}",
    "bases.state.updated": "actualizada",
    "bases.state.not_installed": "no instalada",
    "bases.state.failed": "no se pudo: {detail}",
    "bases.downloading": "Descargando la base de {name} ({step} de {total})…",
    "bases.size_notice": (
        "Las bases de vulnerabilidades pesan unos 2 GB. Con una conexión lenta la descarga "
        "puede tardar bastante, aunque parezca que no avanza; déjala terminar."
    ),
    "bases.still_downloading": "{step} {elapsed}",
    "bases.elapsed.minutes": "{minutes} min {seconds} s",
    "bases.elapsed.seconds": "{seconds} s",
    "bases.lock.waiting": (
        "Otra ventana o comando de Heimdall está actualizando las bases; espera a que termine…"
    ),
    "bases.lock.timeout": (
        "Otra ventana o comando de Heimdall sigue actualizando las bases. "
        "Vuelve a intentarlo cuando termine."
    ),
    "core.paths.data": "Carpeta de datos: {path}{source}",
    "core.paths.bases": "Carpeta de bases: {path}{source}",
    "core.paths.from_env": " (definida por {variable})",
    "cli.hint.app": (
        "Consejo: en esta computadora también puedes analizar con un clic en la app "
        "Heimdall Guardian: {url}"
    ),
    "ui.bases.download_label": "descarga",
    "thresholds.error.no_pin": "Aún no hay PIN: defínalo antes de cambiar los umbrales.",
    "thresholds.error.pin_mismatch": "El PIN no coincide.",
    "thresholds.error.pin_too_short": "El PIN debe tener al menos {minimum} caracteres.",
    "thresholds.archived": (
        "Se archivó el archivo de umbrales del dictamen de una versión anterior ({names}); "
        "se usan los umbrales por defecto y el PIN no se conservó: defina uno nuevo antes de "
        "cambiarlos."
    ),
    "thresholds.log.pin_set": "PIN definido",
    "thresholds.log.pin_changed": "PIN cambiado",
    "thresholds.log.changed": "umbrales modificados",
    "adapter.timeout": "tiempo máximo agotado ({seconds} s)",
    "adapter.run_failed": "no se pudo ejecutar {command}: {error}",
    "adapter.binary_missing": "{binary} no está instalado",
    "adapter.failed": "{tool} falló: {detail}",
    "adapter.unreadable_report": "{tool}: reporte ilegible ({error})",
    "adapter.unreadable_output": "{tool}: salida ilegible ({error})",
    "adapter.db.missing": (
        "Faltan las bases de vulnerabilidades en este equipo, así que no se revisaron las "
        "dependencias. Descárgalas marcando «Actualizar las bases al analizar» en la aplicación, o "
        "con --actualizar-bases en la terminal (alrededor de 2 GB la primera vez). "
        "Se buscaron en: {path}.{hint}"
    ),
    # Empieza con un espacio: va después de la frase que termina con la ruta.
    "adapter.db.isolated_hint": (
        " HDL_DATA_DIR está definida, así que las bases se buscan ahí; apunta HDL_BASES_DIR a tus "
        "bases habituales para reutilizarlas."
    ),
    "adapter.db.missing_short": "falta la base de vulnerabilidades",
    "adapter.gitleaks.no_history": (
        "Sin historial git: solo se buscaron secretos en los archivos actuales."
    ),
    "adapter.opengrep.no_rules": "no se encontraron reglas propias en {path}",
    "adapter.osv.db_of": "la base de {names}",
    "adapter.osv.db_of_one": "la base de un ecosistema",
    "adapter.osv.db_missing": (
        "OSV no tiene en este equipo {named}; actualiza las bases para revisar esas dependencias. "
        "Se buscaron en: {path}.{hint}"
    ),
    "updates.status.error": "no se pudo consultar ({error})",
    "updates.status.not_installed": "no instalada; la última es {latest}",
    "updates.status.no_release": "sin versión publicada",
    "updates.status.newer": "hay una más nueva: {latest}",
    "updates.status.up_to_date": "al día",
    "cli.version.help": "muestra la versión instalada (--check la compara con la última publicada)",
    "cli.version.check": "consulta en línea si hay una versión nueva (no envía nada de tu código)",
    "cli.version.latest": "Última versión publicada: {latest} ({status})",
    "cli.version.page": "Página de la versión: {page}",
    "cli.version.update": (
        "Para actualizar un comando instalado con install_hdl.py, descarga {wheel} de esa página "
        "y ejecuta:\n  python3 install_hdl.py --wheel {wheel}\n"
        "Cuando el paquete esté en PyPI podrás ejecutar: python3 install_hdl.py --version {latest}"
    ),
    "updates.self.error": "no se pudo consultar ({error})",
    "updates.self.no_release": "aún no hay una versión publicada",
    "updates.self.newer": "hay una versión más nueva: {latest}",
    "updates.self.ahead": "más reciente que la última publicada ({latest})",
    "updates.self.current": "al día",
    "ui.about.update_check": "Buscar actualizaciones",
    "ui.about.update_checking": "Consultando...",
    "ui.about.update_open": "Abrir la página de la versión",
    "ui.about.update_line": "Instalada {installed}: {status}",
    "llm.ai_label": "Sugerencia IA — requiere validación humana",
    "llm.destination.invalid_url": "URL de destino no válida: {url}.",
    "llm.destination.credentials": "La URL del destino no debe incluir credenciales.",
    "llm.destination.not_local": (
        "El destino {host} no es local ni está en allowed_hosts: se rechaza para que el código no "
        "salga de la red local."
    ),
    "llm.destination.https_required": "El destino {host} no es local: debe usar HTTPS.",
    "llm.model.cloud": (
        "El modelo {model} se ejecuta en la nube: se rechaza para que el código no salga de la red "
        "local."
    ),
    "llm.client.token_missing": "El destino {name} requiere token y no hay uno en el llavero.",
    "llm.client.http_error": "HTTP {code}: {detail}",
    "llm.client.no_connection": "sin conexión con {name}: {error}",
    "llm.client.unreadable": "respuesta ilegible del destino",
    "llm.client.empty": "respuesta sin contenido",
    "llm.problem": "{name}: {error}",
    "llm.limit.fallback": "IA: se usó el destino {destination} ({problems}).",
    "llm.limit.generic": "IA: {error}",
    "llm.limit.query_failed": "IA: una consulta falló ({error}).",
    "llm.limit.cancelled": "IA: se canceló tras revisar {done} de {total} objetivo(s).",
    "llm.limit.no_triage_model": "IA: sin modelo de triage configurado.",
    "llm.limit.no_endpoint_model": "IA: sin modelo de revisión de endpoints configurado.",
    "llm.limit.no_summary": "IA: no se generó el resumen ejecutivo ({error}).",
    "llm.detail.disabled": "IA desactivada en la configuración",
    "llm.detail.no_destinations": "no hay destinos de IA configurados",
    "llm.detail.problems": "{problems}",
    "llm.detail.stopped": "el destino dejó de responder: {error}",
    "llm.detail.cancelled": "revisión cancelada",
    "llm.invalid_reply": "El modelo no dio una respuesta válida.",
    "llm.finding.title": "{label}: posible {what} en {route}",
    "llm.finding.what_idor": "acceso a registros ajenos cambiando un identificador",
    "llm.finding.what_flow": "pasos del proceso que se pueden saltar o repetir",
    "llm.finding.any_method": "cualquiera",
    "llm.finding.title_sink": "{label}: {what} en {file}",
    "llm.finding.what_sql": "posible inyección SQL",
    "llm.finding.what_exec": "posible inyección de comandos",
    "llm.finding.what_path": "posible recorrido de rutas",
    "llm.finding.what_ssrf": "posible SSRF",
    "llm.finding.what_redirect": "posible redirección abierta",
    "llm.finding.what_deser": "posible deserialización insegura",
    "llm.finding.what_xxe": "posible inyección de entidades externas XML",
    "llm.finding.description_sink": "{explanation}\n\nEntrada: {source}",
    "llm.finding.recommendation_sink": (
        "Revisar el código manualmente. Si se confirma, no construir la operación con datos del "
        "usuario: usar parámetros, una lista de permitidos o una conversión estricta antes de "
        "llegar a este punto."
    ),
    "llm.finding.recommendation": (
        "Revisar manualmente el manejador. Si se confirma, validar que el registro pertenezca a "
        "quien consulta y que cada paso verifique el estado del proceso."
    ),
    "authz.note.unreadable": "No se pudo leer {file}.",
    "authz.note.not_python": "No se pudo leer {file} como Python.",
    "authz.note.module_not_found": "No se encontró el módulo de rutas {module}.",
    "authz.note.too_large": "{file} es demasiado grande para el inventario de Node.js.",
    "authz.note.node_routes": (
        "No se pudo interpretar {file} ({error}): sus rutas no están en el inventario."
    ),
    "authz.note.non_literal_route": "{file}:{line}: ruta no literal ({route}); se omitió.",
    "authz.note.non_literal_chain": "{file}:{line}: route() no literal; se omitió.",
    "authz.note.unresolved_router": (
        "No se pudo resolver el router {router} montado en {scope} ({file}): sus rutas, si se "
        "analizan, quedan sin ese prefijo."
    ),
    "authz.note.unmounted_router": (
        "El router {name} de {file} no se monta en ningún archivo analizado: sus rutas quedan sin "
        "prefijo."
    ),
    "authz.note.node_controllers": (
        "No se pudo interpretar {file} ({error}): sus controladores no están en el inventario."
    ),
    "authz.limit.extractor_failed": (
        "El inventario de endpoints de {name} falló ({error}): cobertura reducida en AUTHZ."
    ),
    "owasp.coverage.yes": "Sí",
    "owasp.coverage.partial": "En parte",
    "owasp.coverage.no": "No",
    "report.disclaimer": (
        "Este análisis es estático. No sustituye pruebas de penetración ni revisión manual de "
        "lógica de negocio."
    ),
    "report.tool_status.ran": "ejecutado",
    "report.tool_status.skipped": "omitido",
    "report.tool_status.error": "error",
    "report.db.none": "sin base",
    "report.db.unused": "no usa",
    "report.undetermined": "No determinado",
    "report.yes": "Sí",
    "report.no": "No",
    "report.any_method": "cualquiera",
    "report.ai.verdict.likely_real": "probable real",
    "report.ai.verdict.likely_false": "probable falso",
    "report.ai.verdict.uncertain": "incierto",
    "report.ai.level.high": "alta",
    "report.ai.level.medium": "media",
    "report.ai.level.low": "baja",
    "report.ai.risk_level.high": "alto",
    "report.ai.risk_level.medium": "medio",
    "report.ai.risk_level.low": "bajo",
    "report.ai.risk_level.none": "ninguno",
    "report.html.lang": "es-MX",
    "report.html.title": "Reporte de seguridad · {project}",
    "report.html.kicker": "{tagline} · Reporte de análisis estático de seguridad",
    "report.html.date": "Fecha",
    "report.profile": "Perfil",
    "report.run": "Corrida",
    "report.run_number": "n.º {run}",
    "report.no_baseline": "sin línea base",
    "report.files": "Archivos analizados",
    "report.version": "Versión de Heimdall Guardian",
    "report.rules_version": "Versión de las reglas",
    "report.html.rules": "reglas {version}",
    "report.html.hash": "Hash del código analizado (SHA-256)",
    "report.verdict.title": "Dictamen de entrega",
    "report.verdict.criterion": "Criterio",
    "report.verdict.found": "Encontrados",
    "report.verdict.maximum": "Máximo",
    "report.verdict.result": "Resultado",
    "report.verdict.exceeded": "Rebasado",
    "report.verdict.exceeded_blocking": "Rebasado · impide recibir",
    "report.verdict.within": "Cumple",
    "report.verdict.custom_thresholds": (
        "Los umbrales aplicados difieren de los valores institucionales por defecto."
    ),
    "report.verdict.issuer": "Emite: {issuer} · {date}",
    "report.verdict.signature": "Huella del dictamen",
    "report.light.rojo": "rojo",
    "report.light.amarillo": "amarillo",
    "report.light.verde": "verde",
    "report.light.label": "Semáforo: {color}",
    "report.light.rojo.text": "Requiere atención inmediata: hay hallazgos críticos abiertos.",
    "report.light.amarillo.text": "Requiere plan de corrección: hay hallazgos altos abiertos.",
    "report.light.verde.text": "Sin hallazgos críticos ni altos abiertos.",
    "report.summary.open_total": (
        "Hallazgos abiertos: {count}. No incluye los aceptados ni los marcados como falso positivo."
    ),
    "report.ai.summary_heading": "Resumen ejecutivo · {label}",
    "report.ai.summary_note": (
        "Redactado por el modelo {model} a partir de cifras agregadas; no recibió código."
    ),
    "report.plan.title": "Por dónde empezar",
    "report.plan.help": (
        "Agrupados por causa común, lo más grave primero. No incluye las sugerencias de la IA."
    ),
    "report.plan.update": "Actualiza {package} a {version}: resuelve {findings} en {files}",
    "report.plan.review": "Revisa {package}: aún no se conoce una versión corregida ({findings})",
    "report.plan.rule": "{title}: {findings} en {files}",
    "report.plan.findings.one": "{count} hallazgo",
    "report.plan.findings.other": "{count} hallazgos",
    "report.plan.files.one": "{count} archivo",
    "report.plan.files.other": "{count} archivos",
    "report.plan.col.number": "#",
    "report.plan.col.action": "Acción",
    "report.plan.col.findings": "Hallazgos",
    "report.plan.col.files": "Archivos",
    "report.plan.col.ids": "IDs",
    "ui.plan.button": "Por dónde empezar",
    "report.risks.title": "Principales riesgos",
    "report.risks.detail": "— {cases} en {files}",
    "report.no_open": "Sin hallazgos abiertos.",
    "report.compare.title": "Comparación con la corrida anterior",
    "report.compare.new": "Nuevos",
    "report.compare.persistent": "Persistentes",
    "report.compare.fixed": "Corregidos",
    "report.compare.accepted": "Riesgo aceptado",
    "report.compare.false_positive": "Falso positivo",
    "report.compare.first_run": (
        "Primera corrida del proyecto: todos los hallazgos son nuevos. La comparación estará "
        "disponible en la siguiente."
    ),
    "report.compare.no_baseline": "Corrida sin línea base.",
    "report.trend.title": "Tendencia de hallazgos abiertos",
    "report.trend.aria": "Hallazgos abiertos por corrida",
    "report.trend.bar": "Corrida {run} ({date}): {label} {count}",
    "report.coverage.title": "Qué revisa Heimdall Guardian",
    "report.coverage.what_is": "Qué es OWASP",
    "report.coverage.category": "Categoría",
    "report.coverage.meaning": "Qué significa",
    "report.coverage.example": "Un ejemplo cotidiano",
    "report.coverage.coverage": "Cobertura de Heimdall Guardian",
    "report.coverage.open": "Hallazgos abiertos",
    "report.owasp_map.title": "Mapa por categoría OWASP Top 10",
    "report.owasp.unclassified": "Sin clasificar",
    "report.endpoints.title": "Inventario de endpoints",
    "report.endpoints.summary": "{total} endpoints detectados; {open} sin autenticación.",
    "report.endpoints.method": "Método",
    "report.endpoints.route": "Ruta",
    "report.endpoints.handler": "Manejador",
    "report.endpoints.requires_auth": "¿Requiere autenticación?",
    "report.endpoints.has_auth": "¿Tiene autenticación?",
    "report.endpoints.idor": "Riesgo IDOR",
    "report.endpoints.source": "Fuente",
    "report.endpoints.public_by_design": "Parece pública por diseño",
    "report.endpoints.no_write": "No · escritura",
    "report.endpoints.not_evaluated": "Sin evaluar",
    "report.endpoints.ai": "IA",
    "report.findings.title": "Hallazgos detallados",
    "report.findings.search": "Buscar por archivo, regla o texto",
    "report.findings.search_aria": "Buscar",
    "report.findings.severity": "Severidad",
    "report.findings.any_severity": "Toda severidad",
    "report.findings.category": "Categoría",
    "report.findings.any_category": "Toda categoría",
    "report.findings.status": "Estado",
    "report.findings.any_status": "Todo estado",
    "report.findings.origin": "Origen",
    "report.findings.any_origin": "Todo origen",
    "report.findings.of": " de ",
    "report.findings.none": "No se encontraron hallazgos en el código.",
    "report.finding.what": "Qué y por qué",
    "report.finding.fix": "Cómo corregir",
    "report.finding.classification": "Clasificación",
    "report.finding.origin": "Origen",
    "report.finding.rule": "regla {rule}",
    "report.finding.confidence": "confianza {level}",
    "report.finding.verify": "Cómo verificarlo",
    "report.finding.references": "Referencias",
    "report.ai.verdict": "Veredicto",
    "report.ai.confidence": "confianza {level}",
    "report.ai.risk_idor": "Riesgo de acceso a registros ajenos",
    "report.ai.risk_flow": "de saltar o repetir pasos",
    "report.ai.suggested_fix": "Corrección sugerida:",
    "report.ai.reachable": "Alcanzable desde la entrada del usuario",
    "report.ai.reachable.yes": "sí",
    "report.ai.reachable.no": "no",
    "report.ai.reachable.unclear": "no está claro",
    "report.ai.source": "Entrada",
    "report.ai.risk_sink": "Riesgo de un ataque a través de esta operación",
    "report.ai.model_note": "Modelo: {model}. No modifica la severidad ni el estado del hallazgo.",
    "report.ai.unknown_model": "desconocido",
    "report.dependencies.title": "Dependencias vulnerables",
    "report.dependencies.severity": "Severidad",
    "report.dependencies.package": "Paquete",
    "report.dependencies.vulnerability": "Vulnerabilidad",
    "report.dependencies.fix": "Corrección",
    "report.dependencies.file": "Archivo",
    "report.dependencies.status": "Estado",
    "report.dependencies.none": "No se encontraron dependencias con vulnerabilidades conocidas.",
    "report.fixed.title": "Corregidos desde la corrida anterior",
    "report.fixed.finding": "Hallazgo",
    "report.fixed.previous_location": "Ubicación anterior",
    "report.annex.title": "Anexo técnico",
    "report.annex.tool": "Herramienta",
    "report.annex.version": "Versión",
    "report.annex.status": "Estado",
    "report.annex.findings": "Hallazgos",
    "report.annex.database": "Base de vulnerabilidades",
    "report.annex.detail": "Detalle",
    "report.annex.limitations": "Limitaciones de esta corrida",
    "report.omitted.title": "Omitido en este análisis",
    "report.omitted.folders.one": "{count} carpeta",
    "report.omitted.folders.other": "{count} carpetas",
    "report.omitted.files.one": "{count} archivo",
    "report.omitted.files.other": "{count} archivos",
    "report.omitted.and": "{first} y {second}",
    "report.omitted.left_out": "No se analizó: {parts}.",
    "report.omitted.more": "y {count} más",
    "report.omitted.findings.one": (
        "{count} hallazgo de análisis anteriores está en un lugar omitido: "
        "conserva su estado y no se cuenta como corregido."
    ),
    "report.omitted.findings.other": (
        "{count} hallazgos de análisis anteriores están en lugares omitidos: "
        "conservan su estado y no se cuentan como corregidos."
    ),
    "report.omitted.type.folder": "Carpeta",
    "report.omitted.type.file": "Archivo",
    "report.omitted.type": "Tipo",
    "report.omitted.path": "Ruta",
    "report.omitted.sheet": "Omitido",
    "cli.summary.omitted": "Omitido: {text}",
    "ui.facts.omitted": "No se analizó: {parts}.",
    "report.annex.none": "Ninguna.",
    "report.annex.excluded": "Rutas excluidas",
    "report.annex.stack": "Stack detectado",
    "report.annex.no_stack": "ninguno",
    "report.sbom.note": (
        "Inventario de componentes (SBOM, CycloneDX {version}): {count} componentes. Se entrega "
        "como archivo aparte."
    ),
    "report.scope": "Alcance.",
    "report.risk.vulnerable_dependency": "Dependencia vulnerable: {package}",
    "report.pdf.title": "Reporte de seguridad - {project}",
    "report.pdf.running_header": "Heimdall Guardian - {project}",
    "report.pdf.page": "Página {page} de {total}",
    "report.pdf.analyzed_project": "Proyecto analizado",
    "report.pdf.analysis_date": "Fecha del análisis",
    "report.pdf.hash": "Hash del código (SHA-256)",
    "report.pdf.exceeded_blocking": "Rebasado (impide recibir)",
    "report.pdf.custom_thresholds": (
        "Los umbrales aplicados difieren de los valores institucionales por defecto; los cambios "
        "constan en la bitácora del dictamen."
    ),
    "report.pdf.accepted_intro": (
        "Hallazgos que no cuentan para el dictamen porque se aceptó el riesgo o los descartó como "
        "falso positivo:"
    ),
    "report.pdf.issuer": "Emite",
    "report.pdf.analyzed_code": "Código analizado",
    "report.pdf.sign_here": "Nombre y firma de quien emite",
    "report.pdf.summary": "Resumen",
    "report.pdf.by_severity": (
        "Hallazgos abiertos por severidad. No incluye los aceptados ni los descartados como falso "
        "positivo."
    ),
    "report.pdf.compared": (
        "Respecto a la corrida {previous}: {new} nuevos, {persistent} persistentes, {fixed} "
        "corregidos, {accepted} con riesgo aceptado y {false_positive} descartados como falso "
        "positivo."
    ),
    "report.pdf.ai_summary_intro": (
        "Resumen redactado por IA (requiere validación humana; se elaboró solo con cifras "
        "agregadas):"
    ),
    "report.pdf.example": "Ejemplo cotidiano",
    "report.pdf.coverage": "Cobertura",
    "report.pdf.open": "Abiertos",
    "report.pdf.code_findings": "Hallazgos en el código ({count})",
    "report.pdf.ai_suggestion": " - sugerencia de IA",
    "report.pdf.truncated": (
        "Se muestran los primeros {max}; el resto está en el reporte HTML o en el Excel."
    ),
    "report.pdf.dependencies": "Dependencias vulnerables ({count})",
    "report.pdf.fixed_version": "Versión corregida",
    "report.pdf.no_patch": "sin parche",
    "report.pdf.endpoints": "Endpoints sin autenticación ({open} de {total})",
    "report.pdf.methods": "Métodos",
    "report.pdf.write": "Escritura",
    "report.pdf.all_authenticated": "Todos los endpoints detectados exigen autenticación.",
    "report.pdf.fixed": "Corregidos desde la corrida anterior ({count})",
    "report.xlsx.id": "ID",
    "report.xlsx.severity": "Severidad",
    "report.xlsx.baseline_status": "Estado línea base",
    "report.xlsx.category": "Categoría",
    "report.xlsx.title": "Título",
    "report.xlsx.file": "Archivo",
    "report.xlsx.line": "Línea",
    "report.xlsx.description": "Descripción",
    "report.xlsx.recommendation": "Recomendación",
    "report.xlsx.rule": "Regla",
    "report.xlsx.cwe": "CWE",
    "report.xlsx.owasp": "OWASP",
    "report.xlsx.origin": "Origen",
    "report.xlsx.detected_by": "Detectado por",
    "report.xlsx.owner": "Responsable",
    "report.xlsx.due_date": "Fecha compromiso",
    "report.xlsx.handling_status": "Estado de atención",
    "report.xlsx.notes": "Observaciones",
    "report.xlsx.sheet.findings": "Hallazgos",
    "report.xlsx.sheet.summary": "Resumen",
    "report.xlsx.sheet.owasp": "OWASP Top 10",
    "report.xlsx.sheet.endpoints": "Endpoints",
    "report.xlsx.owasp.category": "Categoría",
    "report.xlsx.owasp.name": "En español",
    "report.xlsx.owasp.covers": "Qué cubre",
    "report.xlsx.summary.project": "Proyecto",
    "report.xlsx.summary.hash": "Hash del código analizado",
    "report.xlsx.summary.by_severity": "Hallazgos abiertos por severidad",
    "report.xlsx.summary.by_status": "Hallazgos por estado",
    "report.xlsx.summary.limitations": "Limitaciones de la corrida",
    "report.xlsx.endpoints.requires_auth": "Requiere autenticación",
    "report.xlsx.endpoints.has_auth": "Tiene autenticación",
    "report.xlsx.endpoints.evidence": "Evidencia",
    "report.error.no_sbom": (
        "Esta corrida no generó SBOM: use el perfil proveedor o el módulo SBOM."
    ),
    "report.error.unsupported_format": "Formato no soportado: {name}. Extensiones: {valid}.",
    "report.risks.cases.one": "{count} caso",
    "report.risks.cases.other": "{count} casos",
    "report.risks.files.one": "{count} archivo",
    "report.risks.files.other": "{count} archivos",
    "core.limit.large_code.one": (
        "{count} archivo(s) de texto pesan más de {limit} KB ({examples}). Sí se analizaron, pero "
        "conviene revisar si son código generado o minificado: ahí es fácil esconder algo."
    ),
    "core.limit.large_code.other": (
        "{count} archivo(s) de texto pesan más de {limit} KB ({examples}). Sí se analizaron, pero "
        "conviene revisar si son código generado o minificado: ahí es fácil esconder algo."
    ),
    "core.limit.oversized.one": (
        "{count} archivo(s) binarios de más de {limit} KB no se analizaron porque no contienen "
        "código ({examples})."
    ),
    "core.limit.oversized.other": (
        "{count} archivo(s) binarios de más de {limit} KB no se analizaron porque no contienen "
        "código ({examples})."
    ),
    "core.limit.symlinks.one": "{count} enlace(s) simbólico(s) ignorados.",
    "core.limit.symlinks.other": "{count} enlace(s) simbólico(s) ignorados.",
    "core.limit.pattern_skipped.one": (
        "{count} archivo quedó fuera por los patrones de archivo ({patterns}), {examples}. "
        "Los manifiestos y archivos de bloqueo siempre se analizan, y los secretos se buscan "
        "en todos los archivos."
    ),
    "core.limit.pattern_skipped.other": (
        "{count} archivos quedaron fuera por los patrones de archivo ({patterns}), {examples}. "
        "Los manifiestos y archivos de bloqueo siempre se analizan, y los secretos se buscan "
        "en todos los archivos."
    ),
    "core.limit.dropped.one": (
        "{count} hallazgo(s) de las herramientas quedaron fuera porque están en carpetas que se "
        "omiten ({examples}). Si alguna importa, quítala de «Carpetas a omitir»."
    ),
    "core.limit.dropped.other": (
        "{count} hallazgo(s) de las herramientas quedaron fuera porque están en carpetas que se "
        "omiten ({examples}). Si alguna importa, quítala de «Carpetas a omitir»."
    ),
    "core.limit.direct_only.one": (
        "{count} manifiesto lista solo dependencias directas y no tiene archivo de bloqueo al lado "
        "({examples}): no se revisaron sus dependencias transitivas. Genera el archivo de "
        "bloqueo (npm install --package-lock-only, composer update --lock, pip-compile o "
        "uv lock, ...) en tu propio entorno y analiza de nuevo."
    ),
    "core.limit.direct_only.other": (
        "{count} manifiestos listan solo dependencias directas y no tienen archivo de bloqueo al "
        "lado ({examples}): no se revisaron sus dependencias transitivas. Genera los archivos de "
        "bloqueo (npm install --package-lock-only, composer update --lock, pip-compile o "
        "uv lock, ...) en tu propio entorno y analiza de nuevo."
    ),
    "core.limit.vendored_found.one": (
        "Se reconoció {count} biblioteca copiada en el proyecto por el encabezado de su versión "
        "({examples}). Se revisa contra la base de vulnerabilidades y su código queda fuera de "
        "las reglas de código."
    ),
    "core.limit.vendored_found.other": (
        "Se reconocieron {count} bibliotecas copiadas en el proyecto por el encabezado de su "
        "versión ({examples}). Se revisan contra la base de vulnerabilidades y su código queda "
        "fuera de las reglas de código."
    ),
    "core.limit.vendored_sast.one": (
        "{count} hallazgo de las reglas de código dentro de una biblioteca copiada quedó fuera "
        "({examples}): es código de terceros. Sus vulnerabilidades conocidas se reportan por "
        "versión."
    ),
    "core.limit.vendored_sast.other": (
        "{count} hallazgos de las reglas de código dentro de bibliotecas copiadas quedaron fuera "
        "({examples}): es código de terceros. Sus vulnerabilidades conocidas se reportan por "
        "versión."
    ),
    "core.limit.untracked_versioned.one": (
        "{count} hallazgo en un archivo que git no versiona quedó fuera ({examples}): la regla "
        "solo aplica a archivos versionados. Si el archivo se comparte por otro medio, "
        "quítale también los secretos."
    ),
    "core.limit.untracked_versioned.other": (
        "{count} hallazgos en archivos que git no versiona quedaron fuera ({examples}): la regla "
        "solo aplica a archivos versionados. Si los archivos se comparten por otro medio, "
        "quítales también los secretos."
    ),
    "adapter.opengrep.partial.one": (
        "Opengrep no pudo analizar por completo {count} archivo(s) o regla(s)."
    ),
    "adapter.opengrep.partial.other": (
        "Opengrep no pudo analizar por completo {count} archivo(s) o regla(s)."
    ),
    "llm.limit.triage_budget.one": (
        "IA: {count} hallazgo(s) sin triage por el presupuesto de la corrida."
    ),
    "llm.limit.triage_budget.other": (
        "IA: {count} hallazgo(s) sin triage por el presupuesto de la corrida."
    ),
    "llm.limit.sink_budget.one": "IA: {count} punto(s) de riesgo sin revisar por el presupuesto.",
    "llm.limit.sink_budget.other": "IA: {count} punto(s) de riesgo sin revisar por el presupuesto.",
    "llm.limit.endpoint_budget.one": "IA: {count} endpoint(s) sin revisar por el presupuesto.",
    "llm.limit.endpoint_budget.other": "IA: {count} endpoint(s) sin revisar por el presupuesto.",
    "authz.limit.undetermined.one": (
        "{count} endpoint(s) con protección no determinada: revisar el inventario."
    ),
    "authz.limit.undetermined.other": (
        "{count} endpoint(s) con protección no determinada: revisar el inventario."
    ),
    "report.verdict.accepted.one": (
        "{count} hallazgo(s) no cuentan porque se aceptó el riesgo o se descartaron: {ids}."
    ),
    "report.verdict.accepted.other": (
        "{count} hallazgo(s) no cuentan porque se aceptó el riesgo o se descartaron: {ids}."
    ),
    "report.pdf.mediums.one": (
        "Además hay {count} hallazgo(s) de severidad media abiertos, que se reciben con compromiso "
        "de corrección."
    ),
    "report.pdf.mediums.other": (
        "Además hay {count} hallazgo(s) de severidad media abiertos, que se reciben con compromiso "
        "de corrección."
    ),
    "owasp.what_is": (
        "OWASP es una fundación sin fines de lucro dedicada a mejorar la seguridad del software. "
        "Con datos de miles de aplicaciones reales publica cuáles son los riesgos más comunes. Su "
        "lista «Top 10» es la referencia más usada en el mundo para hablar de seguridad de "
        "aplicaciones; la edición más reciente es la de 2025."
    ),
    "owasp.scope_warning": (
        "Cubrir categorías del Top 10 no significa que no existan otros riesgos. Heimdall Guardian "
        "lee el código sin ejecutarlo: no sustituye una revisión humana ni las pruebas de "
        "penetración."
    ),
    "owasp.A01.name": "Control de acceso roto",
    "owasp.A01.explanation": (
        "Alguien puede ver o hacer algo que no le corresponde. También incluye que el sistema haga "
        "peticiones a direcciones que elige un atacante."
    ),
    "owasp.A01.example": (
        "Alguien cambia un número en la dirección web y ve los datos de otra persona."
    ),
    "owasp.A01.coverage_note": (
        "Inventario de endpoints sin autenticación, reglas de acceso a objetos ajenos, rutas de "
        "archivo, redirecciones y peticiones a direcciones elegidas por el usuario. La revisión de "
        "endpoints con IA solo sugiere."
    ),
    "owasp.A02.name": "Configuración de seguridad incorrecta",
    "owasp.A02.explanation": (
        "El sistema queda con ajustes de fábrica o de desarrollo que lo dejan expuesto."
    ),
    "owasp.A02.example": (
        "Una aplicación en producción sigue en modo de pruebas y muestra sus errores internos."
    ),
    "owasp.A02.coverage_note": (
        "Reglas de configuración (modo de depuración, CORS, cookies, errores visibles) y revisión "
        "de archivos de configuración e infraestructura como código."
    ),
    "owasp.A03.name": "Fallas en la cadena de suministro de software",
    "owasp.A03.explanation": (
        "Se usan componentes de terceros con fallas conocidas, o se compromete la forma en que el "
        "software se construye y se entrega."
    ),
    "owasp.A03.example": (
        "La aplicación usa una librería con una falla pública que ya tiene arreglo."
    ),
    "owasp.A03.coverage_note": (
        "Dependencias con vulnerabilidades conocidas e inventario de componentes (SBOM). No revisa "
        "la integridad del proceso de compilación ni de publicación."
    ),
    "owasp.A04.name": "Fallas criptográficas",
    "owasp.A04.explanation": (
        "Los datos sensibles se protegen mal o no se protegen: cifrado débil, claves visibles o "
        "contraseñas guardadas sin cuidado."
    ),
    "owasp.A04.example": (
        "Las contraseñas de los usuarios se guardan con un método que se descifra en minutos."
    ),
    "owasp.A04.coverage_note": (
        "Criptografía débil, aleatoriedad predecible y secretos escritos en el código. No revisa "
        "el cifrado en tránsito ni en reposo de la infraestructura."
    ),
    "owasp.A05.name": "Inyección",
    "owasp.A05.explanation": (
        "Un dato que escribe el usuario se interpreta como una instrucción y el sistema la "
        "ejecuta. Incluye las inyecciones de SQL, de comandos y de código en páginas (XSS)."
    ),
    "owasp.A05.example": (
        "Alguien escribe una instrucción en un campo de búsqueda y obtiene toda la base de datos."
    ),
    "owasp.A05.coverage_note": (
        "Reglas de inyección SQL, NoSQL, de comandos, de código y de scripts en páginas (XSS) para "
        "los lenguajes soportados."
    ),
    "owasp.A06.name": "Diseño inseguro",
    "owasp.A06.explanation": (
        "El problema no está en un error de programación sino en cómo se pensó el sistema: faltan "
        "controles desde el diseño."
    ),
    "owasp.A06.example": (
        "Un trámite permite repetir un cupón de descuento sin límite porque nadie previó el abuso."
    ),
    "owasp.A06.coverage_note": (
        "Solo sugerencias de la IA sobre flujos de negocio y algunas reglas de diseño (carga de "
        "archivos, asignación masiva). El diseño requiere revisión humana."
    ),
    "owasp.A07.name": "Fallas de autenticación",
    "owasp.A07.explanation": (
        "El sistema no comprueba bien quién es cada persona, o permite que alguien se haga pasar "
        "por otra."
    ),
    "owasp.A07.example": (
        "Una clave de acceso quedó escrita en el código y cualquiera con el archivo entra."
    ),
    "owasp.A07.coverage_note": (
        "Secretos expuestos, tokens JWT mal verificados, sesiones y cookies inseguras. No prueba "
        "contraseñas débiles ni segundo factor de autenticación."
    ),
    "owasp.A08.name": "Fallas de integridad de software o datos",
    "owasp.A08.explanation": (
        "El sistema confía en código o datos que nadie verificó y que pudieron alterarse."
    ),
    "owasp.A08.example": (
        "La aplicación reconstruye objetos a partir de datos recibidos y un atacante los manipula."
    ),
    "owasp.A08.coverage_note": (
        "Deserialización insegura de datos externos. No revisa firmas de actualizaciones ni "
        "canales de entrega."
    ),
    "owasp.A09.name": "Fallas de registro y alertas de seguridad",
    "owasp.A09.explanation": (
        "Los eventos importantes no se registran o nadie se entera a tiempo de un ataque."
    ),
    "owasp.A09.example": (
        "Alguien prueba miles de contraseñas durante una semana y nadie recibe un aviso."
    ),
    "owasp.A09.coverage_note": (
        "Un análisis del código no puede saber si hay vigilancia y alertas en operación."
    ),
    "owasp.A10.name": "Manejo inadecuado de condiciones excepcionales",
    "owasp.A10.explanation": (
        "El sistema reacciona mal ante errores o situaciones inesperadas: se cae, se abre o revela "
        "información."
    ),
    "owasp.A10.example": (
        "Ante un error, el sistema deja pasar la operación en lugar de bloquearla."
    ),
    "owasp.A10.coverage_note": (
        "Heimdall Guardian no tiene reglas para esta categoría: un análisis del código no ve cómo "
        "reacciona el sistema ante fallas en operación."
    ),
    "owasp.hint.CWE-16": (
        "Abre el archivo de configuración del entorno de producción y compare el valor con el "
        "recomendado: modo de depuración apagado, orígenes acotados y sin valores de prueba."
    ),
    "owasp.hint.CWE-20": (
        "Sigue el dato desde donde entra hasta donde se usa y confirma que se valida tipo, "
        "longitud y formato antes de usarlo."
    ),
    "owasp.hint.CWE-22": (
        "Sigue el parámetro hasta la función que abre el archivo y confirma que la ruta se "
        "normaliza y se limita a un directorio base. Prueba con `../` en un entorno de pruebas."
    ),
    "owasp.hint.CWE-78": (
        "Revisa si el texto del comando se arma con datos del usuario. Debe usarse una lista de "
        "argumentos sin intérprete de comandos y con valores permitidos."
    ),
    "owasp.hint.CWE-79": (
        "Localiza dónde se imprime el dato en la página y confirma que se escapa según el contexto "
        "(HTML, atributo o script). Prueba con un texto como `<b>x</b>` en pruebas."
    ),
    "owasp.hint.CWE-89": (
        "Revisa si la consulta se arma uniendo texto con datos del usuario. Debe usar parámetros "
        "enlazados; comprueba que ningún dato llegue a la consulta como texto."
    ),
    "owasp.hint.CWE-94": (
        "Busca si algún dato externo llega a una función que ejecuta código. Sustitúyela por una "
        "lista cerrada de operaciones permitidas."
    ),
    "owasp.hint.CWE-95": (
        "Busca si algún dato externo llega a `eval` o equivalente. Sustitúyelo por una lista "
        "cerrada de operaciones o por un análisis seguro del dato."
    ),
    "owasp.hint.CWE-98": (
        "Revisa si la ruta del archivo incluido depende de un dato externo. Debe elegirse de una "
        "lista fija, nunca construirse con la entrada."
    ),
    "owasp.hint.CWE-209": (
        "Provoca un error en un entorno de pruebas y revisa si la respuesta muestra rutas, "
        "consultas o trazas. Producción solo debe mostrar un mensaje genérico."
    ),
    "owasp.hint.CWE-259": (
        "Busca la contraseña escrita en el código y confirma si está vigente. Si lo está, cámbiala "
        "y muévela a un gestor de secretos."
    ),
    "owasp.hint.CWE-285": (
        "Comprueba que la acción verifica el permiso de quien la pide, no solo que haya iniciado "
        "sesión. Prueba con una cuenta sin ese permiso."
    ),
    "owasp.hint.CWE-295": (
        "Revisa si se desactiva la validación de certificados. Debe validarse siempre la cadena de "
        "confianza y el nombre del servidor."
    ),
    "owasp.hint.CWE-306": (
        "Revisa la ruta y sus decoradores, middleware o filtros globales. Prueba la petición sin "
        "credenciales en un entorno de pruebas: debe responder 401 o 403."
    ),
    "owasp.hint.CWE-311": (
        "Confirma con el equipo de infraestructura si el dato viaja o se guarda sin cifrar y qué "
        "mecanismo de cifrado se usa."
    ),
    "owasp.hint.CWE-319": (
        "Revisa la configuración del servidor y del cliente: la comunicación debe usar TLS. "
        "Comprueba que no haya direcciones `http://` hacia servicios con datos."
    ),
    "owasp.hint.CWE-312": (
        "Revisa dónde se guarda el dato: en el dispositivo, SharedPreferences y GetStorage son "
        "archivos legibles. Los datos sensibles deben ir en el llavero (flutter_secure_storage)."
    ),
    "owasp.hint.CWE-326": (
        "Comprueba el tamaño de clave o la longitud usada y compárelos con la guía vigente del "
        "algoritmo (por ejemplo, AES de 128 bits o más y RSA de 2048 o más)."
    ),
    "owasp.hint.CWE-327": (
        "Identifica para qué se usa el algoritmo. Si protege contraseñas o datos, sustitúyelo por "
        "uno vigente (Argon2, bcrypt o scrypt; AES-GCM). MD5 o SHA-1 solo sirven para sumas de "
        "verificación sin valor de seguridad."
    ),
    "owasp.hint.CWE-330": (
        "Confirma si el valor aleatorio protege algo (token, contraseña temporal). Si es así, debe "
        "salir de un generador criptográfico, no de uno de uso general."
    ),
    "owasp.hint.CWE-345": (
        "Revisa si el dato se acepta sin comprobar su origen o integridad. Debe verificarse una "
        "firma o un código de autenticación antes de usarlo."
    ),
    "owasp.hint.CWE-347": (
        "Revisa cómo se decodifica el token: debe verificarse la firma con la clave correcta y un "
        "algoritmo fijo, nunca el que indique el propio token."
    ),
    "owasp.hint.CWE-352": (
        "Comprueba si la acción cambia datos y si exige un token anti-CSRF o una cookie con "
        "SameSite. Prueba enviar la petición desde otro sitio en pruebas."
    ),
    "owasp.hint.CWE-377": (
        "Revisa cómo se crean los archivos temporales: deben usar funciones que generen nombres "
        "impredecibles y con permisos restringidos."
    ),
    "owasp.hint.CWE-400": (
        "Comprueba si hay límites de tamaño, tiempo o número de peticiones en la operación "
        "señalada y pruebe con una entrada grande en pruebas."
    ),
    "owasp.hint.CWE-434": (
        "Revisa la validación del archivo subido: tipo real, extensión permitida, tamaño máximo, "
        "nombre regenerado y carpeta fuera de la que sirve el servidor web."
    ),
    "owasp.hint.CWE-477": (
        "Busca el componente obsoleto en el código y en las dependencias. Confirma con la "
        "documentación del fabricante cuál lo reemplaza y qué versión ya no recibe correcciones."
    ),
    "owasp.hint.CWE-489": (
        "Confirma en el entorno de producción que el modo de depuración está apagado y que ninguna "
        "consola de desarrollo es accesible."
    ),
    "owasp.hint.CWE-502": (
        "Identifica de dónde vienen los datos que se deserializan. Si no son de confianza total, "
        "usa un formato de datos simple (JSON) con validación de esquema."
    ),
    "owasp.hint.CWE-601": (
        "Revisa si el destino de la redirección sale de un dato de la petición. Debe compararse "
        "con una lista de destinos permitidos o limitarse a rutas internas."
    ),
    "owasp.hint.CWE-605": (
        "Revisa si el servicio escucha en todas las interfaces y si es necesario; limita la "
        "dirección de escucha a la que se requiere."
    ),
    "owasp.hint.CWE-611": (
        "Revisa el analizador XML: deben desactivarse las entidades externas y las definiciones de "
        "tipo de documento."
    ),
    "owasp.hint.CWE-614": (
        "Revisa los atributos de la cookie de sesión: debe llevar `Secure` y `HttpOnly`. "
        "Compruébalo en las herramientas del navegador."
    ),
    "owasp.hint.CWE-639": (
        "Prueba con dos cuentas distintas en un entorno de pruebas: la cuenta A pide el "
        "identificador de un registro de B y debe recibir 403 o 404."
    ),
    "owasp.hint.CWE-703": (
        "Revisa qué ocurre cuando falla la operación: el error no debe ignorarse en silencio ni "
        "dejar el sistema en un estado que permita el acceso."
    ),
    "owasp.hint.CWE-732": (
        "Revisa los permisos del archivo o recurso: solo debe poder leerlo o escribirlo quien lo "
        "necesita."
    ),
    "owasp.hint.CWE-532": (
        "Revisa qué valores llegan a print, debugPrint o al logger. Los tokens, contraseñas y "
        "datos de tarjeta no deben aparecer; prueba la app y lee el registro con `adb logcat`."
    ),
    "owasp.hint.CWE-749": (
        "Revisa qué funciones de la aplicación puede invocar la página del WebView. Deben ser las "
        "mínimas, con la página limitada a tu dominio por https y cada mensaje validado."
    ),
    "owasp.hint.CWE-798": (
        "Busca el valor en el historial de versiones y confirma si sigue vigente. Si lo está, "
        "rótalo de inmediato y muévelo a un gestor de secretos."
    ),
    "owasp.hint.CWE-841": (
        "Recorre el flujo de negocio paso a paso en pruebas y verifica que cada paso comprueba el "
        "estado del anterior; intenta saltarse o repetir pasos."
    ),
    "owasp.hint.CWE-915": (
        "Revisa qué campos acepta el modelo desde la petición. Debe existir una lista explícita de "
        "campos permitidos; comprueba que no se pueda enviar, por ejemplo, un rol."
    ),
    "owasp.hint.CWE-916": (
        "Revisa cómo se guardan las contraseñas: deben usar un algoritmo lento con sal (Argon2, "
        "bcrypt o scrypt), nunca MD5, SHA-1 ni SHA-256 simple."
    ),
    "owasp.hint.CWE-918": (
        "Revisa si la dirección que consulta el servidor viene de la petición. Debe validarse "
        "contra una lista de destinos permitidos y bloquear direcciones internas."
    ),
    "owasp.hint.CWE-926": (
        'Abre AndroidManifest.xml y revisa cada componente con android:exported="true": '
        "¿necesita recibir llamadas de otras aplicaciones? Si no, ponlo en false; si sí, exige un "
        "permiso de firma y prueba con `adb shell am start` que rechaza datos inválidos."
    ),
    "owasp.hint.CWE-927": (
        "Busca los PendingIntent y confirma que llevan FLAG_IMMUTABLE e Intent explícito. En los "
        "broadcast, comprueba que lo enviado no es sensible o que solo lo recibe tu aplicación "
        "(setPackage o un permiso de firma)."
    ),
    "owasp.hint.CWE-942": (
        "Revisa la configuración de CORS: los orígenes deben ser una lista concreta; un origen "
        "abierto con credenciales permite que otros sitios lean datos de sesión."
    ),
    "owasp.hint.CWE-943": (
        "Revisa si el filtro de la consulta se arma con objetos que envía el usuario. Debe "
        "validarse que cada valor sea del tipo esperado (texto, número) antes de usarlo."
    ),
    "owasp.hint.CWE-80": (
        "Localiza dónde se imprime el dato en la página y confirma que los caracteres "
        "especiales de HTML se escapan. Prueba con un texto como `<b>x</b>` en pruebas."
    ),
    "owasp.hint.CWE-155": (
        "Revisa si datos del usuario llegan a un patrón o comodín (glob, expansión del shell) y "
        "confirma que los caracteres comodín se escapan o se rechazan."
    ),
    "owasp.hint.CWE-284": (
        "Revisa quién puede llegar al recurso y confirma que la verificación de acceso se hace "
        "en el servidor en cada petición, no solo en la interfaz."
    ),
    "owasp.hint.CWE-494": (
        "Revisa qué se descarga y cómo se verifica. El código o archivo debe comprobarse contra "
        "una suma de verificación o firma fijada antes de usarse."
    ),
    "owasp.hint.CWE-838": (
        "Revisa dónde se escribe el dato (HTML, URL, script, consulta) y confirma que se codifica "
        "para ese contexto antes de imprimirse."
    ),
    "owasp.hint.CWE-1004": (
        "Revisa los atributos de la cookie de sesión: debe llevar `HttpOnly` para que los scripts "
        "de la página no la lean."
    ),
    "adapter.opengrep.default_recommendation": "Revisar y corregir el código señalado.",
    "adapter.bandit.recommendation": (
        "Revisar el uso señalado y aplicar la alternativa segura que describe la referencia."
    ),
    "adapter.gitleaks.title_code": "Secreto en el código: {rule}",
    "adapter.gitleaks.title_history": "Secreto en el historial de git: {rule}",
    "adapter.gitleaks.description_code": "Secreto embebido en el código actual.{detector}",
    "adapter.gitleaks.description_history": (
        "Secreto presente en el historial de git (commit {commit}, {date}). Borrarlo del código"
        " no lo elimina del repositorio.{detector}"
    ),
    "adapter.gitleaks.detector": " Detector: {detail}.",
    "adapter.gitleaks.rec_code": (
        "Revocar y rotar la credencial de inmediato. Retirarla del código y cargarla desde"
        " variables de entorno o un gestor de secretos."
    ),
    "adapter.gitleaks.rec_history": (
        "Revocar y rotar la credencial aunque ya no esté en el código: sigue siendo recuperable"
        " desde el historial de git."
    ),
    "adapter.dependency.title": "{package} {installed} tiene una vulnerabilidad conocida ({id})",
    "adapter.dependency.description": "Dependencia con vulnerabilidad conocida. {summary}",
    "adapter.dependency.rec_no_fix": (
        "Aún no hay versión corregida publicada: evaluar mitigaciones o sustituir la dependencia."
    ),
    "adapter.osv.rec_fixed": "Actualizar {package} a una versión corregida: {versions}.",
    "adapter.vendored.rec_fixed": (
        "Sustituye el archivo copiado de {package} por la versión {versions} o posterior, o "
        "cárgalo con un gestor de paquetes para que se mantenga auditado."
    ),
    "adapter.vendored.rec_no_fix": (
        "Aún no hay versión corregida de {package}: evalúa mitigaciones o sustituye la "
        "biblioteca copiada."
    ),
    "adapter.trivy.rec_fixed": "Actualizar {package} a la versión {version} o posterior.",
    "adapter.trivy.default_resolution": "Corregir la configuración señalada.",
    "authz.kind.write": "de escritura",
    "authz.kind.read": "de lectura",
    "authz.route": "{methods} {path}",
    "authz.finding.title": "Endpoint {kind} sin autenticación: {route}",
    "authz.finding.description": (
        "El endpoint {kind} {path} (métodos: {methods}), atendido por {handler}, no exige"
        " autenticación: {evidence}.{declared}{note}"
    ),
    "authz.finding.declared_in": " La ruta se declara en {file}.",
    "authz.finding.note_public": " Por su nombre podría ser público por diseño; confirmarlo.",
    "authz.finding.note_any_method": " No declara métodos, así que acepta cualquiera.",
    "authz.finding.recommendation": (
        "Exigir autenticación en el endpoint (decorador, mixin, atributo o middleware según el"
        " framework) y validar además el permiso sobre el recurso. Si debe ser público, aceptar"
        " el hallazgo con justificación."
    ),
    "authz.ev.login_middleware": "LoginRequiredMiddleware en settings",
    "authz.ev.drf_default_open": "sin permission_classes y sin permiso por defecto restrictivo",
    "authz.ev.drf_default_settings": "DEFAULT_PERMISSION_CLASSES en settings",
    "authz.ev.django_no_decorator": "sin decorador de autenticación",
    "authz.ev.django_no_mixin": "sin mixin de autenticación",
    "authz.ev.django_admin": "sitio de administración de Django",
    "authz.ev.django_generic_no_mixin": "vista genérica de Django sin mixin",
    "authz.ev.view_not_found": "no se pudo localizar la vista",
    "authz.ev.url_wrapper": "{wrappers}(...) en {file}",
    "authz.ev.net_anonymous_action": "[AllowAnonymous] en la acción",
    "authz.ev.net_authorize_action": "[Authorize] en la acción",
    "authz.ev.net_anonymous_controller": "[AllowAnonymous] en el controlador",
    "authz.ev.net_authorize_controller": "[Authorize] en el controlador",
    "authz.ev.net_global_policy": "política de autorización global",
    "authz.ev.net_none": "sin [Authorize] ni política global",
    "authz.ev.net_anonymous_route": "AllowAnonymous en la ruta",
    "authz.ev.net_require_route": "RequireAuthorization en la ruta",
    "authz.ev.net_route_none": "sin RequireAuthorization ni política global",
    "authz.ev.laravel_constructor": "middleware de autenticación en el constructor del controlador",
    "authz.ev.laravel_outside": "fuera de un grupo o cadena con middleware de autenticación",
    "authz.ev.php_session": "verifica la sesión en el propio archivo",
    "authz.ev.php_basic_auth": "verifica la autenticación básica HTTP en el propio archivo",
    "authz.ev.php_includes": "incluye {file}",
    "authz.ev.php_none": "sin verificación de sesión ni inclusión de un archivo de acceso",
    "authz.ev.php_script": (
        "ejecuta código al cargarse (parece un script programado o de mantenimiento) "
        "sin verificación de sesión ni protección de solo línea de comandos"
    ),
    "authz.ev.guard_empty": "<vacío>",
    "authz.ev.guard_inline": "<middleware anónimo que revisa sesión o token>",
    "authz.ev.guard_handler": "verificación dentro del manejador",
    "authz.ev.guard_item": "{text} ({origin})",
    "authz.ev.guard_auth": "{noun} de autenticación: {items}",
    "authz.ev.guard_unknown": "{noun} sin identificar que podría autenticar: {items}",
    "authz.ev.origin_route": "en la ruta",
    "authz.ev.origin_global_guard": "guard global",
    "authz.ev.origin_use_guards": "@UseGuards en {where}",
    "authz.ev.where_method": "el método",
    "authz.ev.where_class": "la clase",
    "authz.ev.express_none": (
        "sin middleware de autenticación en la ruta ni en {router}.use() previos"
    ),
    "authz.ev.nest_public": "{decorator} en {where}: pública por decorador",
    "authz.ev.nest_public_guarded": (
        "{decorator} en {where}, pero también hay guards explícitos: revisar"
    ),
    "authz.ev.nest_none": "sin @UseGuards de autenticación ni guard global",
    "core.ai_stats.profile": "Perfil de análisis",
    "core.ai_stats.files": "Archivos analizados",
    "core.ai_stats.stacks": "Tecnologías detectadas",
    "core.ai_stats.none": "ninguna",
    "core.ai_stats.open_total": "Hallazgos abiertos en total",
    "core.ai_stats.by_severity": "Hallazgos de severidad {name}",
    "core.ai_stats.by_category": "Hallazgos de categoría {name}",
    "core.ai_stats.endpoints": "Endpoints detectados",
    "core.ai_stats.endpoints_open": "Endpoints sin autenticación",
    "core.ai_stats.ai_new": "Posibles problemas que la IA encontró más allá de las reglas",
    "core.ai_stats.frequent": "Tipos de hallazgo más frecuentes",
    "cli.rules.help": (
        "revisa tus propios archivos de reglas (carpetas extra en config.toml o --carpeta)"
    ),
    "cli.rules.check": "valida los archivos de reglas e informa los problemas (acción por defecto)",
    "cli.rules.dir": (
        "carpeta con archivos de reglas; repítela para varias (por defecto, las configuradas)"
    ),
    "cli.rules.none": (
        "No hay carpetas de reglas extra configuradas. Agrega extra_dirs en [rules] de "
        "config.toml o usa --carpeta."
    ),
    "cli.rules.ok": "OK     ",
    "cli.rules.invalid": "INVÁLIDA",
    "cli.rules.no_engine": "El motor de reglas no pudo validar la sintaxis: {error}",
    "core.limit.user_rule_problem": "Se omitieron tus propias reglas. {file}: {detail}",
    "adapter.opengrep.user_rule_invalid": (
        "Se omitió tu archivo de reglas {file} porque el motor lo rechazó: {detail}"
    ),
    "core.user_rules.missing_dir": "La carpeta de reglas {dir} no existe.",
    "core.user_rules.inside_project": (
        "La carpeta de reglas {dir} está dentro del proyecto analizado, así que se ignoró: el"
        " código analizado no puede configurar el análisis."
    ),
    "core.user_rules.too_many_files": (
        "La carpeta de reglas {dir} tiene más de {limit} archivos; solo se leyeron los "
        "primeros {limit}."
    ),
    "core.user_rules.file_too_big": "El archivo pesa más de {limit_kb} KB.",
    "core.user_rules.unreadable": "No se puede leer el archivo: {error}",
    "core.user_rules.bad_yaml": "El archivo no es YAML válido: {error}",
    "core.user_rules.no_rules": (
        "El archivo debe ser un mapa con una lista `rules` que no esté vacía."
    ),
    "core.user_rules.rule_not_mapping": "Regla {rule}: cada regla debe ser un mapa.",
    "core.user_rules.missing_field": "Regla {rule}: falta `{field}` o está vacío.",
    "core.user_rules.bad_id": (
        "Regla {rule}: el ID debe verse como PREFIJO-ETIQUETA-001 (mayúsculas y tres dígitos)."
    ),
    "core.user_rules.reserved_id": (
        "Regla {rule}: el prefijo AI- y la etiqueta CAND están reservados para Heimdall Guardian."
    ),
    "core.user_rules.builtin_id": "Regla {rule}: el ID ya lo usa una regla incluida.",
    "core.user_rules.duplicate_id": (
        "Regla {rule}: el ID está definido más de una vez en tus reglas."
    ),
    "core.user_rules.no_matcher": (
        "Regla {rule}: necesita `pattern`, `patterns`, `pattern-either`, `pattern-regex`, o "
        "modo taint con `pattern-sources` y `pattern-sinks`."
    ),
    "core.user_rules.bad_cwe": "Regla {rule}: `metadata.cwe` debe verse como CWE-89, no {value}.",
    "core.user_rules.owasp_2021": (
        "Regla {rule}: {value} es una etiqueta OWASP 2021; usa la de 2025: {suggestion}."
    ),
    "core.user_rules.bad_owasp": (
        "Regla {rule}: {value} no es una etiqueta de OWASP Top 10:2025 (por ejemplo A05:2025 "
        "Injection)."
    ),
    "core.user_rules.bad_value": "Regla {rule}: `{field}` vale {value}; usa uno de: {expected}.",
}
