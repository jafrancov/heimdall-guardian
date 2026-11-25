# Rules catalog

Heimdall Guardian ships 124 own rules in Opengrep format. This catalog is generated from the rule files, so it always matches the version you install.

## Dart and Flutter

| ID | Title | Severity | Confidence | CWE | OWASP |
|---|---|---|---|---|---|
| [DART-SEC-001](DART-SEC-001.md) | Hard-coded API key, secret or password (Dart/Flutter) | HIGH | MEDIUM | CWE-798 | A07:2025 Authentication Failures |
| [DART-SQL-001](DART-SQL-001.md) | SQL query built from text (sqflite/drift, Dart/Flutter) | HIGH | MEDIUM | CWE-89 | A05:2025 Injection |
| [DART-STO-001](DART-STO-001.md) | Token or password in unencrypted storage (Dart/Flutter) | HIGH | MEDIUM | CWE-312 | A04:2025 Cryptographic Failures |
| [DART-TLS-001](DART-TLS-001.md) | TLS certificate validation disabled (Dart/Flutter) | HIGH | HIGH | CWE-295 | A04:2025 Cryptographic Failures |
| [DART-WEB-001](DART-WEB-001.md) | WebView with a JavaScript bridge to the application (Dart/Flutter) | HIGH | MEDIUM | CWE-749 | A06:2025 Insecure Design |
| [DART-CAND-001](DART-CAND-001.md) | SQL built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-89 | A05:2025 Injection |
| [DART-CAND-002](DART-CAND-002.md) | Command built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-78 | A05:2025 Injection |
| [DART-CAND-003](DART-CAND-003.md) | File path from a variable (to review) (candidate) | MEDIUM | LOW | CWE-22 | A01:2025 Broken Access Control |
| [DART-CAND-004](DART-CAND-004.md) | Request to a URL from a variable (to review) (candidate) | MEDIUM | LOW | CWE-918 | A01:2025 Broken Access Control |
| [DART-CONF-001](DART-CONF-001.md) | Insecure configuration in AndroidManifest.xml or Info.plist | MEDIUM | HIGH | CWE-16 | A02:2025 Security Misconfiguration |
| [DART-CRY-001](DART-CRY-001.md) | Weak cryptography or predictable randomness (Dart/Flutter) | MEDIUM | MEDIUM | CWE-327 | A04:2025 Cryptographic Failures |
| [DART-LOG-001](DART-LOG-001.md) | Sensitive data written to the log (Dart/Flutter) | MEDIUM | MEDIUM | CWE-532 | A09:2025 Security Logging and Alerting Failures |
| [DART-NET-001](DART-NET-001.md) | Unencrypted http:// address in the code (Dart/Flutter) | MEDIUM | MEDIUM | CWE-319 | A04:2025 Cryptographic Failures |
| [DART-WEB-002](DART-WEB-002.md) | WebView with JavaScript enabled (Dart/Flutter) | MEDIUM | LOW | CWE-749 | A06:2025 Insecure Design |

## Python and Django

