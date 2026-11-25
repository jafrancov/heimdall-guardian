# PHP-CALL-001: Dynamic call with a request-controlled name (PHP)

[Back to the rules catalog](index.md)

## What it detects

A function, method or class name comes from the request and is called dynamically ($name(...), call_user_func, new $class, $object-&gt;$method()). The visitor chooses which code runs, so they can reach any function of the application or of PHP itself.

## How to fix it

Never call a name taken from the request. Map the accepted values to the functions or classes you allow (a fixed array checked with in_array($x, $list, true) or array_key_exists) and reject anything else before calling. A check with function_exists or is_callable is not enough: it also accepts every function PHP provides.

## Why it matters

This rule maps to [CWE-94](https://cwe.mitre.org/data/definitions/94.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Look for any external data reaching a function that runs code. Replace it with a closed list of allowed operations.

## Facts

| | |
|---|---|
| Severity | CRITICAL |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-94](https://cwe.mitre.org/data/definitions/94.html) |
| OWASP | A05:2025 Injection |
