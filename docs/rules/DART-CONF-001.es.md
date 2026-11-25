# DART-CONF-001: Configuración insegura en AndroidManifest.xml o Info.plist

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Configuración nativa insegura de la app móvil (Android o iOS): tráfico http sin cifrar permitido, aplicación depurable o copia de seguridad habilitada. Cada una amplía lo que un atacante con acceso a la red o al dispositivo puede obtener.

## Cómo corregirlo

En AndroidManifest.xml usar usesCleartextTraffic="false" (o definir un network_security_config con solo los dominios necesarios), debuggable="false" y allowBackup="false" en la versión publicada. En Info.plist, quitar NSAllowsArbitraryLoads y declarar excepciones solo por dominio. Las pruebas locales pueden ir en android/app/src/debug.

## Por qué importa

Esta regla corresponde a [CWE-16](https://cwe.mitre.org/data/definitions/16.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Abre el archivo de configuración del entorno de producción y compare el valor con el recomendado: modo de depuración apagado, orígenes acotados y sin valores de prueba.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | CONFIGURACION |
| Stack | Dart y Flutter |
| Lenguajes | `regex` |
| CWE | [CWE-16](https://cwe.mitre.org/data/definitions/16.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
