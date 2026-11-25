# DJ-XSS-001: HTML sin escapar: mark_safe con datos variables

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

mark_safe() sobre un valor variable desactiva el escapado de HTML. Si el valor contiene datos del usuario, permite inyectar scripts (XSS).

## Cómo corregirlo

Usar format_html(), que escapa cada argumento, o dejar que la plantilla escape el valor.

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
| Lenguajes | `python` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Inyección |
