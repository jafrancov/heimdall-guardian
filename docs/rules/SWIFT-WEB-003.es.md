# SWIFT-WEB-003: UIWebView obsoleto e inseguro (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Uso de UIWebView: Apple lo declaró obsoleto, la App Store rechaza aplicaciones que lo incluyen y no recibe correcciones de seguridad. No aísla el proceso de la página ni permite restringir la ejecución de JavaScript como WKWebView.

## Cómo corregirlo

Migrar a WKWebView (WebKit), que corre en un proceso aparte y permite controlar la navegación con WKNavigationDelegate. Para mostrar páginas externas sin código propio, SFSafariViewController.

## Por qué importa

Esta regla corresponde a [CWE-477](https://cwe.mitre.org/data/definitions/477.html) y a la categoría A03:2025 Fallas en la cadena de suministro de software del OWASP Top 10:2025.

## Cómo verificarlo

Busca el componente obsoleto en el código y en las dependencias. Confirma con la documentación del fabricante cuál lo reemplaza y qué versión ya no recibe correcciones.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Swift |
| Lenguajes | `regex` |
| CWE | [CWE-477](https://cwe.mitre.org/data/definitions/477.html) |
| OWASP | A03:2025 Fallas en la cadena de suministro de software |
