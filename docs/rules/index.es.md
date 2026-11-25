# Catálogo de reglas

Heimdall Guardian incluye 124 reglas propias en formato Opengrep. Este catálogo se genera a partir de los archivos de reglas, así que siempre coincide con la versión que instalas.

## Dart y Flutter

| ID | Título | Severidad | Confianza | CWE | OWASP |
|---|---|---|---|---|---|
| [DART-SEC-001](DART-SEC-001.es.md) | Llave de API, secreto o contraseña escrita en el código (Dart/Flutter) | ALTA | MEDIA | CWE-798 | A07:2025 Fallas de autenticación |
| [DART-SQL-001](DART-SQL-001.es.md) | Consulta SQL construida con texto (sqflite/drift, Dart/Flutter) | ALTA | MEDIA | CWE-89 | A05:2025 Inyección |
| [DART-STO-001](DART-STO-001.es.md) | Token o contraseña en almacenamiento sin cifrar (Dart/Flutter) | ALTA | MEDIA | CWE-312 | A04:2025 Fallas criptográficas |
| [DART-TLS-001](DART-TLS-001.es.md) | Validación de certificados TLS desactivada (Dart/Flutter) | ALTA | ALTA | CWE-295 | A04:2025 Fallas criptográficas |
| [DART-WEB-001](DART-WEB-001.es.md) | WebView con puente de JavaScript hacia la aplicación (Dart/Flutter) | ALTA | MEDIA | CWE-749 | A06:2025 Diseño inseguro |
| [DART-CAND-001](DART-CAND-001.es.md) | SQL armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-89 | A05:2025 Inyección |
| [DART-CAND-002](DART-CAND-002.es.md) | Comando armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-78 | A05:2025 Inyección |
| [DART-CAND-003](DART-CAND-003.es.md) | Ruta de archivo desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-22 | A01:2025 Control de acceso roto |
| [DART-CAND-004](DART-CAND-004.es.md) | Petición a una URL desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-918 | A01:2025 Control de acceso roto |
| [DART-CONF-001](DART-CONF-001.es.md) | Configuración insegura en AndroidManifest.xml o Info.plist | MEDIA | ALTA | CWE-16 | A02:2025 Configuración de seguridad incorrecta |
| [DART-CRY-001](DART-CRY-001.es.md) | Criptografía débil o aleatoriedad predecible (Dart/Flutter) | MEDIA | MEDIA | CWE-327 | A04:2025 Fallas criptográficas |
| [DART-LOG-001](DART-LOG-001.es.md) | Dato sensible escrito en el registro (Dart/Flutter) | MEDIA | MEDIA | CWE-532 | A09:2025 Fallas de registro y alertas de seguridad |
| [DART-NET-001](DART-NET-001.es.md) | Dirección http:// sin cifrar en el código (Dart/Flutter) | MEDIA | MEDIA | CWE-319 | A04:2025 Fallas criptográficas |
| [DART-WEB-002](DART-WEB-002.es.md) | WebView con JavaScript habilitado (Dart/Flutter) | MEDIA | BAJA | CWE-749 | A06:2025 Diseño inseguro |

## Python y Django

