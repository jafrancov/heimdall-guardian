# NET-CONF-003: CORS abierto con credenciales (.NET)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

CORS permite cualquier origen junto con credenciales: cualquier sitio web puede hacer peticiones autenticadas en nombre del usuario.

## Cómo corregirlo

Sustituir AllowAnyOrigin() por WithOrigins() con los dominios reales del sistema.

## Por qué importa

Esta regla corresponde a [CWE-942](https://cwe.mitre.org/data/definitions/942.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Revisa la configuración de CORS: los orígenes deben ser una lista concreta; un origen abierto con credenciales permite que otros sitios lean datos de sesión.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | ALTA |
| Categoría | CONFIGURACION |
| Stack | .NET |
| Lenguajes | `csharp` |
| CWE | [CWE-942](https://cwe.mitre.org/data/definitions/942.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