| ID | Title | Severity | Confidence | CWE | OWASP |
|---|---|---|---|---|---|
| [DJ-CONF-002](DJ-CONF-002.md) | Literal SECRET_KEY in the code | CRITICAL | HIGH | CWE-798 | A07:2025 Authentication Failures |
| [DJ-AUTH-001](DJ-AUTH-001.md) | View without authentication (Django, FBV) | HIGH | LOW | CWE-306 | A01:2025 Broken Access Control |
| [DJ-AUTH-002](DJ-AUTH-002.md) | View without authentication (Django, CBV) | HIGH | LOW | CWE-306 | A01:2025 Broken Access Control |
| [DJ-AUTH-003](DJ-AUTH-003.md) | API without authentication: AllowAny (DRF) | HIGH | MEDIUM | CWE-306 | A01:2025 Broken Access Control |
| [DJ-CONF-001](DJ-CONF-001.md) | DEBUG turned on in settings | HIGH | MEDIUM | CWE-489 | A02:2025 Security Misconfiguration |
| [DJ-SQL-001](DJ-SQL-001.md) | Dynamic SQL in a direct query (Django) | HIGH | MEDIUM | CWE-89 | A05:2025 Injection |
| [DJ-AUTH-004](DJ-AUTH-004.md) | CSRF protection disabled (@csrf_exempt) | MEDIUM | HIGH | CWE-352 | A01:2025 Broken Access Control |
| [DJ-CAND-001](DJ-CAND-001.md) | SQL built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-89 | A05:2025 Injection |
| [DJ-CAND-002](DJ-CAND-002.md) | Command built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-78 | A05:2025 Injection |
| [DJ-CAND-003](DJ-CAND-003.md) | File path from a variable (to review) (candidate) | MEDIUM | LOW | CWE-22 | A01:2025 Broken Access Control |
| [DJ-CAND-004](DJ-CAND-004.md) | Request to a URL from a variable (to review) (candidate) | MEDIUM | LOW | CWE-918 | A01:2025 Broken Access Control |
| [DJ-CAND-005](DJ-CAND-005.md) | Redirect to a variable (to review) (candidate) | MEDIUM | LOW | CWE-601 | A01:2025 Broken Access Control |
| [DJ-CAND-006](DJ-CAND-006.md) | Deserialization of a variable (to review) (candidate) | MEDIUM | LOW | CWE-502 | A08:2025 Software or Data Integrity Failures |
| [DJ-CAND-007](DJ-CAND-007.md) | XML parsed from a variable (to review) (candidate) | MEDIUM | LOW | CWE-611 | A02:2025 Security Misconfiguration |
| [DJ-CONF-003](DJ-CONF-003.md) | ALLOWED_HOSTS or CORS open to any origin | MEDIUM | HIGH | CWE-942 | A02:2025 Security Misconfiguration |
| [DJ-CONF-004](DJ-CONF-004.md) | Insecure cookies or transport in settings | MEDIUM | MEDIUM | CWE-614 | A02:2025 Security Misconfiguration |
| [DJ-IDOR-001](DJ-IDOR-001.md) | Possible access to other people's objects (IDOR) | MEDIUM | LOW | CWE-639 | A01:2025 Broken Access Control |
| [DJ-UPL-001](DJ-UPL-001.md) | File upload without type or size validation | MEDIUM | LOW | CWE-434 | A06:2025 Insecure Design |
| [DJ-XSS-001](DJ-XSS-001.md) | Unescaped HTML: mark_safe with variable data | MEDIUM | MEDIUM | CWE-79 | A05:2025 Injection |
| [DJ-XSS-002](DJ-XSS-002.md) | Unescaped HTML in a template (\|safe, autoescape off) | MEDIUM | MEDIUM | CWE-79 | A05:2025 Injection |

## .NET

| ID | Title | Severity | Confidence | CWE | OWASP |
|---|---|---|---|---|---|
| [NET-CONF-001](NET-CONF-001.md) | Password in connection string (.NET) | CRITICAL | HIGH | CWE-798 | A07:2025 Authentication Failures |
| [NET-AUTH-001](NET-AUTH-001.md) | Controller without [Authorize] (.NET) | HIGH | LOW | CWE-306 | A01:2025 Broken Access Control |
| [NET-AUTH-002](NET-AUTH-002.md) | Anonymous write action ([AllowAnonymous]) | HIGH | HIGH | CWE-306 | A01:2025 Broken Access Control |
| [NET-CONF-003](NET-CONF-003.md) | CORS open with credentials (.NET) | HIGH | HIGH | CWE-942 | A02:2025 Security Misconfiguration |
| [NET-DES-001](NET-DES-001.md) | Insecure deserialization (.NET) | HIGH | HIGH | CWE-502 | A08:2025 Software or Data Integrity Failures |
| [NET-SQL-001](NET-SQL-001.md) | Dynamic SQL in a direct query (.NET) | HIGH | MEDIUM | CWE-89 | A05:2025 Injection |
| [NET-CAND-001](NET-CAND-001.md) | SQL built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-89 | A05:2025 Injection |
| [NET-CAND-002](NET-CAND-002.md) | Command built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-78 | A05:2025 Injection |
| [NET-CAND-003](NET-CAND-003.md) | File path from a variable (to review) (candidate) | MEDIUM | LOW | CWE-22 | A01:2025 Broken Access Control |
| [NET-CAND-004](NET-CAND-004.md) | Request to a URL from a variable (to review) (candidate) | MEDIUM | LOW | CWE-918 | A01:2025 Broken Access Control |
| [NET-CAND-005](NET-CAND-005.md) | Redirect to a variable (to review) (candidate) | MEDIUM | LOW | CWE-601 | A01:2025 Broken Access Control |
| [NET-CAND-006](NET-CAND-006.md) | Deserialization of a variable (to review) (candidate) | MEDIUM | LOW | CWE-502 | A08:2025 Software or Data Integrity Failures |
| [NET-CAND-007](NET-CAND-007.md) | XML parsed from a variable (to review) (candidate) | MEDIUM | LOW | CWE-611 | A02:2025 Security Misconfiguration |
| [NET-CONF-002](NET-CONF-002.md) | Insecure web.config (customErrors, debug, validateRequest) | MEDIUM | HIGH | CWE-16 | A02:2025 Security Misconfiguration |
| [NET-CRY-001](NET-CRY-001.md) | Weak cryptography (.NET) | MEDIUM | MEDIUM | CWE-327 | A04:2025 Cryptographic Failures |

