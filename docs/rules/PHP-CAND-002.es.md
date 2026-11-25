# PHP-CAND-002: Comando armado con una variable (por revisar)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

> Candidata: solo la revisa la IA local, nunca se reporta sola

Se ejecuta un comando del sistema con un valor que no es constante. Es solo un punto por revisar: la IA local comprueba si le llega entrada no confiable.

## Cómo corregirlo

Evita el shell; pasa el programa y sus argumentos como lista y valida cada valor contra una lista permitida.

## Por qué importa

Esta regla corresponde a [CWE-78](https://cwe.mitre.org/data/definitions/78.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si el texto del comando se arma con datos del usuario. Debe usarse una lista de argumentos sin intérprete de comandos y con valores permitidos.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| OWASP | A05:2025 Inyección |
