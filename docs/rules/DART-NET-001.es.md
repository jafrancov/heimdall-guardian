# DART-NET-001: Dirección http:// sin cifrar en el código (Dart/Flutter)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Dirección http:// sin cifrar: el tráfico de la aplicación viaja en texto claro y cualquiera en la misma red puede leerlo o modificarlo. Android 9 y iOS bloquean este tráfico por defecto, así que además suele obligar a abrir una excepción global.

## Cómo corregirlo

Usar https:// en todas las direcciones de servicios. Para desarrollo local, localhost, 127.0.0.1 y 10.0.2.2 están permitidos; si un entorno de pruebas no tiene certificado, resolverlo ahí en lugar de aceptar http en la versión publicada.

## Por qué importa

Esta regla corresponde a [CWE-319](https://cwe.mitre.org/data/definitions/319.html) y a la categoría A04:2025 Fallas criptográficas del OWASP Top 10:2025.

## Cómo verificarlo

Revisa la configuración del servidor y del cliente: la comunicación debe usar TLS. Comprueba que no haya direcciones `http://` hacia servicios con datos.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Dart y Flutter |
| Lenguajes | `regex` |
| CWE | [CWE-319](https://cwe.mitre.org/data/definitions/319.html) |
| OWASP | A04:2025 Fallas criptográficas |
