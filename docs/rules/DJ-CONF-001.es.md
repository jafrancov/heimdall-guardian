# DJ-CONF-001: DEBUG activado en configuración

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

DEBUG = True en un archivo de configuración que no es de desarrollo. En producción expone trazas, rutas, consultas SQL y parte de la configuración a cualquier visitante.

## Cómo corregirlo

Definir DEBUG = False por defecto y activarlo solo desde una variable de entorno en los equipos de desarrollo.

## Por qué importa

Esta regla corresponde a [CWE-489](https://cwe.mitre.org/data/definitions/489.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Confirma en el entorno de producción que el modo de depuración está apagado y que ninguna consola de desarrollo es accesible.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | CONFIGURACION |
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-489](https://cwe.mitre.org/data/definitions/489.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
