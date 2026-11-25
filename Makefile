.PHONY: setup tools bundle wheel cli-wheel cli-archive app lint format typecheck test qa docs docs-serve outdated upgrade

setup: tools  ## environment + tools + git hooks (global pre-commit)
	uv sync
	pre-commit install

tools:  ## downloads gitleaks, osv-scanner and opengrep (pinned version + SHA-256)
	uv run python tools/fetch_tools.py

bundle:  ## rules + binaries inside the package (for distribution)
	uv run python tools/build_bundle.py

wheel: bundle  ## self-contained installable package in dist/
	uv build --wheel

cli-wheel:  ## light command-line wheel (rules, no binaries) in dist/cli/; rebuilds _bundle
	uv run python tools/build_cli_wheel.py

cli-archive: cli-wheel  ## CLI-only archive for servers (install_hdl.py + wheel) in dist/
	uv run python tools/build_cli_archive.py

app:  ## desktop app and installer for this OS (see CONTRIBUTING)
	uv run python tools/build_app.py

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy

test:
	uv run pytest --cov

outdated:  ## report outdated packages, pinned tools and GitHub Actions (informs only)
	uv run python tools/check_outdated.py

upgrade:  ## try upgrading dependencies; keeps them only if QA is green (PACKAGE=name for one)
	uv run python tools/try_upgrade.py $(foreach p,$(PACKAGE),--package $(p))

qa:  ## everything that runs before each commit
	pre-commit run --all-files

docs:  ## regenerates the generated docs pages and builds the site with strict checks
	uv run python tools/build_rule_docs.py
	uv run --group docs mkdocs build --strict

docs-serve:  ## live preview of the documentation site
	uv run python tools/build_rule_docs.py
	uv run --group docs mkdocs serve
