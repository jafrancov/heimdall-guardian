# DART-TLS-001: Validación de certificados TLS desactivada (Dart/Flutter)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Validación de certificados desactivada: el callback que decide qué hacer con un certificado inválido siempre responde que sí. Cualquiera en la red (una wifi pública, por ejemplo) puede hacerse pasar por el servidor y leer o modificar el tráfico.

## Cómo corregirlo

Eliminar el callback (badCertificateCallback, onBadCertificate o validateCertificate que devuelve true) y dejar que la plataforma valide la cadena. Si hace falta confiar en una CA propia, agregarla con SecurityContext.setTrustedCertificatesBytes o fijar el certificado (pinning) comparando su huella, nunca aceptar todo.

## Por qué importa

Esta regla corresponde a [CWE-295](https://cwe.mitre.org/data/definitions/295.html) y a la categoría A04:2025 Fallas criptográficas del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si se desactiva la validación de certificados. Debe validarse siempre la cadena de confianza y el nombre del servidor.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Dart y Flutter |
| Lenguajes | `dart` |
| CWE | [CWE-295](https://cwe.mitre.org/data/definitions/295.html) |
| OWASP | A04:2025 Fallas criptográficas |
