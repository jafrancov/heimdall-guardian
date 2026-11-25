# DJ-CONF-003: ALLOWED_HOSTS o CORS abiertos a cualquier origen

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Configuración abierta a cualquier origen: ALLOWED_HOSTS con comodín o CORS permitido para todos los orígenes.

## Cómo corregirlo

Enumerar los dominios reales del sistema en ALLOWED_HOSTS y en CORS_ALLOWED_ORIGINS.

## Por qué importa

Esta regla corresponde a [CWE-942](https://cwe.mitre.org/data/definitions/942.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Revisa la configuración de CORS: los orígenes deben ser una lista concreta; un origen abierto con credenciales permite que otros sitios lean datos de sesión.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | CONFIGURACION |
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-942](https://cwe.mitre.org/data/definitions/942.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
