# NODE-SSRF-001: Solicitud del servidor a una URL controlada por la petición (SSRF, Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Datos de la petición se usan como dirección de una solicitud HTTP del servidor (axios, fetch, got, request, http.get, needle…): permite que un atacante haga consultas a servicios internos o a metadatos de la nube (SSRF).

## Cómo corregirlo

No aceptar URL completas del usuario. Elegir el destino de una lista blanca de hosts o claves, validar el esquema (solo https) y bloquear direcciones privadas, de loopback y de metadatos (169.254.169.254) tras resolver el nombre.

## Por qué importa

Esta regla corresponde a [CWE-918](https://cwe.mitre.org/data/definitions/918.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si la dirección que consulta el servidor viene de la petición. Debe validarse contra una lista de destinos permitidos y bloquear direcciones internas.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-918](https://cwe.mitre.org/data/definitions/918.html) |
| OWASP | A01:2025 Control de acceso roto |
