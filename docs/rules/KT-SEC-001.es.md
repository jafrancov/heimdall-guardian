# KT-SEC-001: Llave de API, secreto o contraseña escrita en el código (Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Secreto escrito en el código: una constante con nombre de llave de API, secreto, token o contraseña recibe un texto fijo. Quien tenga la aplicación (un APK se descompila en minutos) o el repositorio puede extraerlo.

## Cómo corregirlo

Quitar el valor del código y rotarlo si ya se publicó. Un secreto de servidor no debe viajar en la aplicación: usar un servicio propio que lo guarde. Si es una llave pública de cliente, restringirla en el proveedor por paquete y huella de firma, e inyectarla en la compilación desde local.properties o variables de entorno que no se suban al repositorio.

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
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) |
| OWASP | A07:2025 Fallas de autenticación |
