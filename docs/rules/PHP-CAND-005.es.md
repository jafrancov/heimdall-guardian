# PHP-CAND-005: Redirección a una variable (por revisar)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

> Candidata: solo la revisa la IA local, nunca se reporta sola

Se redirige al usuario a un destino que no es constante. Es solo un punto por revisar: la IA local comprueba si le llega entrada no confiable.

## Cómo corregirlo

Redirige solo a rutas relativas o a hosts de una lista permitida.

## Por qué importa

Esta regla corresponde a [CWE-601](https://cwe.mitre.org/data/definitions/601.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si el destino de la redirección sale de un dato de la petición. Debe compararse con una lista de destinos permitidos o limitarse a rutas internas.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-601](https://cwe.mitre.org/data/definitions/601.html) |
| OWASP | A01:2025 Control de acceso roto |
