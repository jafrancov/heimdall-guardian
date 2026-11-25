# Demo project: Corner Shop

A small, **deliberately vulnerable** application made to show what Heimdall reports. It
mixes four stacks, as many real deliveries do:

- `backend/`: a Django service (SQL built with f-strings, a command run with `shell=True`,
  views without authentication, `DEBUG = True`, an unrestricted file upload) with an old
  `requirements.txt` and a `Dockerfile` with bad practices.
- `api/`: an Express service (NoSQL injection, permissive CORS, a weak session secret,
  unverified JWTs, path traversal, an unprotected delete endpoint) with a `package-lock.json`.
- `mobile/`: a Flutter app (tokens in `SharedPreferences`, `http://` addresses, accepting any
  certificate, a permissive Android manifest) with a `pubspec.lock`.
- `.env.example`: made-up secrets.

## Read this first

- **Do not deploy it and do not run it.** Every weakness is on purpose, and the old
  dependencies have known vulnerabilities.
- All credentials are made up. None is valid for any real service, and none uses a real
  provider format; they only look like secrets to the generic patterns.
- Quality tools (ruff, mypy, pytest, pre-commit) skip this folder.

## Analyze it

```bash
uv run hdl scan examples/demo-project --profile standard --output demo.html
```

Or open the folder from the desktop app (`uv run hdl ui`). For the dependency findings you
need the vulnerability databases (`uv run hdl databases --update`, about 1.4 GB); without
them the rest of the result is the same. Reports cannot be saved inside the analyzed folder,
so write them somewhere else.

You should see findings in every severity, several OWASP Top 10:2025 categories, the
endpoint inventory with and without authentication, and vulnerable dependencies.
