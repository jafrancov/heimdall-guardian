# PHP-XSS-001: XSS: salida de datos de la petición sin escapar (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Datos de la petición se escriben en la página sin escapar: permite inyectar scripts en el navegador de otros usuarios (XSS).

## Cómo corregirlo

Escapar con htmlspecialchars($valor, ENT_QUOTES, 'UTF-8') al escribir en HTML, o usar el escapado automático del motor de plantillas.

## Por qué importa

Esta regla corresponde a [CWE-79](https://cwe.mitre.org/data/definitions/79.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Localiza dónde se imprime el dato en la página y confirma que se escapa según el contexto (HTML, atributo o script). Prueba con un texto como `&lt;b&gt;x&lt;/b&gt;` en pruebas.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Inyección |