| ID | Título | Severidad | Confianza | CWE | OWASP |
|---|---|---|---|---|---|
| [DJ-CONF-002](DJ-CONF-002.es.md) | SECRET_KEY literal en el código | CRÍTICA | ALTA | CWE-798 | A07:2025 Fallas de autenticación |
| [DJ-AUTH-001](DJ-AUTH-001.es.md) | Vista sin autenticación (Django, FBV) | ALTA | BAJA | CWE-306 | A01:2025 Control de acceso roto |
| [DJ-AUTH-002](DJ-AUTH-002.es.md) | Vista sin autenticación (Django, CBV) | ALTA | BAJA | CWE-306 | A01:2025 Control de acceso roto |
| [DJ-AUTH-003](DJ-AUTH-003.es.md) | API sin autenticación: AllowAny (DRF) | ALTA | MEDIA | CWE-306 | A01:2025 Control de acceso roto |
| [DJ-CONF-001](DJ-CONF-001.es.md) | DEBUG activado en configuración | ALTA | MEDIA | CWE-489 | A02:2025 Configuración de seguridad incorrecta |
| [DJ-SQL-001](DJ-SQL-001.es.md) | SQL dinámico en consulta directa (Django) | ALTA | MEDIA | CWE-89 | A05:2025 Inyección |
| [DJ-AUTH-004](DJ-AUTH-004.es.md) | Protección CSRF desactivada (@csrf_exempt) | MEDIA | ALTA | CWE-352 | A01:2025 Control de acceso roto |
| [DJ-CAND-001](DJ-CAND-001.es.md) | SQL armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-89 | A05:2025 Inyección |
| [DJ-CAND-002](DJ-CAND-002.es.md) | Comando armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-78 | A05:2025 Inyección |
| [DJ-CAND-003](DJ-CAND-003.es.md) | Ruta de archivo desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-22 | A01:2025 Control de acceso roto |
| [DJ-CAND-004](DJ-CAND-004.es.md) | Petición a una URL desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-918 | A01:2025 Control de acceso roto |
| [DJ-CAND-005](DJ-CAND-005.es.md) | Redirección a una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-601 | A01:2025 Control de acceso roto |
| [DJ-CAND-006](DJ-CAND-006.es.md) | Deserialización de una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-502 | A08:2025 Fallas de integridad de software o datos |
| [DJ-CAND-007](DJ-CAND-007.es.md) | XML analizado desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-611 | A02:2025 Configuración de seguridad incorrecta |
| [DJ-CONF-003](DJ-CONF-003.es.md) | ALLOWED_HOSTS o CORS abiertos a cualquier origen | MEDIA | ALTA | CWE-942 | A02:2025 Configuración de seguridad incorrecta |
| [DJ-CONF-004](DJ-CONF-004.es.md) | Cookies o transporte inseguros en settings | MEDIA | MEDIA | CWE-614 | A02:2025 Configuración de seguridad incorrecta |
| [DJ-IDOR-001](DJ-IDOR-001.es.md) | Posible acceso a objetos ajenos (IDOR) | MEDIA | BAJA | CWE-639 | A01:2025 Control de acceso roto |
| [DJ-UPL-001](DJ-UPL-001.es.md) | Carga de archivos sin validación de tipo o tamaño | MEDIA | BAJA | CWE-434 | A06:2025 Diseño inseguro |
| [DJ-XSS-001](DJ-XSS-001.es.md) | HTML sin escapar: mark_safe con datos variables | MEDIA | MEDIA | CWE-79 | A05:2025 Inyección |
| [DJ-XSS-002](DJ-XSS-002.es.md) | HTML sin escapar en plantilla (\|safe, autoescape off) | MEDIA | MEDIA | CWE-79 | A05:2025 Inyección |

## .NET

| ID | Título | Severidad | Confianza | CWE | OWASP |
|---|---|---|---|---|---|
| [NET-CONF-001](NET-CONF-001.es.md) | Contraseña en cadena de conexión (.NET) | CRÍTICA | ALTA | CWE-798 | A07:2025 Fallas de autenticación |
| [NET-AUTH-001](NET-AUTH-001.es.md) | Controlador sin [Authorize] (.NET) | ALTA | BAJA | CWE-306 | A01:2025 Control de acceso roto |
| [NET-AUTH-002](NET-AUTH-002.es.md) | Acción de escritura anónima ([AllowAnonymous]) | ALTA | ALTA | CWE-306 | A01:2025 Control de acceso roto |
| [NET-CONF-003](NET-CONF-003.es.md) | CORS abierto con credenciales (.NET) | ALTA | ALTA | CWE-942 | A02:2025 Configuración de seguridad incorrecta |
| [NET-DES-001](NET-DES-001.es.md) | Deserialización insegura (.NET) | ALTA | ALTA | CWE-502 | A08:2025 Fallas de integridad de software o datos |
| [NET-SQL-001](NET-SQL-001.es.md) | SQL dinámico en consulta directa (.NET) | ALTA | MEDIA | CWE-89 | A05:2025 Inyección |
| [NET-CAND-001](NET-CAND-001.es.md) | SQL armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-89 | A05:2025 Inyección |
| [NET-CAND-002](NET-CAND-002.es.md) | Comando armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-78 | A05:2025 Inyección |
| [NET-CAND-003](NET-CAND-003.es.md) | Ruta de archivo desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-22 | A01:2025 Control de acceso roto |
| [NET-CAND-004](NET-CAND-004.es.md) | Petición a una URL desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-918 | A01:2025 Control de acceso roto |
| [NET-CAND-005](NET-CAND-005.es.md) | Redirección a una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-601 | A01:2025 Control de acceso roto |
| [NET-CAND-006](NET-CAND-006.es.md) | Deserialización de una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-502 | A08:2025 Fallas de integridad de software o datos |
| [NET-CAND-007](NET-CAND-007.es.md) | XML analizado desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-611 | A02:2025 Configuración de seguridad incorrecta |
| [NET-CONF-002](NET-CONF-002.es.md) | web.config inseguro (customErrors, debug, validateRequest) | MEDIA | ALTA | CWE-16 | A02:2025 Configuración de seguridad incorrecta |
| [NET-CRY-001](NET-CRY-001.es.md) | Criptografía débil (.NET) | MEDIA | MEDIA | CWE-327 | A04:2025 Fallas criptográficas |

