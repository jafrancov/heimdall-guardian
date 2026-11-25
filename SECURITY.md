# Security

[Leer en español → SECURITY.es.md](SECURITY.es.md)

## Reporting a vulnerability in Heimdall Guardian

If you find a security flaw in this tool, do not open a public issue. Use **Security →
Report a vulnerability** in the GitHub repository (private report). Include which version
you use, how to reproduce it and what impact you see.

Of particular interest is any way for the analyzed code to:

- get executed or launch a program during the analysis;
- write inside or outside the analyzed folder;
- hide findings through configuration files or comments;
- make code, secrets or inventories leave the local network;
- manipulate the AI model to change a result;
- appear unmasked (a secret) in a report.

## Scope of the tool

Heimdall Guardian performs static analysis. It does not replace penetration testing or
manual review of business logic. A result with no findings does not mean the code is
secure.