## Kotlin and Android

| ID | Title | Severity | Confidence | CWE | OWASP |
|---|---|---|---|---|---|
| [KT-SEC-001](KT-SEC-001.md) | Hard-coded API key, secret or password (Kotlin/Android) | HIGH | MEDIUM | CWE-798 | A07:2025 Authentication Failures |
| [KT-SQL-001](KT-SQL-001.md) | SQL query built from text (SQLite or Room, Kotlin/Android) | HIGH | MEDIUM | CWE-89 | A05:2025 Injection |
| [KT-STO-001](KT-STO-001.md) | Token or password in SharedPreferences or DataStore (Kotlin/Android) | HIGH | MEDIUM | CWE-312 | A04:2025 Cryptographic Failures |
| [KT-STO-002](KT-STO-002.md) | File or preferences with permissions for other applications (Kotlin/Android) | HIGH | HIGH | CWE-732 | A01:2025 Broken Access Control |
| [KT-TLS-001](KT-TLS-001.md) | TLS certificate validation disabled (Kotlin/Android) | HIGH | HIGH | CWE-295 | A04:2025 Cryptographic Failures |
| [KT-WEB-001](KT-WEB-001.md) | WebView with addJavascriptInterface (Kotlin/Android) | HIGH | MEDIUM | CWE-749 | A06:2025 Insecure Design |
| [KT-CAND-001](KT-CAND-001.md) | SQL built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-89 | A05:2025 Injection |
| [KT-CAND-002](KT-CAND-002.md) | Command built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-78 | A05:2025 Injection |
| [KT-CAND-003](KT-CAND-003.md) | File path from a variable (to review) (candidate) | MEDIUM | LOW | CWE-22 | A01:2025 Broken Access Control |
| [KT-CAND-004](KT-CAND-004.md) | Request to a URL from a variable (to review) (candidate) | MEDIUM | LOW | CWE-918 | A01:2025 Broken Access Control |
| [KT-CONF-001](KT-CONF-001.md) | Exported component without permission or http traffic allowed (AndroidManifest.xml) | MEDIUM | LOW | CWE-926 | A02:2025 Security Misconfiguration |
| [KT-CRY-001](KT-CRY-001.md) | Weak cryptographic algorithm, fixed IV or insecure randomness (Kotlin/Android) | MEDIUM | MEDIUM | CWE-327 | A04:2025 Cryptographic Failures |
| [KT-INT-001](KT-INT-001.md) | Mutable PendingIntent, exposed receiver or broadcast without permission (Kotlin/Android) | MEDIUM | LOW | CWE-927 | A01:2025 Broken Access Control |
| [KT-LOG-001](KT-LOG-001.md) | Sensitive data written to the log (Kotlin/Android) | MEDIUM | MEDIUM | CWE-532 | A09:2025 Security Logging and Alerting Failures |
| [KT-NET-001](KT-NET-001.md) | Unencrypted http:// address in the code (Kotlin/Android) | MEDIUM | MEDIUM | CWE-319 | A04:2025 Cryptographic Failures |
| [KT-WEB-002](KT-WEB-002.md) | WebView with local file access or an address taken from an Intent (Kotlin/Android) | MEDIUM | LOW | CWE-749 | A06:2025 Insecure Design |

