# DJ-XSS-002: HTML sin escapar en plantilla (\|safe, autoescape off)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

La plantilla desactiva el escapado automático de HTML (filtro safe o autoescape off). Si el valor contiene datos del usuario, permite inyectar scripts (XSS).

## Cómo corregirlo

Quitar el filtro safe o el bloque autoescape off. Si se necesita HTML enriquecido, limpiarlo antes en el servidor con una lista blanca de etiquetas.

## Por qué importa

Esta regla corresponde a [CWE-79](https://cwe.mitre.org/data/definitions/79.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Localiza dónde se imprime el dato en la página y confirma que se escapa según el contexto (HTML, atributo o script). Prueba con un texto como `&lt;b&gt;x&lt;/b&gt;` en pruebas.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Python y Django |
| Lenguajes | `regex` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Inyección |
