# DJ-CAND-007: XML analizado desde una variable (por revisar)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

> Candidata: solo la revisa la IA local, nunca se reporta sola

Se analiza un documento XML a partir de un valor que no es constante. Es solo un punto por revisar: la IA local comprueba si le llega entrada no confiable.

## Cómo corregirlo

Desactiva los DTD y las entidades externas en el analizador XML, o usa uno configurado para rechazarlos.

## Por qué importa

Esta regla corresponde a [CWE-611](https://cwe.mitre.org/data/definitions/611.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Revisa el analizador XML: deben desactivarse las entidades externas y las definiciones de tipo de documento.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-611](https://cwe.mitre.org/data/definitions/611.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