## Kotlin y Android

| ID | Título | Severidad | Confianza | CWE | OWASP |
|---|---|---|---|---|---|
| [KT-SEC-001](KT-SEC-001.es.md) | Llave de API, secreto o contraseña escrita en el código (Kotlin/Android) | ALTA | MEDIA | CWE-798 | A07:2025 Fallas de autenticación |
| [KT-SQL-001](KT-SQL-001.es.md) | Consulta SQL construida con texto (SQLite o Room, Kotlin/Android) | ALTA | MEDIA | CWE-89 | A05:2025 Inyección |
| [KT-STO-001](KT-STO-001.es.md) | Token o contraseña en SharedPreferences o DataStore (Kotlin/Android) | ALTA | MEDIA | CWE-312 | A04:2025 Fallas criptográficas |
| [KT-STO-002](KT-STO-002.es.md) | Archivo o preferencias con permisos para otras aplicaciones (Kotlin/Android) | ALTA | ALTA | CWE-732 | A01:2025 Control de acceso roto |
| [KT-TLS-001](KT-TLS-001.es.md) | Validación de certificados TLS desactivada (Kotlin/Android) | ALTA | ALTA | CWE-295 | A04:2025 Fallas criptográficas |
| [KT-WEB-001](KT-WEB-001.es.md) | WebView con addJavascriptInterface (Kotlin/Android) | ALTA | MEDIA | CWE-749 | A06:2025 Diseño inseguro |
| [KT-CAND-001](KT-CAND-001.es.md) | SQL armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-89 | A05:2025 Inyección |
| [KT-CAND-002](KT-CAND-002.es.md) | Comando armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-78 | A05:2025 Inyección |
| [KT-CAND-003](KT-CAND-003.es.md) | Ruta de archivo desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-22 | A01:2025 Control de acceso roto |
| [KT-CAND-004](KT-CAND-004.es.md) | Petición a una URL desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-918 | A01:2025 Control de acceso roto |
| [KT-CONF-001](KT-CONF-001.es.md) | Componente exportado sin permiso o tráfico http permitido (AndroidManifest.xml) | MEDIA | BAJA | CWE-926 | A02:2025 Configuración de seguridad incorrecta |
| [KT-CRY-001](KT-CRY-001.es.md) | Algoritmo criptográfico débil, IV fijo o aleatorio inseguro (Kotlin/Android) | MEDIA | MEDIA | CWE-327 | A04:2025 Fallas criptográficas |
| [KT-INT-001](KT-INT-001.es.md) | PendingIntent mutable, receptor expuesto o difusión sin permiso (Kotlin/Android) | MEDIA | BAJA | CWE-927 | A01:2025 Control de acceso roto |
| [KT-LOG-001](KT-LOG-001.es.md) | Dato sensible escrito en el registro (Kotlin/Android) | MEDIA | MEDIA | CWE-532 | A09:2025 Fallas de registro y alertas de seguridad |
| [KT-NET-001](KT-NET-001.es.md) | Dirección http:// sin cifrar en el código (Kotlin/Android) | MEDIA | MEDIA | CWE-319 | A04:2025 Fallas criptográficas |
| [KT-WEB-002](KT-WEB-002.es.md) | WebView con acceso a archivos locales o dirección tomada de un Intent (Kotlin/Android) | MEDIA | BAJA | CWE-749 | A06:2025 Diseño inseguro |

