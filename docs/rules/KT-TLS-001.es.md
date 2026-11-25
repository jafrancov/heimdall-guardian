# KT-TLS-001: Validación de certificados TLS desactivada (Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Se desactiva la validación de la conexión segura: un TrustManager que acepta cualquier certificado, un HostnameVerifier que siempre responde true, ALLOW_ALL_HOSTNAME_VERIFIER o un WebView que continúa tras un error de certificado (handler.proceed()). Cualquiera en la misma red puede interceptar y modificar el tráfico con un certificado falso.

## Cómo corregirlo

Quitar el TrustManager y el HostnameVerifier personalizados y usar los del sistema. Si el servidor usa una autoridad propia, declararla en network_security_config.xml o fijar el certificado con CertificatePinner de OkHttp. En onReceivedSslError, llamar a handler.cancel() y mostrar el error al usuario.

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
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-295](https://cwe.mitre.org/data/definitions/295.html) |
| OWASP | A04:2025 Fallas criptográficas |
