# Your own rules

You can add your own [Opengrep](https://opengrep.dev) rules to the built-in ones, for
example to check a convention of your company. They are YAML files in the same format as
the built-in rules.

## Where to put them

Use a folder **outside** the project you analyze, for example `~/heimdall-rules`. A folder
inside the analyzed project is ignored: the analyzed code must never configure the analysis,
and a vendor could ship rules that hide findings.

Tell Heimdall Guardian where it is, either in `config.toml`:

```toml
[rules]
extra_dirs = ["~/heimdall-rules"]
```

or in **Settings → Your own rules** in the app, where **Check rules** shows the result
right away. Every `.yaml` and `.yml` file in those folders is read.

## Format

```yaml
rules:
  - id: ACME-SQL-001
    languages: [php]
    message: Query built by concatenating user input.
    pattern: $DB->query("..." . $_GET[...] . "...")
    severity: ERROR
    metadata:
      cwe: CWE-89
      owasp: "A05:2025 Injection"
      severity_hdl: high          # critical | high | medium | low | info
      confidence: medium          # high | medium | low
      title: SQL query built from user input
      recommendation: Use prepared statements with bound parameters.
      title_es: Consulta SQL armada con datos del usuario     # optional
      recommendation_es: Usa consultas preparadas con parámetros.   # optional
    message_es: Consulta armada concatenando datos del usuario.   # optional
```

`languages`, `message`, a matcher (`pattern`, `patterns`, `pattern-either`, `pattern-regex`
or a taint rule) and the metadata above are required. `owasp` uses the 2025 labels.

## IDs

An ID looks like `XX-TAG-NNN` (`ACME-SQL-001`). The tag decides where the finding goes:
`CONF` is configuration, `AUTH` and `IDOR` are access control, any other is code. You cannot
reuse the ID of a built-in rule, repeat an ID in your rules, use the `AI-` prefix or the
`CAND` tag: they are reserved.

## What is checked

Before each analysis the structure of every file is checked, and then the engine validates
its syntax. A file with a problem is skipped whole, the analysis goes on, and the result
declares which file was skipped and why. To check without analyzing:

```bash
uv run hdl rules --check             # the configured folders
uv run hdl rules --check --dir ~/heimdall-rules
```

## In the reports

Reports record the rule files and IDs of your rules, and they change the rules version, so
a result can be traced to the exact rules that produced it.
