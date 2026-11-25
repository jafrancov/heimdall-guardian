# NODE-EXE-001: Inyección de comandos con datos de la petición (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Datos de la petición llegan a un comando del sistema (child_process.exec, execSync, spawn o execFile con shell, shelljs.exec): permite ejecutar comandos arbitrarios en el servidor.

## Cómo corregirlo

Evitar el intérprete de comandos: usar execFile o spawn sin shell:true y pasar los argumentos como arreglo, validados contra una lista blanca. Si es inevitable construir un comando, escapar cada argumento con shell- quote.

## Por qué importa

Esta regla corresponde a [CWE-78](https://cwe.mitre.org/data/definitions/78.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si el texto del comando se arma con datos del usuario. Debe usarse una lista de argumentos sin intérprete de comandos y con valores permitidos.

## Datos

| | |
|---|---|
| Severidad | CRÍTICA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| OWASP | A05:2025 Inyección |
