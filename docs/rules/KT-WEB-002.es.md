# KT-WEB-002: WebView con acceso a archivos locales o dirección tomada de un Intent (Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Configuración del WebView que amplía lo que puede hacer una página: acceso a archivos locales (allowFileAccess, allowFileAccessFromFileURLs, allowUniversalAccessFromFileURLs) o carga de una dirección que llega en un Intent. Un HTML malicioso guardado en la aplicación o un Intent de otra aplicación pueden leer archivos propios o abrir páginas controladas por un atacante.

## Cómo corregirlo

Dejar allowFileAccess, allowFileAccessFromFileURLs y allowUniversalAccessFromFileURLs en false y servir el contenido local con WebViewAssetLoader. Antes de llamar a loadUrl con un dato de un Intent, validar esquema https y que el host esté en una lista permitida.

## Por qué importa

Esta regla corresponde a [CWE-749](https://cwe.mitre.org/data/definitions/749.html) y a la categoría A06:2025 Diseño inseguro del OWASP Top 10:2025.

## Cómo verificarlo

Revisa qué funciones de la aplicación puede invocar la página del WebView. Deben ser las mínimas, con la página limitada a tu dominio por https y cada mensaje validado.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Diseño inseguro |
