# NODE-PATH-001: Acceso a archivos con ruta controlada por la petición (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Datos de la petición forman la ruta de un archivo (fs.readFile, createReadStream, writeFile, unlink, res.sendFile, res.download…) sin reducirla a un nombre de archivo: permite leer, escribir o borrar archivos fuera de la carpeta prevista (path traversal).

## Cómo corregirlo

Reducir la entrada a un nombre con path.basename() o una lista blanca, resolver contra una carpeta base fija con path.resolve y comprobar que el resultado siga dentro de ella; en Express, res.sendFile(nombre, { root: carpeta }).

## Por qué importa

Esta regla corresponde a [CWE-22](https://cwe.mitre.org/data/definitions/22.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Sigue el parámetro hasta la función que abre el archivo y confirma que la ruta se normaliza y se limita a un directorio base. Prueba con `../` en un entorno de pruebas.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-22](https://cwe.mitre.org/data/definitions/22.html) |
| OWASP | A01:2025 Control de acceso roto |
