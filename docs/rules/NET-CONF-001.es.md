# NET-CONF-001: Contraseña en cadena de conexión (.NET)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Cadena de conexión con la contraseña escrita en un archivo de configuración versionado. Quien tenga acceso al repositorio tiene acceso a la base de datos.

## Cómo corregirlo

Cambiar la contraseña y sacarla del archivo: variables de entorno, User Secrets en desarrollo o un gestor de secretos en producción.

## Por qué importa

Esta regla corresponde a [CWE-798](https://cwe.mitre.org/data/definitions/798.html) y a la categoría A07:2025 Fallas de autenticación del OWASP Top 10:2025.

## Cómo verificarlo

Busca el valor en el historial de versiones y confirma si sigue vigente. Si lo está, rótalo de inmediato y muévelo a un gestor de secretos.

## Datos

| | |
|---|---|
| Severidad | CRÍTICA |
| Confianza | ALTA |
| Categoría | CONFIGURACION |
| Stack | .NET |
| Lenguajes | `regex` |
| CWE | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) |
| OWASP | A07:2025 Fallas de autenticación |
