# PHP-EXE-001: Ejecución de comandos con entrada variable (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Ejecución de código o de comandos del sistema con un argumento variable. Si el valor proviene del usuario, permite ejecutar comandos arbitrarios en el servidor.

## Cómo corregirlo

Eliminar eval/exec/system/shell_exec/passthru sobre datos variables. Si el comando es indispensable, usar una lista blanca de valores y escapeshellarg() en cada argumento.

## Por qué importa

Esta regla corresponde a [CWE-78](https://cwe.mitre.org/data/definitions/78.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si el texto del comando se arma con datos del usuario. Debe usarse una lista de argumentos sin intérprete de comandos y con valores permitidos.

## Datos

| | |
|---|---|
| Severidad | CRÍTICA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| OWASP | A05:2025 Inyección |
