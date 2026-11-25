# DJ-IDOR-001: Posible acceso a objetos ajenos (IDOR)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Se obtiene un objeto solo por su identificador, tomado de la URL, sin filtrar por el usuario o la organización de quien consulta. Si no hay otra validación, un usuario puede leer o modificar registros ajenos cambiando el identificador (IDOR).

## Cómo corregirlo

Filtrar también por el propietario, por ejemplo get_object_or_404(Modelo, pk=pk, usuario=request.user), o verificar el permiso sobre el objeto antes de usarlo.

## Por qué importa

Esta regla corresponde a [CWE-639](https://cwe.mitre.org/data/definitions/639.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Prueba con dos cuentas distintas en un entorno de pruebas: la cuenta A pide el identificador de un registro de B y debe recibir 403 o 404.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | CONTROL ACCESO |
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-639](https://cwe.mitre.org/data/definitions/639.html) |
| OWASP | A01:2025 Control de acceso roto |
