# Tus propias reglas

Puedes sumar tus propias reglas de [Opengrep](https://opengrep.dev) a las incluidas, por
ejemplo para revisar una convención de tu empresa. Son archivos YAML con el mismo formato
que las reglas incluidas.

## Dónde ponerlas

Usa una carpeta **fuera** del proyecto que analizas, por ejemplo `~/heimdall-rules`. Una
carpeta dentro del proyecto analizado se ignora: el código analizado nunca debe configurar
el análisis, y un proveedor podría incluir reglas que oculten hallazgos.

Dile a Heimdall Guardian dónde está, en `config.toml`:

```toml
[rules]
extra_dirs = ["~/heimdall-rules"]
```

o en **Configuración → Tus propias reglas** en la aplicación, donde **Revisar reglas**
muestra el resultado al momento. Se lee cada archivo `.yaml` y `.yml` de esas carpetas.

## Formato

```yaml
rules:
  - id: ACME-SQL-001
    languages: [php]
    message: Query built by concatenating user input.
    pattern: $DB->query("..." . $_GET[...] . "...")
    severity: ERROR
    metadata:
      cwe: CWE-89
      owasp: "A05:2025 Injection"
      severity_hdl: high          # critical | high | medium | low | info
      confidence: medium          # high | medium | low
      title: SQL query built from user input
      recommendation: Use prepared statements with bound parameters.
      title_es: Consulta SQL armada con datos del usuario     # opcional
      recommendation_es: Usa consultas preparadas con parámetros.   # opcional
    message_es: Consulta armada concatenando datos del usuario.   # opcional
```

Son obligatorios `languages`, `message`, un criterio de búsqueda (`pattern`, `patterns`,
`pattern-either`, `pattern-regex` o una regla de flujo de datos) y la metadata de arriba.
`owasp` usa las etiquetas de 2025.

## IDs

Un ID tiene la forma `XX-TAG-NNN` (`ACME-SQL-001`). La etiqueta decide dónde cae el
hallazgo: `CONF` es configuración, `AUTH` e `IDOR` son control de acceso y cualquier otra es
código. No puedes reutilizar el ID de una regla incluida ni repetir un ID en tus reglas, y
el prefijo `AI-` y la etiqueta `CAND` están reservados.

## Qué se revisa

Antes de cada análisis se revisa la estructura de cada archivo y luego el motor valida su
sintaxis. Un archivo con problemas se omite completo, el análisis sigue y el resultado
declara qué archivo se omitió y por qué. Para revisar sin analizar:

```bash
uv run hdl rules --check             # las carpetas configuradas
uv run hdl rules --check --dir ~/heimdall-rules
```

## En los reportes

Los reportes registran los archivos y los IDs de tus reglas, y estas cambian la versión de
las reglas, así que un resultado se puede rastrear hasta las reglas exactas que lo produjeron.
