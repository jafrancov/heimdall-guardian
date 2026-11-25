# NODE-XSS-001: XSS reflejado: datos de la petición en la respuesta sin escapar (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Datos de la petición se envían en la respuesta (res.send, res.write, res.end) sin escapar. Express responde con text/html a los textos, por lo que el navegador ejecuta el HTML o el script inyectado (XSS reflejado).

## Cómo corregirlo

Escapar la salida con una función de codificación HTML (escape-html, he.encode) o devolver JSON con res.json. Para HTML con formato usar una plantilla que escape por defecto (EJS &lt;%= %&gt;, Handlebars {{ }}, Pug =) o sanitizar con DOMPurify o sanitize-html.

## Por qué importa

Esta regla corresponde a [CWE-79](https://cwe.mitre.org/data/definitions/79.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Localiza dónde se imprime el dato en la página y confirma que se escapa según el contexto (HTML, atributo o script). Prueba con un texto como `&lt;b&gt;x&lt;/b&gt;` en pruebas.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Inyección |
