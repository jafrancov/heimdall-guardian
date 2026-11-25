# NODE-CONF-002: Insecure session cookie or hard-coded session secret (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Insecure session or cookie: a cookie without httpOnly or secure, or a session secret written in the code. An injected script can read the cookie, it travels over unencrypted connections, and anyone who can read the repository can forge sessions.

## How to fix it

Set httpOnly: true, secure: true (behind HTTPS, with trust proxy if applicable) and sameSite: 'lax' or 'strict'. Read the session secret from an environment variable (process.env.SESSION_SECRET).

## Why it matters

This rule maps to [CWE-1004](https://cwe.mitre.org/data/definitions/1004.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Check the session cookie's attributes: it should carry `HttpOnly` so that scripts on the page cannot read it.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | HIGH |
| Category | CONFIGURATION |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-1004](https://cwe.mitre.org/data/definitions/1004.html) |
| OWASP | A02:2025 Security Misconfiguration |
