# SWIFT-KEY-001: Keychain con accesibilidad «siempre» (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Elemento del Keychain con accesibilidad débil: kSecAttrAccessibleAlways (y su variante ThisDeviceOnly) deja el dato disponible incluso con el dispositivo bloqueado y recién encendido, y Apple lo declaró obsoleto. Un atacante con el dispositivo en la mano puede leerlo sin desbloquearlo.

## Cómo corregirlo

Usar kSecAttrAccessibleWhenUnlockedThisDeviceOnly para datos que solo se necesitan con la app en uso, o kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly si una tarea en segundo plano debe leerlos. Para datos muy sensibles, agregar un control de acceso con biometría (SecAccessControlCreateWithFlags).

## Por qué importa

Esta regla corresponde a [CWE-311](https://cwe.mitre.org/data/definitions/311.html) y a la categoría A04:2025 Fallas criptográficas del OWASP Top 10:2025.

## Cómo verificarlo

Confirma con el equipo de infraestructura si el dato viaja o se guarda sin cifrar y qué mecanismo de cifrado se usa.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Swift |
| Lenguajes | `swift` |
| CWE | [CWE-311](https://cwe.mitre.org/data/definitions/311.html) |
| OWASP | A04:2025 Fallas criptográficas |
