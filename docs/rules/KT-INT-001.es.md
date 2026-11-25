# KT-INT-001: PendingIntent mutable, receptor expuesto o difusión sin permiso (Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Comunicación entre componentes que otra aplicación puede aprovechar: un PendingIntent sin FLAG_IMMUTABLE (una aplicación que lo reciba puede rellenar o cambiar su Intent y actuar con los permisos de esta), un receptor registrado sin RECEIVER_NOT_EXPORTED que acepta mensajes de cualquier aplicación, o un sendBroadcast con datos sensibles sin permiso que lo reciba cualquier aplicación instalada.

## Cómo corregirlo

Crear los PendingIntent con PendingIntent.FLAG_IMMUTABLE (usar FLAG_MUTABLE solo cuando el sistema deba rellenarlo, y entonces con un Intent explícito). Registrar los receptores internos con ContextCompat.registerReceiver(..., ContextCompat.RECEIVER_NOT_EXPORTED). Para difusiones con datos sensibles usar Intent explícito (setPackage) o sendBroadcast(intent, permiso) con un permiso propio de firma.

## Por qué importa

Esta regla corresponde a [CWE-927](https://cwe.mitre.org/data/definitions/927.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Busca los PendingIntent y confirma que llevan FLAG_IMMUTABLE e Intent explícito. En los broadcast, comprueba que lo enviado no es sensible o que solo lo recibe tu aplicación (setPackage o un permiso de firma).

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-927](https://cwe.mitre.org/data/definitions/927.html) |
| OWASP | A01:2025 Control de acceso roto |
