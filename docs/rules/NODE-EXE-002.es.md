# NODE-EXE-002: Ejecución de código con datos de la petición (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Datos de la petición se evalúan como código JavaScript (eval, new Function, vm.runIn*Context, new vm.Script o setTimeout/setInterval con texto): permite ejecutar código arbitrario en el servidor.

## Cómo corregirlo

Eliminar eval, new Function y vm sobre datos del usuario. Para expresiones o formatos de datos usar un analizador específico (JSON.parse, una librería de expresiones sin ejecución) y, para lógica variable, una lista blanca de operaciones.

## Por qué importa

Esta regla corresponde a [CWE-95](https://cwe.mitre.org/data/definitions/95.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Busca si algún dato externo llega a `eval` o equivalente. Sustitúyelo por una lista cerrada de operaciones o por un análisis seguro del dato.

## Datos

| | |
|---|---|
| Severidad | CRÍTICA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-95](https://cwe.mitre.org/data/definitions/95.html) |
| OWASP | A05:2025 Inyección |