## Node.js and TypeScript

| ID | Title | Severity | Confidence | CWE | OWASP |
|---|---|---|---|---|---|
| [NODE-EXE-001](NODE-EXE-001.md) | Command injection with request data (Node.js) | CRITICAL | HIGH | CWE-78 | A05:2025 Injection |
| [NODE-EXE-002](NODE-EXE-002.md) | Code execution with request data (Node.js) | CRITICAL | HIGH | CWE-95 | A05:2025 Injection |
| [NODE-SQL-001](NODE-SQL-001.md) | SQL injection with request data (Node.js) | CRITICAL | HIGH | CWE-89 | A05:2025 Injection |
| [NODE-DES-001](NODE-DES-001.md) | Insecure deserialization (Node.js) | HIGH | MEDIUM | CWE-502 | A08:2025 Software or Data Integrity Failures |
| [NODE-JWT-001](NODE-JWT-001.md) | JWT with the none algorithm or without expiration validation (Node.js) | HIGH | HIGH | CWE-347 | A07:2025 Authentication Failures |
| [NODE-NOSQL-001](NODE-NOSQL-001.md) | NoSQL injection with request data (Node.js) | HIGH | MEDIUM | CWE-943 | A05:2025 Injection |
| [NODE-PATH-001](NODE-PATH-001.md) | File access with a request-controlled path (Node.js) | HIGH | MEDIUM | CWE-22 | A01:2025 Broken Access Control |
| [NODE-SSRF-001](NODE-SSRF-001.md) | Server-side request to a request-controlled URL (SSRF, Node.js) | HIGH | MEDIUM | CWE-918 | A01:2025 Broken Access Control |
| [NODE-XSS-001](NODE-XSS-001.md) | Reflected XSS: request data in the response without escaping (Node.js) | HIGH | MEDIUM | CWE-79 | A05:2025 Injection |
| [NODE-CAND-001](NODE-CAND-001.md) | SQL built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-89 | A05:2025 Injection |
| [NODE-CAND-002](NODE-CAND-002.md) | Command built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-78 | A05:2025 Injection |
| [NODE-CAND-003](NODE-CAND-003.md) | File path from a variable (to review) (candidate) | MEDIUM | LOW | CWE-22 | A01:2025 Broken Access Control |
| [NODE-CAND-004](NODE-CAND-004.md) | Request to a URL from a variable (to review) (candidate) | MEDIUM | LOW | CWE-918 | A01:2025 Broken Access Control |
| [NODE-CAND-005](NODE-CAND-005.md) | Redirect to a variable (to review) (candidate) | MEDIUM | LOW | CWE-601 | A01:2025 Broken Access Control |
| [NODE-CAND-006](NODE-CAND-006.md) | Deserialization of a variable (to review) (candidate) | MEDIUM | LOW | CWE-502 | A08:2025 Software or Data Integrity Failures |
| [NODE-CAND-007](NODE-CAND-007.md) | XML parsed from a variable (to review) (candidate) | MEDIUM | LOW | CWE-611 | A02:2025 Security Misconfiguration |
| [NODE-CONF-001](NODE-CONF-001.md) | CORS open to any origin with credentials (Node.js) | MEDIUM | HIGH | CWE-942 | A02:2025 Security Misconfiguration |
| [NODE-CONF-002](NODE-CONF-002.md) | Insecure session cookie or hard-coded session secret (Node.js) | MEDIUM | HIGH | CWE-1004 | A02:2025 Security Misconfiguration |
| [NODE-CRY-001](NODE-CRY-001.md) | Weak cryptography or predictable randomness (Node.js) | MEDIUM | MEDIUM | CWE-327 | A04:2025 Cryptographic Failures |
| [NODE-JWT-002](NODE-JWT-002.md) | Hard-coded JWT secret (Node.js) | MEDIUM | HIGH | CWE-798 | A07:2025 Authentication Failures |
| [NODE-JWT-003](NODE-JWT-003.md) | JWT decoded without verifying the signature (Node.js) | MEDIUM | LOW | CWE-345 | A07:2025 Authentication Failures |
| [NODE-RED-001](NODE-RED-001.md) | Open redirect with request data (Node.js) | MEDIUM | MEDIUM | CWE-601 | A01:2025 Broken Access Control |
| [NODE-XSS-002](NODE-XSS-002.md) | Dynamic HTML inserted into the DOM without sanitizing (JavaScript) | MEDIUM | LOW | CWE-79 | A05:2025 Injection |

