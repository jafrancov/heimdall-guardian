# SWIFT-CAND-003: Petición a una URL desde una variable (por revisar)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

> Candidata: solo la revisa la IA local, nunca se reporta sola

Se hace una petición HTTP a una URL que no es constante. Es solo un punto por revisar: la IA local comprueba si le llega entrada no confiable.

## Cómo corregirlo

Valida el host contra una lista permitida y bloquea las direcciones privadas e internas.

## Por qué importa

Esta regla corresponde a [CWE-918](https://cwe.mitre.org/data/definitions/918.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si la dirección que consulta el servidor viene de la petición. Debe validarse contra una lista de destinos permitidos y bloquear direcciones internas.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | Swift |
| Lenguajes | `regex` |
| CWE | [CWE-918](https://cwe.mitre.org/data/definitions/918.html) |
| OWASP | A01:2025 Control de acceso roto |
