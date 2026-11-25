# PHP-CONF-001: display_errors activo o credenciales en .env versionado

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Configuración insegura: display_errors activado (muestra rutas, consultas y trazas a cualquier visitante) o credenciales escritas en un archivo .env versionado.

## Cómo corregirlo

En producción, display_errors = Off y log_errors = On. El archivo .env no se versiona: agregarlo a .gitignore, dejar un .env.example sin valores y cambiar las credenciales expuestas.

## Por qué importa

Esta regla corresponde a [CWE-209](https://cwe.mitre.org/data/definitions/209.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Provoca un error en un entorno de pruebas y revisa si la respuesta muestra rutas, consultas o trazas. Producción solo debe mostrar un mensaje genérico.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | CONFIGURACION |
| Stack | PHP y Laravel |
| Lenguajes | `regex` |
| CWE | [CWE-209](https://cwe.mitre.org/data/definitions/209.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