## PHP and Laravel

| ID | Title | Severity | Confidence | CWE | OWASP |
|---|---|---|---|---|---|
| [PHP-CALL-001](PHP-CALL-001.md) | Dynamic call with a request-controlled name (PHP) | CRITICAL | MEDIUM | CWE-94 | A05:2025 Injection |
| [PHP-EXE-001](PHP-EXE-001.md) | Command execution with variable input (PHP) | CRITICAL | MEDIUM | CWE-78 | A05:2025 Injection |
| [PHP-SQL-001](PHP-SQL-001.md) | SQL injection with request data (PHP) | CRITICAL | HIGH | CWE-89 | A05:2025 Injection |
| [PHP-UPL-001](PHP-UPL-001.md) | Uploaded file stored under a client-controlled path (PHP) | CRITICAL | MEDIUM | CWE-434 | A06:2025 Insecure Design |
| [PHP-AUTH-002](PHP-AUTH-002.md) | Route without authentication middleware (Laravel) | HIGH | LOW | CWE-306 | A01:2025 Broken Access Control |
| [PHP-CONF-001](PHP-CONF-001.md) | display_errors on or credentials in a versioned .env | HIGH | MEDIUM | CWE-209 | A02:2025 Security Misconfiguration |
| [PHP-CRY-001](PHP-CRY-001.md) | Passwords hashed with md5/sha1 (PHP) | HIGH | MEDIUM | CWE-916 | A04:2025 Cryptographic Failures |
| [PHP-DES-001](PHP-DES-001.md) | Deserialization of request data (PHP) | HIGH | HIGH | CWE-502 | A08:2025 Software or Data Integrity Failures |
| [PHP-INC-001](PHP-INC-001.md) | File inclusion with a variable path (PHP) | HIGH | MEDIUM | CWE-98 | A05:2025 Injection |
| [PHP-SQL-002](PHP-SQL-002.md) | SQL injection through a function parameter (PHP) | HIGH | MEDIUM | CWE-89 | A05:2025 Injection |
| [PHP-XSS-001](PHP-XSS-001.md) | XSS: request data output without escaping (PHP) | HIGH | HIGH | CWE-79 | A05:2025 Injection |
| [PHP-CAND-001](PHP-CAND-001.md) | SQL built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-89 | A05:2025 Injection |
| [PHP-CAND-002](PHP-CAND-002.md) | Command built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-78 | A05:2025 Injection |
| [PHP-CAND-003](PHP-CAND-003.md) | File path from a variable (to review) (candidate) | MEDIUM | LOW | CWE-22 | A01:2025 Broken Access Control |
| [PHP-CAND-004](PHP-CAND-004.md) | Request to a URL from a variable (to review) (candidate) | MEDIUM | LOW | CWE-918 | A01:2025 Broken Access Control |
| [PHP-CAND-005](PHP-CAND-005.md) | Redirect to a variable (to review) (candidate) | MEDIUM | LOW | CWE-601 | A01:2025 Broken Access Control |
| [PHP-CAND-006](PHP-CAND-006.md) | Deserialization of a variable (to review) (candidate) | MEDIUM | LOW | CWE-502 | A08:2025 Software or Data Integrity Failures |
| [PHP-CAND-007](PHP-CAND-007.md) | XML parsed from a variable (to review) (candidate) | MEDIUM | LOW | CWE-611 | A02:2025 Security Misconfiguration |
| [PHP-CONF-002](PHP-CONF-002.md) | Hard-coded production/debug flag (PHP) | MEDIUM | MEDIUM | CWE-489 | A02:2025 Security Misconfiguration |
| [PHP-MAS-001](PHP-MAS-001.md) | Mass assignment (Laravel) | MEDIUM | MEDIUM | CWE-915 | A06:2025 Insecure Design |

