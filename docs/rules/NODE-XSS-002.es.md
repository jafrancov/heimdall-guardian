# NODE-XSS-002: HTML dinámico insertado en el DOM sin sanitizar (JavaScript)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Se inserta HTML dinámico en la página (innerHTML, outerHTML, insertAdjacentHTML, document.write, dangerouslySetInnerHTML o jQuery .html). Si el valor incluye datos del usuario sin sanitizar, permite ejecutar scripts (XSS basado en DOM).

## Cómo corregirlo

Asignar texto con textContent o crear nodos con createElement. Si hace falta HTML, sanitizarlo antes con DOMPurify.sanitize(valor). En React, evitar dangerouslySetInnerHTML o sanitizar el valor.

## Por qué importa

Esta regla corresponde a [CWE-79](https://cwe.mitre.org/data/definitions/79.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Localiza dónde se imprime el dato en la página y confirma que se escapa según el contexto (HTML, atributo o script). Prueba con un texto como `&lt;b&gt;x&lt;/b&gt;` en pruebas.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Inyección |
