# SWIFT-SEC-001: Llave de API, secreto o contraseña escrita en el código (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Secreto escrito en el código: una constante con nombre de llave de API, secreto, token o contraseña recibe un texto fijo. Quien tenga la aplicación (un IPA se descifra y se inspecciona en minutos) o el repositorio puede extraerlo.

## Cómo corregirlo

Quitar el valor del código y rotarlo si ya se publicó. Un secreto de servidor no debe viajar en la aplicación: usar un servicio propio que lo guarde. Si es una llave pública de cliente, restringirla en el proveedor por bundle ID, y pasarla con un archivo .xcconfig o un esquema fuera del repositorio.

## Por qué importa

Esta regla corresponde a [CWE-798](https://cwe.mitre.org/data/definitions/798.html) y a la categoría A07:2025 Fallas de autenticación del OWASP Top 10:2025.

## Cómo verificarlo

Busca el valor en el historial de versiones y confirma si sigue vigente. Si lo está, rótalo de inmediato y muévelo a un gestor de secretos.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Swift |
| Lenguajes | `regex` |
| CWE | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) |
| OWASP | A07:2025 Fallas de autenticación |