## Swift

| ID | Title | Severity | Confidence | CWE | OWASP |
|---|---|---|---|---|---|
| [SWIFT-SEC-001](SWIFT-SEC-001.md) | Hard-coded API key, secret or password (Swift/iOS) | HIGH | MEDIUM | CWE-798 | A07:2025 Authentication Failures |
| [SWIFT-SQL-001](SWIFT-SQL-001.md) | SQL query built from text (SQLite, GRDB or FMDB, Swift/iOS) | HIGH | MEDIUM | CWE-89 | A05:2025 Injection |
| [SWIFT-STO-001](SWIFT-STO-001.md) | Token or password in UserDefaults or @AppStorage (Swift/iOS) | HIGH | MEDIUM | CWE-312 | A04:2025 Cryptographic Failures |
| [SWIFT-TLS-001](SWIFT-TLS-001.md) | TLS certificate validation disabled (Swift/iOS) | HIGH | HIGH | CWE-295 | A04:2025 Cryptographic Failures |
| [SWIFT-WEB-001](SWIFT-WEB-001.md) | WKWebView with a JavaScript bridge to the application (Swift/iOS) | HIGH | MEDIUM | CWE-749 | A06:2025 Insecure Design |
| [SWIFT-WEB-002](SWIFT-WEB-002.md) | WKWebView with universal access to local files (Swift/iOS) | HIGH | HIGH | CWE-749 | A06:2025 Insecure Design |
| [SWIFT-CAND-001](SWIFT-CAND-001.md) | SQL built from a variable (to review) (candidate) | MEDIUM | LOW | CWE-89 | A05:2025 Injection |
| [SWIFT-CAND-002](SWIFT-CAND-002.md) | File path from a variable (to review) (candidate) | MEDIUM | LOW | CWE-22 | A01:2025 Broken Access Control |
| [SWIFT-CAND-003](SWIFT-CAND-003.md) | Request to a URL from a variable (to review) (candidate) | MEDIUM | LOW | CWE-918 | A01:2025 Broken Access Control |
| [SWIFT-CONF-001](SWIFT-CONF-001.md) | Insecure configuration in Info.plist or .entitlements (Swift/iOS) | MEDIUM | HIGH | CWE-16 | A02:2025 Security Misconfiguration |
| [SWIFT-CRY-001](SWIFT-CRY-001.md) | Weak cryptography or fixed initialization vector (Swift/iOS) | MEDIUM | MEDIUM | CWE-327 | A04:2025 Cryptographic Failures |
| [SWIFT-DES-001](SWIFT-DES-001.md) | Deserialization without class restriction using NSKeyedUnarchiver (Swift/iOS) | MEDIUM | HIGH | CWE-502 | A08:2025 Software or Data Integrity Failures |
| [SWIFT-KEY-001](SWIFT-KEY-001.md) | Keychain item with «always» accessibility (Swift/iOS) | MEDIUM | HIGH | CWE-311 | A04:2025 Cryptographic Failures |
| [SWIFT-LOG-001](SWIFT-LOG-001.md) | Sensitive data written to the log (Swift/iOS) | MEDIUM | MEDIUM | CWE-532 | A09:2025 Security Logging and Alerting Failures |
| [SWIFT-NET-001](SWIFT-NET-001.md) | Unencrypted http:// address in the code (Swift/iOS) | MEDIUM | MEDIUM | CWE-319 | A04:2025 Cryptographic Failures |
| [SWIFT-WEB-003](SWIFT-WEB-003.md) | Deprecated and insecure UIWebView (Swift/iOS) | MEDIUM | HIGH | CWE-477 | A03:2025 Software Supply Chain Failures |