## Node.js y TypeScript

| ID | Título | Severidad | Confianza | CWE | OWASP |
|---|---|---|---|---|---|
| [NODE-EXE-001](NODE-EXE-001.es.md) | Inyección de comandos con datos de la petición (Node.js) | CRÍTICA | ALTA | CWE-78 | A05:2025 Inyección |
| [NODE-EXE-002](NODE-EXE-002.es.md) | Ejecución de código con datos de la petición (Node.js) | CRÍTICA | ALTA | CWE-95 | A05:2025 Inyección |
| [NODE-SQL-001](NODE-SQL-001.es.md) | Inyección SQL con datos de la petición (Node.js) | CRÍTICA | ALTA | CWE-89 | A05:2025 Inyección |
| [NODE-DES-001](NODE-DES-001.es.md) | Deserialización insegura (Node.js) | ALTA | MEDIA | CWE-502 | A08:2025 Fallas de integridad de software o datos |
| [NODE-JWT-001](NODE-JWT-001.es.md) | JWT con algoritmo none o sin validar la expiración (Node.js) | ALTA | ALTA | CWE-347 | A07:2025 Fallas de autenticación |
| [NODE-NOSQL-001](NODE-NOSQL-001.es.md) | Inyección NoSQL con datos de la petición (Node.js) | ALTA | MEDIA | CWE-943 | A05:2025 Inyección |
| [NODE-PATH-001](NODE-PATH-001.es.md) | Acceso a archivos con ruta controlada por la petición (Node.js) | ALTA | MEDIA | CWE-22 | A01:2025 Control de acceso roto |
| [NODE-SSRF-001](NODE-SSRF-001.es.md) | Solicitud del servidor a una URL controlada por la petición (SSRF, Node.js) | ALTA | MEDIA | CWE-918 | A01:2025 Control de acceso roto |
| [NODE-XSS-001](NODE-XSS-001.es.md) | XSS reflejado: datos de la petición en la respuesta sin escapar (Node.js) | ALTA | MEDIA | CWE-79 | A05:2025 Inyección |
| [NODE-CAND-001](NODE-CAND-001.es.md) | SQL armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-89 | A05:2025 Inyección |
| [NODE-CAND-002](NODE-CAND-002.es.md) | Comando armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-78 | A05:2025 Inyección |
| [NODE-CAND-003](NODE-CAND-003.es.md) | Ruta de archivo desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-22 | A01:2025 Control de acceso roto |
| [NODE-CAND-004](NODE-CAND-004.es.md) | Petición a una URL desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-918 | A01:2025 Control de acceso roto |
| [NODE-CAND-005](NODE-CAND-005.es.md) | Redirección a una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-601 | A01:2025 Control de acceso roto |
| [NODE-CAND-006](NODE-CAND-006.es.md) | Deserialización de una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-502 | A08:2025 Fallas de integridad de software o datos |
| [NODE-CAND-007](NODE-CAND-007.es.md) | XML analizado desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-611 | A02:2025 Configuración de seguridad incorrecta |
| [NODE-CONF-001](NODE-CONF-001.es.md) | CORS abierto a cualquier origen con credenciales (Node.js) | MEDIA | ALTA | CWE-942 | A02:2025 Configuración de seguridad incorrecta |
| [NODE-CONF-002](NODE-CONF-002.es.md) | Cookie de sesión insegura o secreto de sesión en el código (Node.js) | MEDIA | ALTA | CWE-1004 | A02:2025 Configuración de seguridad incorrecta |
| [NODE-CRY-001](NODE-CRY-001.es.md) | Criptografía débil o aleatoriedad predecible (Node.js) | MEDIA | MEDIA | CWE-327 | A04:2025 Fallas criptográficas |
| [NODE-JWT-002](NODE-JWT-002.es.md) | Secreto JWT escrito en el código (Node.js) | MEDIA | ALTA | CWE-798 | A07:2025 Fallas de autenticación |
| [NODE-JWT-003](NODE-JWT-003.es.md) | Token JWT decodificado sin verificar la firma (Node.js) | MEDIA | BAJA | CWE-345 | A07:2025 Fallas de autenticación |
| [NODE-RED-001](NODE-RED-001.es.md) | Redirección abierta con datos de la petición (Node.js) | MEDIA | MEDIA | CWE-601 | A01:2025 Control de acceso roto |
| [NODE-XSS-002](NODE-XSS-002.es.md) | HTML dinámico insertado en el DOM sin sanitizar (JavaScript) | MEDIA | BAJA | CWE-79 | A05:2025 Inyección |

