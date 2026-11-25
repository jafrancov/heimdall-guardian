# Revisar hallazgos

## Detalle de un hallazgo

Abre un hallazgo y, en **Para especialistas**, verás la regla, la herramienta, el CWE y la
categoría OWASP, la confianza, la ubicación exacta (`archivo:línea`) y, cuando existe,
**Cómo verificarlo** sin ejecutar el código ajeno. La misma guía aparece en cada hallazgo del
reporte HTML y en el [Catálogo de reglas](rules/index.md).

## Aceptar un riesgo o marcar un falso positivo

```bash
uv run hdl suppress <carpeta> HDL-2026-000012 --status accepted \
  --reason "Sistema interno, no expuesto" --review 2027-01-31
```

- `--status` es `accepted` o `false_positive`.
- La justificación es obligatoria. Cuando pasa la fecha de revisión, el hallazgo vuelve a
  contar.
- El cambio se ve de inmediato en el último análisis y en sus reportes.
- `hdl suppressions <carpeta>` las lista y `hdl unsuppress <carpeta> <id>` retira una.

## Por dónde empezar

**Por dónde empezar** (en la app y en cada reporte) agrupa los hallazgos abiertos por
causa común, del más grave al menos: una línea por paquete vulnerable con la versión que
corrige todos sus hallazgos, y una por regla con cuántos hallazgos y archivos abarca. No
incluye las sugerencias de IA.

## Carpetas a omitir

Por omisión se saltan las carpetas de dependencias y de salida: `node_modules`, `venv`,
`.venv`, `vendor`, `bin`, `obj`, `dist`, `build`, `static/CACHE` y `migrations`.

- En la aplicación: **Carpetas a omitir**, se recuerda por proyecto.
- En la línea de comandos: `--exclude generado` o `--include build`.
- Para todos los proyectos: `exclude_extra` e `include_extra` en [`config.toml`](configuration.md).

También puedes omitir archivos por patrón: cualquier entrada con `*`, `?` o `[` es un
patrón de archivo (`--exclude '*.spec.ts'`, `docs/*.md`, o el campo **Archivos a omitir**).
Un patrón sin `/` se compara con el nombre del archivo; con `/`, con la ruta completa. Los
manifiestos y lockfiles (`package.json`, `package-lock.json`...) siempre se analizan, y los
secretos se buscan en todos los archivos.

Heimdall también *sugiere* carpetas según el stack detectado (`.next` y `coverage` en Node,
`Pods` y `DerivedData` en Swift, `.dart_tool` en Flutter...) y carpetas de editor o de
asistente de IA (`.context`, `.agents`, `.claude`, `.cursor`, `.idea`, `.vscode`). Aparecen
arriba en **Carpetas a omitir** y en `--dry-run`; no se omite nada hasta que guardes. Si
recibes código de un proveedor, las de editor y asistente empiezan sin marcar, porque ahí
se puede esconder código. También se sugieren las carpetas del `.gitignore` del proyecto, pero
solo como sugerencia: lo que dice el código analizado nunca configura el análisis.

Si la carpeta tiene varios proyectos separados (por ejemplo `api/`, `ios/` y `backend/`,
cada uno con su manifiesto y ninguno en la raíz), la aplicación los lista bajo el nombre
de la carpeta: analízala completa, o haz clic en uno para analizarlo por separado.
`--dry-run` también los lista.

Los reportes listan lo que no se analizó (carpetas y archivos omitidos). Los hallazgos de
análisis anteriores que quedan en un lugar que ahora omites cuentan como *omitidos*:
conservan su estado y nunca se reportan como corregidos.

`hdl scan <carpeta> --dry-run` y **Vista previa** muestran qué archivos entran.

## Línea base

Heimdall guarda una línea base por proyecto: entre un análisis y el siguiente, cada hallazgo
es `new`, `persistent` o `fixed`. La huella ignora el número de línea, así que mover código
no crea hallazgos nuevos. Comparte una línea base con otra persona o equipo:

```bash
uv run hdl baseline <carpeta> --export .heimdall-baseline.json
uv run hdl baseline <otra-carpeta> --import .heimdall-baseline.json
```

## SARIF en tu editor

```bash
uv run hdl scan <carpeta> --output resultado.sarif
```

Los editores y GitHub muestran los resultados SARIF sobre la línea de código.
