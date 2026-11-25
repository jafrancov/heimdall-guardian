# DJ-CONF-002: SECRET_KEY literal en el código

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

SECRET_KEY escrita como literal en el código. Quien tenga acceso al repositorio puede falsificar sesiones, tokens de restablecimiento de contraseña y datos firmados.

## Cómo corregirlo

Generar una llave nueva, cargarla desde una variable de entorno o un gestor de secretos y dar por comprometida la que quedó en el repositorio.

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
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) |
| OWASP | A07:2025 Fallas de autenticación |