## PHP y Laravel

| ID | Título | Severidad | Confianza | CWE | OWASP |
|---|---|---|---|---|---|
| [PHP-CALL-001](PHP-CALL-001.es.md) | Llamada dinámica con un nombre controlado por la petición (PHP) | CRÍTICA | MEDIA | CWE-94 | A05:2025 Inyección |
| [PHP-EXE-001](PHP-EXE-001.es.md) | Ejecución de comandos con entrada variable (PHP) | CRÍTICA | MEDIA | CWE-78 | A05:2025 Inyección |
| [PHP-SQL-001](PHP-SQL-001.es.md) | Inyección SQL con datos de la petición (PHP) | CRÍTICA | ALTA | CWE-89 | A05:2025 Inyección |
| [PHP-UPL-001](PHP-UPL-001.es.md) | Archivo subido guardado en una ruta controlada por el cliente (PHP) | CRÍTICA | MEDIA | CWE-434 | A06:2025 Diseño inseguro |
| [PHP-AUTH-002](PHP-AUTH-002.es.md) | Ruta sin middleware de autenticación (Laravel) | ALTA | BAJA | CWE-306 | A01:2025 Control de acceso roto |
| [PHP-CONF-001](PHP-CONF-001.es.md) | display_errors activo o credenciales en .env versionado | ALTA | MEDIA | CWE-209 | A02:2025 Configuración de seguridad incorrecta |
| [PHP-CRY-001](PHP-CRY-001.es.md) | Contraseñas con md5/sha1 (PHP) | ALTA | MEDIA | CWE-916 | A04:2025 Fallas criptográficas |
| [PHP-DES-001](PHP-DES-001.es.md) | Deserialización de datos de la petición (PHP) | ALTA | ALTA | CWE-502 | A08:2025 Fallas de integridad de software o datos |
| [PHP-INC-001](PHP-INC-001.es.md) | Inclusión de archivo con ruta variable (PHP) | ALTA | MEDIA | CWE-98 | A05:2025 Inyección |
| [PHP-SQL-002](PHP-SQL-002.es.md) | Inyección SQL a través de un parámetro de función (PHP) | ALTA | MEDIA | CWE-89 | A05:2025 Inyección |
| [PHP-XSS-001](PHP-XSS-001.es.md) | XSS: salida de datos de la petición sin escapar (PHP) | ALTA | ALTA | CWE-79 | A05:2025 Inyección |
| [PHP-CAND-001](PHP-CAND-001.es.md) | SQL armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-89 | A05:2025 Inyección |
| [PHP-CAND-002](PHP-CAND-002.es.md) | Comando armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-78 | A05:2025 Inyección |
| [PHP-CAND-003](PHP-CAND-003.es.md) | Ruta de archivo desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-22 | A01:2025 Control de acceso roto |
| [PHP-CAND-004](PHP-CAND-004.es.md) | Petición a una URL desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-918 | A01:2025 Control de acceso roto |
| [PHP-CAND-005](PHP-CAND-005.es.md) | Redirección a una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-601 | A01:2025 Control de acceso roto |
| [PHP-CAND-006](PHP-CAND-006.es.md) | Deserialización de una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-502 | A08:2025 Fallas de integridad de software o datos |
| [PHP-CAND-007](PHP-CAND-007.es.md) | XML analizado desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-611 | A02:2025 Configuración de seguridad incorrecta |
| [PHP-CONF-002](PHP-CONF-002.es.md) | Bandera de producción o depuración fija en el código (PHP) | MEDIA | MEDIA | CWE-489 | A02:2025 Configuración de seguridad incorrecta |
| [PHP-MAS-001](PHP-MAS-001.es.md) | Asignación masiva (Laravel) | MEDIA | MEDIA | CWE-915 | A06:2025 Diseño inseguro |

