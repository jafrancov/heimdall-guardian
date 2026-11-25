# SWIFT-CONF-001: Configuración insegura en Info.plist o .entitlements (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Configuración nativa insegura en la app de iOS: App Transport Security desactivado (permite tráfico http sin cifrar, global o por dominio) o derechos con get-task-allow, que permiten adjuntar un depurador a la aplicación. Cada una amplía lo que un atacante con acceso a la red o al dispositivo puede obtener.

## Cómo corregirlo

En Info.plist, quitar NSAllowsArbitraryLoads, NSAllowsArbitraryLoadsInWebContent y NSExceptionAllowsInsecureHTTPLoads, y declarar excepciones solo por dominio y, si es posible, solo para pruebas. En los archivos .entitlements de la versión publicada, get-task-allow debe ser false u omitirse; Xcode lo agrega solo a las compilaciones de depuración.

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
| Stack | Swift |
| Lenguajes | `regex` |
| CWE | [CWE-16](https://cwe.mitre.org/data/definitions/16.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
