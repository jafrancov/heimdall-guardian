# SWIFT-TLS-001: Validación de certificados TLS desactivada (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Validación de certificados desactivada: el delegado de URLSession acepta cualquier certificado del servidor sin evaluarlo, o se usa un evaluador que no valida nada. Cualquiera en la red (una wifi pública, por ejemplo) puede hacerse pasar por el servidor y leer o modificar el tráfico.

## Cómo corregirlo

Eliminar el método didReceive challenge para que el sistema valide la cadena, o evaluar serverTrust con SecTrustEvaluateWithError antes de responder .useCredential. Si hace falta confiar en una CA propia o fijar el certificado (pinning), comparar la llave pública o la huella del certificado recibido con la esperada y cancelar el desafío si no coincide. En Alamofire, usar PinnedCertificatesTrustEvaluator o DefaultTrustEvaluator en lugar de DisabledTrustEvaluator.

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
| Stack | Swift |
| Lenguajes | `regex` |
| CWE | [CWE-295](https://cwe.mitre.org/data/definitions/295.html) |
| OWASP | A04:2025 Fallas criptográficas |