## Swift

| ID | Título | Severidad | Confianza | CWE | OWASP |
|---|---|---|---|---|---|
| [SWIFT-SEC-001](SWIFT-SEC-001.es.md) | Llave de API, secreto o contraseña escrita en el código (Swift/iOS) | ALTA | MEDIA | CWE-798 | A07:2025 Fallas de autenticación |
| [SWIFT-SQL-001](SWIFT-SQL-001.es.md) | Consulta SQL construida con texto (SQLite, GRDB o FMDB, Swift/iOS) | ALTA | MEDIA | CWE-89 | A05:2025 Inyección |
| [SWIFT-STO-001](SWIFT-STO-001.es.md) | Token o contraseña en UserDefaults o @AppStorage (Swift/iOS) | ALTA | MEDIA | CWE-312 | A04:2025 Fallas criptográficas |
| [SWIFT-TLS-001](SWIFT-TLS-001.es.md) | Validación de certificados TLS desactivada (Swift/iOS) | ALTA | ALTA | CWE-295 | A04:2025 Fallas criptográficas |
| [SWIFT-WEB-001](SWIFT-WEB-001.es.md) | WKWebView con puente de JavaScript hacia la aplicación (Swift/iOS) | ALTA | MEDIA | CWE-749 | A06:2025 Diseño inseguro |
| [SWIFT-WEB-002](SWIFT-WEB-002.es.md) | WKWebView con acceso universal a archivos locales (Swift/iOS) | ALTA | ALTA | CWE-749 | A06:2025 Diseño inseguro |
| [SWIFT-CAND-001](SWIFT-CAND-001.es.md) | SQL armado con una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-89 | A05:2025 Inyección |
| [SWIFT-CAND-002](SWIFT-CAND-002.es.md) | Ruta de archivo desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-22 | A01:2025 Control de acceso roto |
| [SWIFT-CAND-003](SWIFT-CAND-003.es.md) | Petición a una URL desde una variable (por revisar) (candidata) | MEDIA | BAJA | CWE-918 | A01:2025 Control de acceso roto |
| [SWIFT-CONF-001](SWIFT-CONF-001.es.md) | Configuración insegura en Info.plist o .entitlements (Swift/iOS) | MEDIA | ALTA | CWE-16 | A02:2025 Configuración de seguridad incorrecta |
| [SWIFT-CRY-001](SWIFT-CRY-001.es.md) | Criptografía débil o vector de inicialización fijo (Swift/iOS) | MEDIA | MEDIA | CWE-327 | A04:2025 Fallas criptográficas |
| [SWIFT-DES-001](SWIFT-DES-001.es.md) | Deserialización sin restricción de clases con NSKeyedUnarchiver (Swift/iOS) | MEDIA | ALTA | CWE-502 | A08:2025 Fallas de integridad de software o datos |
| [SWIFT-KEY-001](SWIFT-KEY-001.es.md) | Keychain con accesibilidad «siempre» (Swift/iOS) | MEDIA | ALTA | CWE-311 | A04:2025 Fallas criptográficas |
| [SWIFT-LOG-001](SWIFT-LOG-001.es.md) | Dato sensible escrito en el registro (Swift/iOS) | MEDIA | MEDIA | CWE-532 | A09:2025 Fallas de registro y alertas de seguridad |
| [SWIFT-NET-001](SWIFT-NET-001.es.md) | Dirección http:// sin cifrar en el código (Swift/iOS) | MEDIA | MEDIA | CWE-319 | A04:2025 Fallas criptográficas |
| [SWIFT-WEB-003](SWIFT-WEB-003.es.md) | UIWebView obsoleto e inseguro (Swift/iOS) | MEDIA | ALTA | CWE-477 | A03:2025 Fallas en la cadena de suministro de software |
