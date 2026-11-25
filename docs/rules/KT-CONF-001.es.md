# KT-CONF-001: Componente exportado sin permiso o tráfico http permitido (AndroidManifest.xml)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Componente de Android exportado sin permiso: una actividad, servicio, receptor o proveedor con android:exported="true" y sin android:permission puede ser invocado por cualquier aplicación instalada; un proveedor con grantUriPermissions="true" permite además dar acceso a sus datos por URI. También se marca el tráfico http sin cifrar permitido en network_security_config.xml.

## Cómo corregirlo

Declarar android:exported="false" salvo que el componente deba recibir llamadas de otras aplicaciones; en ese caso exigir un android:permission de firma (signature), validar cada Intent recibido y no confiar en sus datos. Los proveedores de archivos deben ser FileProvider con exported="false" y grantUriPermissions="true". En network_security_config.xml, permitir http solo para dominios de desarrollo concretos y nunca en base-config.

## Por qué importa

Esta regla corresponde a [CWE-926](https://cwe.mitre.org/data/definitions/926.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Abre AndroidManifest.xml y revisa cada componente con android:exported="true": ¿necesita recibir llamadas de otras aplicaciones? Si no, ponlo en false; si sí, exige un permiso de firma y prueba con `adb shell am start` que rechaza datos inválidos.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | CONFIGURACION |
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-926](https://cwe.mitre.org/data/definitions/926.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
