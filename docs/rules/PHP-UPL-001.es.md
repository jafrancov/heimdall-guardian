# PHP-UPL-001: Archivo subido guardado en una ruta controlada por el cliente (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Un archivo subido se guarda en una ruta construida con datos que controla el cliente (el nombre original del archivo, la extensión, un campo del formulario o el nombre del campo de carga). El visitante decide el nombre y la carpeta, así que un script puede terminar en una carpeta donde el servidor web ejecuta PHP, y se puede sobrescribir un archivo existente.

## Cómo corregirlo

Generar el nombre guardado en el servidor (por ejemplo con random_bytes) y obtener la extensión de una lista blanca, no del nombre original. Validar la extensión y el tipo MIME real contra una lista blanca antes de mover el archivo, y guardarlo fuera de la raíz web o en una carpeta donde PHP no se ejecute. Si la carpeta viene de la petición, elegirla de una lista fija o comprobar con realpath() que queda dentro de la raíz de cargas.

## Por qué importa

Esta regla corresponde a [CWE-434](https://cwe.mitre.org/data/definitions/434.html) y a la categoría A06:2025 Diseño inseguro del OWASP Top 10:2025.

## Cómo verificarlo

Revisa la validación del archivo subido: tipo real, extensión permitida, tamaño máximo, nombre regenerado y carpeta fuera de la que sirve el servidor web.

## Datos

| | |
|---|---|
| Severidad | CRÍTICA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-434](https://cwe.mitre.org/data/definitions/434.html) |
| OWASP | A06:2025 Diseño inseguro |
