# KT-CAND-003: Ruta de archivo desde una variable (por revisar)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

> Candidata: solo la revisa la IA local, nunca se reporta sola

Se abre un archivo con una ruta que no es constante. Es solo un punto por revisar: la IA local comprueba si le llega entrada no confiable.

## Cómo corregirlo

Resuelve la ruta contra una carpeta base fija y rechaza cualquier resultado que quede fuera de ella.

## Por qué importa

Esta regla corresponde a [CWE-22](https://cwe.mitre.org/data/definitions/22.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Sigue el parámetro hasta la función que abre el archivo y confirma que la ruta se normaliza y se limita a un directorio base. Prueba con `../` en un entorno de pruebas.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-22](https://cwe.mitre.org/data/definitions/22.html) |
| OWASP | A01:2025 Control de acceso roto |
