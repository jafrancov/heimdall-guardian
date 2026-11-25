# DJ-UPL-001: Carga de archivos sin validación de tipo o tamaño

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Campo de carga de archivos sin validadores. Sin límite de tipo ni de tamaño se pueden subir ejecutables, HTML con scripts o archivos que agoten el almacenamiento.

## Cómo corregirlo

Agregar validators (FileExtensionValidator y un validador de tamaño) y verificar el contenido real del archivo, no solo su extensión.

## Por qué importa

Esta regla corresponde a [CWE-434](https://cwe.mitre.org/data/definitions/434.html) y a la categoría A06:2025 Diseño inseguro del OWASP Top 10:2025.

## Cómo verificarlo

Revisa la validación del archivo subido: tipo real, extensión permitida, tamaño máximo, nombre regenerado y carpeta fuera de la que sirve el servidor web.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-434](https://cwe.mitre.org/data/definitions/434.html) |
| OWASP | A06:2025 Diseño inseguro |
