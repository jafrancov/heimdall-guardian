"""Visible messages, English (source language). Keys are stable; values use `str.format`.

Every key must exist in `messages_es` with the same placeholders
(`tests/unit/test_i18n_messages.py` enforces it). Plurals use
`.one` / `.other` key pairs (see `tn`).
"""

from __future__ import annotations

MESSAGES: dict[str, str] = {
    "cli.lang.help": ("interface language: en or es (overrides HDL_LANG and config.toml)"),
    "lang.error.unsupported": "Unsupported language: {value}. Options: {options}.",
    "core.ai.progress": "reviewing {done} of {total}",
    "cli.description": (
        "Heimdall Guardian: local, read-only static security analysis of source code."
    ),
    "cli.help.help": "show this help message and exit",
    "cli.help.version": "show the version and exit",
    "cli.metavar.folder": "folder",
    "cli.metavar.name": "NAME",
    "cli.metavar.folder_upper": "FOLDER",
    "cli.metavar.date": "YYYY-MM-DD",
    "cli.metavar.file_json": "FILE.json",
    "cli.metavar.file_targz": "FILE.tar.gz",
    "cli.arg.folder": "project folder (never modified)",
    "cli.arg.output": (
        "output file; the format comes from the extension ({formats}). Can be repeated. Without "
        "this option, JSON goes to standard output"
    ),
    "cli.scan.help": "analyzes a folder and generates the report",
    "cli.scan.profile": (
        "analysis profile: quick, standard, full, vendor or custom (default: the configured one, "
        "or standard)"
    ),
    "cli.scan.modules": "modules of the custom profile, separated by commas: {modules}",
    "cli.scan.dry_run": "lists what would be analyzed, without running any tool",
    "cli.scan.update_databases": "allows downloading the vulnerability databases before analyzing",
    "cli.scan.exclude": (
        "folder, file or file pattern that is not analyzed in this run (can be repeated), "
        "e.g. build, src/vendor/big.js or '*.spec.ts'"
    ),
    "cli.scan.exclude_gitignored": (
        "also skip, in this run, what git ignores in the folder (without git, what the root "
        ".gitignore lists by plain name)"
    ),
    "cli.scan.include": (
        "folder that is analyzed even if it is skipped by default (can be repeated)"
    ),
    "cli.scan.ai": "AI configuration used in this analysis (default: the active one)",
    "cli.scan.issuer": "who issues the verdict (vendor profile); default: the system user",
    "cli.scan.no_baseline": "does not compare with earlier runs and does not save this run",
    "cli.report.help": "regenerates reports from a saved run",
    "cli.report.run": "run number (default: the latest)",
    "cli.runs.help": "lists the project's saved runs",
    "cli.forget.help": "deletes a project's history (its folder is not touched)",
    "cli.forget.yes": "confirms the deletion",
    "cli.suppress.help": "accepts a finding's risk or marks it as a false positive",
    "cli.suppress.id": "finding ID, e.g. HDL-2026-000012",
    "cli.suppress.status": "accepted or false_positive",
    "cli.suppress.reason": "justification (required)",
    "cli.suppress.review": "review date; when it passes, the finding counts again",
    "cli.suppress.author": "who decides (default: the system user)",
    "cli.unsuppress.help": "removes a finding's suppression",
    "cli.unsuppress.id": "finding ID",
    "cli.suppressions.help": "lists the current suppressions",
    "cli.tools.help": "shows the available tools and their version",
    "cli.tools.news": "checks online for newer versions (downloads nothing)",
    "cli.thresholds.help": "shows or changes the verdict thresholds (requires a PIN)",
    "cli.thresholds.set_pin": "sets or changes the PIN",
    "cli.thresholds.log": "shows the changes made",
    "cli.thresholds.count_ai": "whether AI suggestions count toward the verdict (yes or no)",
    "cli.baseline.help": "exports or imports the project's baseline (findings and suppressions)",
    "cli.baseline.export": "writes the baseline to a file",
    "cli.baseline.import": "adds the baseline from a file",
    "cli.databases.help": "status of the vulnerability databases; export or import them",
    "cli.databases.update": "downloads or updates the databases now",
    "cli.databases.export": "packs the databases into a file",
    "cli.databases.import": "loads the databases from a file",
    "cli.llm.help": "tests the connection to the AI destinations",
    "cli.llm.destination": "destination name (default: the active one)",
    "cli.llm.save_token": "asks for the destination's token and saves it in the system keychain",
    "cli.ui.help": "opens the desktop interface",
    "cli.ui.web": "serves it on a local port",
    "cli.ui.port": "port for --web (default: any free one)",
    "cli.config.help": "shows where the configuration is",
    "cli.config.init": "creates the file if it does not exist",
    "cli.error": "Error: {error}",
    "cli.error.not_folder": "Not a folder: {path}",
    "cli.error.output_inside": "{option} cannot be inside the analyzed folder.",
    "cli.error.format": "Unsupported format: {name}. Extensions: {formats}.",
    "cli.error.modules_need_custom": "{modules} only applies with {profile} custom.",
    "cli.error.bad_profile": "Unknown profile: {value}. Options: {valid}.",
    "cli.error.bad_status": "Unknown status: {value}. Options: {valid}.",
    "cli.error.bad_yes_no": "Expected yes or no, not {value}.",
    "cli.plan.folder": "Folder:   {path}",
    "cli.plan.stack": "Stack:    {stacks}",
    "cli.plan.stack_none": "none detected",
    "cli.plan.profile": "Profile:  {profile} ({modules})",
    "cli.plan.no_modules": "no modules",
    "cli.plan.pending": "          not yet available: {modules}",
    "cli.plan.files": "Files:    {count}",
    "cli.plan.gitignored": "Ignored by git and skipped in this run: {count} entries ({source})",
    "cli.plan.gitignored_source.git": "git",
    "cli.plan.gitignored_source.gitignore": ".gitignore",
    "cli.plan.subprojects": "This folder holds {count} projects: {names}.",
    "cli.plan.subprojects_hint": "To analyze one on its own: hdl scan {example}",
    "cli.plan.suggested": "Suggested to skip: {pattern} ({reason}), e.g. {example}",
    "cli.plan.suggested_hint": (
        'Add them with --exclude NAME, or in the app under "Folders to skip".'
    ),
    "core.presets.reason.stack": "Usual in {stack} projects",
    "core.presets.reason.tool": "Editor or AI-assistant folder",
    "core.presets.reason.gitignore": "Listed in the project's .gitignore",
    "cli.report.written": "Report:  {path}",
    "cli.summary.tool_line": "{name:<9} {status:<9} {count:>4} finding(s)",
    "cli.summary.open": "Open: {counts}",
    "cli.summary.run": "Run {run}: {counts}",
    "cli.summary.limitation": "Limitation: {text}",
    "cli.summary.verdict": "Verdict: {outcome}",
    "cli.summary.criterion": "  {name}: {found} (maximum {limit}) {mark}",
    "cli.summary.exceeded": "EXCEEDED",
    "cli.summary.met": "met",
    "cli.progress.ai": "  AI: {status}",
    "cli.forget.confirm": (
        "This deletes the project's analyses, baseline and accepted risks. Repeat the command "
        "with {option} to confirm."
    ),
    "cli.forget.none": "That project has no saved history.",
    "cli.forget.done": "Project history deleted. The project folder was not modified.",
    "cli.runs.none": "There are no saved runs for this project.",
    "cli.runs.counts": "(new {new}, fixed {fixed})",
    "cli.suppress.done": (
        "{id}: {status}. It is already reflected in the latest run and its reports."
    ),
    "cli.unsuppress.done": "{id}: suppression removed.",
    "cli.unsuppress.none": "{id} had no current suppression.",
    "cli.suppressions.none": "There are no current suppressions.",
    "cli.suppressions.review": ", review on {date}",
    "cli.tools.unknown_version": "unknown version",
    "cli.tools.not_installed": "not installed",
    "cli.tools.database": "  (database: {date})",
    "cli.tools.install": "downloads the pinned tools (checked by SHA-256) into the data folder",
    "cli.tools.missing": (
        "\nMissing tools: {names}.\nRun `hdl tools --install` to download them (about "
        "150 MB), or copy the tools folder from a machine that has the Heimdall Guardian app."
    ),
    "cli.tools.install_no_manifest": "This installation does not carry the list of pinned tools.",
    "cli.tools.install_no_platform": "There are no pinned tools for this system ({platform}).",
    "cli.tools.install_start": "Installing the tools into {path}",
    "cli.tools.install_downloaded": (
        "{name} {version}: downloaded {transferred} and installed ({size})"
    ),
    "cli.tools.install_present": "{name} {version}: already installed ({size})",
    "cli.tools.install_done": ("Done: {count} downloaded, {total} in total, in {path}"),
    "cli.tools.install_failed": (
        "Could not install the tools: {error}\nWithout internet, copy the folder {path} "
        "from a machine with the Heimdall Guardian app."
    ),
    "cli.ui.no_flet": (
        "The desktop interface is not installed here. Install the Heimdall Guardian app, "
        'or add it to this command with `pip install "heimdall-guardian[ui]"`.'
    ),
    "tools.install.only_https": "Only https URLs are downloaded: {url}",
    "tools.install.no_member": "{member} is not a file inside the package",
    "tools.install.unsafe_member": "{member} is not a safe file name inside the package",
    "tools.install.hash_mismatch": (
        "{name} {version}: the SHA-256 does not match; not installing.\n"
        "  expected: {expected}\n  actual:   {actual}"
    ),
    "cli.tools.news_header": (
        "\nPublished versions (checks GitHub and PyPI; sends nothing from your code):"
    ),
    "cli.tools.news_notes": "\nRelease notes:",
    "cli.tools.news_pinned": (
        "\nEach tool is pinned with a version and SHA-256 so the analysis is reproducible, so it "
        "does not update itself. If you use the installer, they arrive with the next version of "
        "Heimdall Guardian. If you build it yourself: change the version, URL and hash in "
        "tools/tools.toml, run the integration tests and build the installer."
    ),
    "cli.llm.no_destination": "There is no AI destination {name} in the configuration.",
    "cli.llm.token_prompt": "Token for {name}: ",
    "cli.llm.token_saved": "Token for {name} saved in the system keychain.",
    "cli.llm.destination_line": "Destination: {name} ({runtime}) {url}",
    "cli.llm.state_offline": "Status:      not connected ({error})",
    "cli.llm.state_online": "Status:      connected, {count} model(s) available",
    "cli.llm.model_line": "Model for {task}: {note}",
    "cli.llm.model_unset": "not set",
    "cli.llm.model_missing": "  (not among the destination's models)",
    "cli.llm.test_system": "Reply in English, in one sentence.",
    "cli.llm.test_user": "Say “connection OK”.",
    "cli.llm.test_failed": "Test:        failed ({error})",
    "cli.llm.test_ok": "Test:        {text} in {seconds:.1f} s ({speed:.0f} tokens/s)",
    "cli.config.created": "Configuration created: {path}",
    "cli.config.missing": "{path}  (does not exist; defaults are used)",
    "cli.config.exists": "{path}",
    "cli.thresholds.pin_current": "Current PIN: ",
    "cli.thresholds.pin_new": "New PIN: ",
    "cli.thresholds.pin_repeat": "Repeat the new PIN: ",
    "cli.thresholds.pin_prompt": "PIN: ",
    "cli.thresholds.pin_saved": "PIN saved.",
    "cli.thresholds.updated": "Thresholds updated; the change was recorded in the log.",
    "cli.thresholds.default": "  (default: {value})",
    "cli.baseline.need_option": "Use {export} or {import_}.",
    "cli.baseline.imported": "Imported: {findings} findings and {suppressions} new suppressions.",
    "cli.baseline.inside": "The baseline is not exported inside the analyzed folder.",
    "cli.baseline.exported": "Exported {count} findings to {path}.",
    "cli.databases.imported": "Databases imported: {count} files.",
    "cli.databases.exported": "Databases exported to {path}: {count} files.",
    "cli.databases.location": "Location: {path}",
    "cli.databases.dated": "{name:<9} database of {date}",
    "lang.name.en": "English",
    "lang.name.es": "Spanish",
    "config.notice.old_version": (
        "Your configuration file is from an older version and was not "
        "loaded: {path}. Defaults are in use; rename or delete the "
        "file, then save the settings again."
    ),
    "ui.window.title": "Heimdall Guardian",
    "ui.brand.tagline": "Your code's guardian",
    "ui.brand.motto": "Vigilance and prevention",
    "ui.brand.home_tip": "Back to the welcome screen",
    "ui.nav.new_analysis": "New analysis",
    "ui.nav.new_analysis_tip": "Back to the welcome screen (⌘N or Ctrl+N)",
    "ui.nav.coverage": "What it checks",
    "ui.nav.coverage_tip": "The OWASP categories and what Heimdall Guardian covers",
    "ui.nav.settings": "Settings",
    "ui.nav.settings_tip": "Settings",
    "ui.nav.about": "About",
    "ui.nav.about_tip": "About Heimdall Guardian",
    "ui.common.cancel": "Cancel",
    "ui.common.close": "Close",
    "ui.common.save": "Save",
    "ui.question.depth": "How thorough",
    "ui.question.which_folder": "Which folder shall we check?",
    "ui.question.local_note": "It is analyzed on this computer. Nothing is modified or run.",
    "ui.question.no_stack": "no recognized stack",
    "ui.question.files_stacks": "{count} files · {stacks}",
    "ui.action.analyze": "Analyze",
    "ui.action.choose_folder": "Choose folder",
    "ui.action.change_folder": "Change folder",
    "ui.action.preview": "Preview",
    "ui.subprojects.title.one": "This folder holds {count} project",
    "ui.subprojects.title.other": "This folder holds {count} projects",
    "ui.subprojects.help": "Analyze it all together, or open one to analyze it on its own.",
    "ui.subprojects.open_tip": "Open {name} as its own project",
    "ui.action.skip_folders": "Folders to skip",
    "ui.action.skip_folders_suggested.one": "Folders to skip ({count} suggested)",
    "ui.action.skip_folders_suggested.other": "Folders to skip ({count} suggested)",
    "ui.action.update_bases_on_scan": "Update the databases when analyzing",
    "ui.action.update_bases_now": "Update the databases now",
    "ui.bases.downloading": "Downloading the databases…",
    "ui.bases.none": (
        "There are no vulnerability databases yet: they will be downloaded (about 2 GB)."
    ),
    "ui.bases.updated_today": "Vulnerability databases updated today.",
    "ui.bases.updated_ago.one": "Vulnerability databases updated {count} day ago.",
    "ui.bases.updated_ago.other": "Vulnerability databases updated {count} days ago.",
    "ui.bases.partial_failure": "Not all the databases were updated. {detail}",
    "ui.bases.updated": "Vulnerability databases updated.",
    "ui.ai.time_warning": (
        "With AI, the analysis can take several minutes: it depends on "
        "the model and on your computer's capacity."
    ),
    "ui.ai.choice_label": "AI for this analysis",
    "ui.custom.issuer": "Who issues the verdict",
    "ui.profile.steps": "Checks: {steps}",
    "ui.profile.verdict_step": "Verdict",
    "ui.profile.quick.name": "Quick",
    "ui.profile.quick.desc": "Secrets, dependencies and configuration. Under 2 minutes.",
    "ui.profile.standard.name": "Standard",
    "ui.profile.standard.desc": "Before a release: adds insecure code and access control.",
    "ui.profile.full.name": "Full",
    "ui.profile.full.desc": "Audit: adds git history and AI review.",
    "ui.profile.vendor.name": "Vendor delivery",
    "ui.profile.vendor.desc": "Receiving third-party code, with a verdict.",
    "ui.profile.custom.name": "Custom",
    "ui.profile.custom.desc": "You choose what is checked.",
    "ui.module.sec": "Secrets",
    "ui.module.sec_h": "Git history",
    "ui.module.dep": "Dependencies",
    "ui.module.conf": "Configuration",
    "ui.module.sast": "Insecure code",
    "ui.module.authz": "Access control",
    "ui.module.ai": "AI review",
    "ui.module.sbom": "Inventory (SBOM)",
    "ui.tool.gitleaks": "Secrets",
    "ui.tool.trivy": "Dependencies and configuration",
    "ui.tool.osv": "Dependencies (second source)",
    "ui.tool.vendored": "Copied libraries",
    "ui.tool.opengrep": "Built-in code rules",
    "ui.tool.opengrep_for": "{names} code (built-in rules)",
    "ui.list.and": "{first} and {last}",
    "ui.tool.bandit": "Python code",
    "ui.tool.authz": "Endpoint inventory",
    "ui.tool.llm": "AI review",
    "ui.tool.summary": "AI executive summary",
    "ui.tool.result": "Saving the result",
    "ui.tool.unknown_version": "unknown version",
    "ui.tool.database": "{detail}, database from {date}",
    "ui.tool.not_installed": "not installed",
    "ui.home.not_analyzed": "{name} has not been analyzed yet.",
    "ui.home.not_analyzed_hint": (
        "Choose how thorough and press Analyze. With “Preview” you see "
        "which files are included, without running anything."
    ),
    "ui.home.path_hint": "or paste the folder path here",
    "ui.home.check.sec": "Passwords, keys and tokens, in the history too.",
    "ui.home.check.dep": "Libraries with known flaws.",
    "ui.home.check.sast": "Injection, XSS, commands, weak cryptography.",
    "ui.home.check.authz": "Pages and endpoints without authentication.",
    "ui.home.title": "Choose a folder and I will tell you how secure its code is.",
    "ui.home.subtitle": (
        "Where each problem is, why it matters and how to fix it. "
        "Everything is analyzed on this computer: nothing is modified "
        "or run."
    ),
    "ui.home.no_projects": "You have not checked any project yet.",
    "ui.home.watch_critical.one": (
        "You watch {count} project; {critical} with open critical problems."
    ),
    "ui.home.watch_critical.other": (
        "You watch {count} projects; {critical} with open critical problems."
    ),
    "ui.home.watch_clear.one": "You watch {count} project; none with open critical problems.",
    "ui.home.watch_clear.other": "You watch {count} projects; none with open critical problems.",
    "ui.recent.title": "Recent analyses",
    "ui.recent.remove_tip": "Remove from history",
    "ui.recent.forget_title": "Remove {name} from the history?",
    "ui.recent.forget_body": (
        "Its saved analyses, its baseline and the accepted or "
        "dismissed risks are deleted. The reports you already saved "
        "and the project folder are not touched."
    ),
    "ui.recent.forget_irreversible": "This cannot be undone.",
    "ui.recent.forgotten": "{name} was removed from the history.",
    "ui.picker.choose": "Folder to analyze",
    "ui.scan.running": "Analyzing {name}",
    "ui.scan.keep_working": "You can keep working; the folder is not touched.",
    "ui.scan.busy": "An analysis is in progress. Cancel it before starting another.",
    "ui.scan.cancel_notice": "It cancels when the tool or the AI query in progress finishes.",
    "ui.scan.status.start": "analyzing…",
    "ui.scan.status.done": "done",
    "ui.scan.status.skipped": "not available",
    "ui.scan.status.error": "failed; continuing without it",
    "ui.scan.status.in_progress": "in progress…",
    "ui.scan.cancelled": "Analysis cancelled. Nothing was saved.",
    "ui.scan.failed": "The analysis could not be completed: {error}",
    "ui.result.save_report": "Save report:",
    "ui.result.endpoints": "{count} endpoints, {open} without authentication",
    "ui.result.how": "How it was analyzed",
    "ui.result.limitations.one": "{count} limitation of this run",
    "ui.result.limitations.other": "{count} limitations of this run",
    "ui.result.context": "{comparison} Analyzed on {date} with the {profile} profile.",
    "ui.result.search_hint": "Search by file, rule or text",
    "ui.result.ai_summary": "Summary written by AI ({model})",
    "ui.result.hide_suppressed": "Hide the {count} accepted or dismissed",
    "ui.result.show_suppressed": "Show the {count} accepted or dismissed",
    "ui.result.stratum_tip": "Show only these; another click shows them all",
    "ui.result.no_open": "No open findings",
    "ui.result.nothing_matches": "Nothing matches what you are looking for.",
    "ui.severity_name.critical.one": "critical",
    "ui.severity_name.critical.other": "critical",
    "ui.severity_name.high.one": "high",
    "ui.severity_name.high.other": "high",
    "ui.severity_name.medium.one": "medium",
    "ui.severity_name.medium.other": "medium",
    "ui.severity_name.low.one": "low",
    "ui.severity_name.low.other": "low",
    "ui.severity_name.info.one": "informational",
    "ui.severity_name.info.other": "informational",
    "ui.verdict.critical.headline": "It is not ready to be released yet.",
    "ui.verdict.critical.why": "Open: {critical}.",
    "ui.verdict.critical.why_high": "Open: {critical} and {high}.",
    "ui.verdict.high.headline": "It can be fixed soon, but not today.",
    "ui.verdict.high.why": "No critical findings; {high} still to address.",
    "ui.verdict.rest.headline": "No serious problems.",
    "ui.verdict.rest.why": "{count} of lower severity are left to review at your own pace.",
    "ui.verdict.clean.headline": "Nothing was found that needs fixing.",
    "ui.verdict.clean.why": ("This analysis is static: it does not replace a penetration test."),
    "ui.delivery.not_approved": "The delivery cannot be accepted.",
    "ui.delivery.approved_with_observations": "The delivery is accepted with observations.",
    "ui.delivery.approved": "The delivery can be accepted.",
    "ui.delivery.exceeds": "Exceeded: {criteria}.",
    "ui.delivery.criterion": "{name} ({found}, maximum {maximum})",
    "ui.delivery.mediums": "{count} medium findings remain, with a commitment to fix them.",
    "ui.delivery.within": "No verdict threshold is exceeded.",
    "ui.compare.first": "First run of this project.",
    "ui.compare.since": "Since run {previous}: {parts}.",
    "ui.compare.new": "{count} new",
    "ui.compare.fixed": "{count} fixed",
    "ui.compare.persistent": "{count} unchanged",
    "ui.compare.accepted": "{count} accepted or dismissed",
    "ui.finding.ai_suggestion": "AI suggestion · {state}",
    "ui.finding.what": "What is happening",
    "ui.finding.how_fix": "How to fix it",
    "ui.finding.classification": "Classification",
    "ui.finding.model": "Model: {model}",
    "ui.finding.accept": "Accept the risk",
    "ui.finding.false_positive": "It is a false positive",
    "ui.finding.recount": "Count it again",
    "ui.finding.recounted": "{id} counts again.",
    "ui.finding.saved": "{id} saved. The result and the reports already reflect it.",
    "ui.finding.reason": "Justification (required)",
    "ui.finding.review_date": "Review again on (YYYY-MM-DD, optional)",
    "ui.finding.mark_false_positive": "Mark as false positive",
    "ui.finding.unknown_user": "unknown",
    "ui.expert.title": "For experts",
    "ui.expert.subtitle": "Rule, classification, exact location and how to verify it",
    "ui.expert.rule": "Rule",
    "ui.expert.tool": "Tool",
    "ui.expert.cwe": "CWE",
    "ui.expert.owasp": "OWASP",
    "ui.expert.confidence": "Confidence",
    "ui.expert.location": "Location",
    "ui.expert.verify": "How to verify it",
    "ui.ai.verdict.likely_real": "Probably real",
    "ui.ai.verdict.likely_false": "Probably false",
    "ui.ai.verdict.uncertain": "Uncertain",
    "ui.ai.level.high": "high",
    "ui.ai.level.medium": "medium",
    "ui.ai.level.low": "low",
    "ui.ai.risk_level.high": "high",
    "ui.ai.risk_level.medium": "medium",
    "ui.ai.risk_level.low": "low",
    "ui.ai.risk_level.none": "none",
    "ui.ai.opinion": "{verdict} (confidence {level}).",
    "ui.ai.risk": "risk of {name}: {level}",
    "ui.ai.risk_name.idor": "access to other people's records",
    "ui.ai.risk_name.flow": "skipping or repeating steps",
    "ui.ai.suggested_fix": "Suggested fix: {fix}",
    "ui.ai.reachable": "Reachable from user input: {answer}",
    "ui.ai.reachable.yes": "yes",
    "ui.ai.reachable.no": "no",
    "ui.ai.reachable.unclear": "unclear",
    "ui.ai.source": "Input: {source}",
    "ui.ai.risk_name.sink": "an attack through this operation",
    "ui.facts.ai_new_findings.one": (
        "The AI found {count} possible problem that the rules "
        "alone do not report; check it before acting."
    ),
    "ui.facts.ai_new_findings.other": (
        "The AI found {count} possible problems that the rules "
        "alone do not report; check them before acting."
    ),
    "ui.facts.ai_sinks_clear.one": "The AI reviewed {count} risk point and found nothing to add.",
    "ui.facts.ai_sinks_clear.other": (
        "The AI reviewed {count} risk points and found nothing to add."
    ),
    "ui.how.title": "How it was analyzed",
    "ui.how.profile": "Profile {profile}: {modules}.",
    "ui.facts.ran": "Ran: {tools}.",
    "ui.facts.failed": "Could not run: {tools}.",
    "ui.facts.no_ai": "No AI review: this profile does not include it.",
    "ui.facts.ai_ran": "AI review: model {model}. {detail}{summary}",
    "ui.facts.ai_summary_yes": " It wrote the summary.",
    "ui.facts.ai_summary_no": " It did not write a summary.",
    "ui.facts.unnamed_model": "unnamed",
    "ui.facts.ai_failed": "The AI review did not run: {detail}.",
    "ui.facts.unavailable": "not available",
    "ui.limitations.title": "Limitations of this run",
    "ui.endpoints.title": "Endpoint inventory",
    "ui.endpoints.any_method": "any",
    "ui.endpoints.protected": "with authentication",
    "ui.endpoints.unprotected": "without authentication",
    "ui.endpoints.unknown": "undetermined",
    "ui.folders.title": "Folders to skip",
    "ui.folders.suggested_title": "Suggested for this project",
    "ui.folders.suggested_help": (
        "They look like build output, caches or tool folders. Nothing is skipped until you save."
    ),
    "ui.folders.vendor_note": (
        "Receiving vendor code: editor, assistant and .gitignore folders start unchecked, "
        "because code can hide there."
    ),
    "ui.folders.patterns_label": "Files to skip (patterns, comma separated)",
    "ui.folders.patterns_hint": "e.g. *.spec.ts, docs/*.md",
    "ui.folders.patterns_help": (
        "Manifests and lockfiles such as package.json are always analyzed, and secrets are "
        "searched in every file."
    ),
    "ui.folders.choose_first": "Choose a folder first.",
    "ui.folders.by_default": "{folder}   (skipped by default)",
    "ui.folders.none": "This folder has no subfolders.",
    "ui.folders.will_analyze": "{count} files will be analyzed.",
    "ui.folders.help": (
        "Check the folders you do not want analyzed in this project. "
        "This is remembered for the next analyses."
    ),
    "ui.preview.title": "{count} files would be analyzed",
    "ui.preview.modules": "Modules: {modules}",
    "ui.preview.excluded": "Not included: {folders}",
    "ui.settings.title": "Settings",
    "ui.settings.analysis": "Analysis",
    "ui.settings.language": "Idioma / Language",
    "ui.settings.default_profile": "Profile on open",
    "ui.settings.never_analyzed": "Folders that are never analyzed: {folders}.",
    "ui.settings.extra_folders": ("Other folders to skip (comma-separated, e.g. legacy, docs/old)"),
    "ui.settings.user_rules": "Your own rules",
    "ui.settings.user_rules_help": (
        "Folders with Opengrep rules in YAML that are added to the built-in ones. They are "
        "checked before each analysis; a rule with errors is skipped and the result says why."
    ),
    "ui.settings.user_rules_dirs": "Rule folders (comma-separated, e.g. ~/heimdall-rules)",
    "ui.settings.user_rules_check": "Check rules",
    "ui.settings.user_rules_checking": "Checking...",
    "ui.settings.user_rules_none": "No rule folders.",
    "ui.settings.user_rules_ok.one": "{count} rule ready in {files} files",
    "ui.settings.user_rules_ok.other": "{count} rules ready in {files} files",
    "ui.settings.user_rules_problem": "{file}: {detail}",
    "ui.settings.user_rules_more.one": "and {count} more",
    "ui.settings.user_rules_more.other": "and {count} more",
    "ui.settings.user_rules_no_engine": (
        "The rule engine is not available, so only the structure was checked."
    ),
    "ui.settings.ai_section": "AI review",
    "ui.settings.use_ai": "Use AI review",
    "ui.settings.ai_help": (
        "Register one or more AI servers, each with its models. It can "
        "be the same server with other models."
    ),
    "ui.settings.tools": "Tools",
    "ui.settings.checking_versions": "Checking the versions…",
    "ui.cli.title": "Command line",
    "ui.cli.installed": "The hdl command is installed: {path}",
    "ui.cli.installed_version": "Installed version: {version}",
    "ui.cli.not_installed": "The hdl command is not installed.",
    "ui.cli.note": (
        "It shares the databases and the history with this app. After installing it, open a "
        "new terminal to use it."
    ),
    "ui.cli.needs_internet": "The first time it needs internet to download what it uses.",
    "ui.cli.install": "Install the hdl command",
    "ui.cli.uninstall": "Uninstall the hdl command",
    "ui.cli.no_python": (
        "Installing the command needs Python {minimum} or newer, and none was found on this "
        "computer."
    ),
    "ui.cli.download_python": "Download Python",
    "ui.cli.unavailable": (
        "This copy of the app does not include the command installer. Get install_hdl.py from "
        "the project's release page."
    ),
    "ui.cli.checking": "Looking for Python…",
    "ui.cli.running_install": "Installing the command. This can take a minute…",
    "ui.cli.running_uninstall": "Removing the command…",
    "ui.cli.result.installed_title": "The hdl command is ready",
    "ui.cli.result.installed": "The command is at {path}.",
    "ui.cli.result.reopen": "Open a new terminal to use it.",
    "ui.cli.result.install_failed": "The command could not be installed",
    "ui.cli.result.uninstalled_title": "The hdl command was removed",
    "ui.cli.result.uninstalled": ("Your databases, history and settings were not touched."),
    "ui.cli.result.uninstall_failed": "The command could not be removed",
    "ui.cli.result.last_lines": "The last lines of the installer:",
    "ui.cli.result.no_output": "The installer printed nothing.",
    "ui.cli.offer.title": "The hdl command",
    "ui.cli.offer.body": (
        "Do you also want the hdl command for the terminal? It lets you analyze from the "
        "command line and automate, sharing databases and history with this app."
    ),
    "ui.cli.offer.install": "Install it",
    "ui.cli.offer.later": "Not now",
    "ui.cli.offer.later_note": "If you skip it now, you can do it later in Settings.",
    "ui.settings.thresholds": "Verdict thresholds",
    "ui.settings.language_busy": "Change the language when the analysis finishes.",
    "ui.settings.not_saved": "Not saved: {error}",
    "ui.settings.saved": "Settings saved in {path}",
    "ui.thresholds.title": "Verdict thresholds",
    "ui.thresholds.help": (
        "They decide whether a vendor delivery can be accepted. Every "
        "change asks for the PIN and is recorded with user and date."
    ),
    "ui.thresholds.max_critical": "Critical",
    "ui.thresholds.max_secrets": "Secrets",
    "ui.thresholds.max_unauth_write_endpoints": "Write endpoints without authentication",
    "ui.thresholds.max_high": "High",
    "ui.thresholds.max_patchable_critical_deps": "Critical dependencies with a patch",
    "ui.thresholds.maximum": "Maximum: {label}",
    "ui.thresholds.count_ai": "Count AI suggestions",
    "ui.thresholds.pin": "PIN",
    "ui.thresholds.pin_new": "New PIN (at least 6 characters)",
    "ui.thresholds.pin_repeat": "Repeat the new PIN",
    "ui.thresholds.pin_mismatch": "The PINs do not match.",
    "ui.thresholds.invalid": "Invalid value: {error}",
    "ui.thresholds.saved": "Thresholds saved; the change was recorded in the log.",
    "ui.thresholds.changes": "Changes recorded in the log: {count}",
    "ui.coverage.title": "What Heimdall Guardian checks",
    "ui.coverage.what_is": "What OWASP is",
    "ui.coverage.edition": "The categories follow the OWASP Top 10:{year}.",
    "ui.coverage.yes": "Yes",
    "ui.coverage.partial": "Partly",
    "ui.coverage.no": "No",
    "ui.coverage.none_open": "No open findings",
    "ui.coverage.open.one": "{count} open",
    "ui.coverage.open.other": "{count} open",
    "ui.coverage.example": "For example: {example}",
    "ui.tour.indicator": "Step {current} of {total}",
    "ui.tour.next": "Next",
    "ui.tour.back": "Back",
    "ui.tour.skip": "Skip",
    "ui.tour.start": "Get started",
    "ui.tour.replay": "Take the tour again",
    "ui.tour.what.title": "What Heimdall Guardian does",
    "ui.tour.what.body": (
        "It reviews the code in a folder on your computer and tells you which security "
        "risks it has, ordered by severity, with how to fix each one. It works without "
        "internet, except to update its databases."
    ),
    "ui.tour.wont.title": "What it does not do",
    "ui.tour.wont.body": (
        "It does not change your folder, does not run your code and does not send it "
        "anywhere: the AI is optional and only runs on your computer. It does not replace "
        "a review by a person."
    ),
    "ui.tour.read.title": "How to read the result",
    "ui.tour.read.body": (
        "The sentence at the top, in traffic-light colors, sums it up. The bands by "
        "severity filter the list, and each finding explains what is happening and how to "
        "fix it. You can accept a risk or mark a false positive, always with a reason."
    ),
    "ui.about.author": "Author: {author}. License Apache-2.0.",
    "ui.about.description": (
        "Static security analysis of source code, local and read-only: "
        "it checks for secrets, vulnerable dependencies, insecure code "
        "and endpoints without authentication, and tells you where "
        "each problem is and how to fix it."
    ),
    "ui.about.guarantees": (
        "It only reads the folder you choose, never runs its code and "
        "nothing leaves your network. It does not replace penetration "
        "tests or a manual review of the business logic."
    ),
    "ui.about.third_party": "Third-party components",
    "ui.about.license_line": "{name}: license {license}",
    "ui.about.third_party_note": (
        "They are included unmodified; their full licenses come with the application."
    ),
    "ui.about.graphics": "Graphic elements",
    "ui.about.art_notice_original": (
        "Original legal notice, kept in Spanish as its author wrote it."
    ),
    "ui.export.dialog_title": "Save report",
    "ui.export.inside_folder": (
        "The report is not saved inside the analyzed folder. Choose another place."
    ),
    "ui.export.failed": "Could not save: {error}",
    "ui.export.saved": "Report saved in {path}",
    "ui.aiedit.use": "Use",
    "ui.settings.ai_reasoning": "Let the model reason before answering (slower)",
    "llm.limit.low_valid": (
        "The model answered in an unusable format in {invalid} of {asked} queries "
        '({truncated} cut off for length). If it is a reasoning model, set reasoning = "off" '
        "for this destination, or raise its limits."
    ),
    "ui.aiedit.fallback": "If it does not respond, use",
    "ui.aiedit.add": "Add AI configuration",
    "ui.aiedit.unnamed": "Unnamed ({number})",
    "ui.aiedit.none": "None",
    "ui.aiedit.keep_one": "Keep at least one configuration.",
    "ui.aiedit.testing": "Testing…",
    "ui.aiedit.connected": "Connected. Models: {models}",
    "ui.aiedit.no_models": "none",
    "ui.aiedit.no_connection": "No connection: {error}",
    "ui.aiedit.name": "Name (e.g. office)",
    "ui.aiedit.url": "Server address",
    "ui.aiedit.remove_tip": "Remove this configuration",
    "ui.aiedit.test": "Test connection",
    "ui.aiedit.models_none": "no models",
    "ui.aitask.triage": "Model for assessing findings",
    "ui.aitask.endpoints": "Model for reviewing endpoints",
    "ui.aitask.sinks": "Model for reviewing risky operations (optional)",
    "ui.aitask.summary": "Model for the summary",
    "ui.aitask.consensus": "Second contrast model (optional)",
    "ui.aiform.at_least_one": "Keep at least one AI configuration.",
    "ui.aiform.name_required": "Give configuration {number} a name.",
    "ui.aiform.duplicate": "There are two configurations named «{name}».",
    # --- I3-A: core, reports, storage, adapters and AI ---
    "core.error.not_a_folder": "Not a folder: {path}",
    "core.examples.few": "e.g. {paths}",
    "core.examples.many": "e.g. {paths} and others",
    "core.limit.pending_modules": "Modules not yet available in this version: {names}.",
    "core.limit.partial_module": "Module {module} is partial: {reason}.",
    "core.limit.not_installed": "{tool} is not installed: reduced coverage in {affected}.",
    "core.limit.tool_failed": "{tool} failed: reduced coverage in {affected}.",
    "core.limit.db_old": (
        "The {tool} vulnerability database is {age} days old: anything published since may be "
        "missing. Update it with --update-databases."
    ),
    "core.limit.ai_disabled": "AI is turned off: the analysis ran without the AI module.",
    "core.limit.ai_unavailable": (
        "AI is not available ({detail}): the analysis continued without it."
    ),
    "core.tool.ai_stats": (
        "target {destination}; {valid} of {asked} replies valid; {cached} taken from the cache; "
        "{sinks_reviewed} risk points reviewed, {sinks_found} possible problems."
    ),
    "core.tool.ai_stats_detail": (
        "target {destination}; {valid} of {asked} replies valid; {cached} taken from the cache; "
        "{sinks_reviewed} risk points reviewed, {sinks_found} possible problems. {detail}"
    ),
    "core.tool.no_ai_config": "no AI configuration",
    "core.tool.not_installed": "not installed",
    "core.coverage.note": (
        "{name}: secrets, dependencies and configuration are checked; there are no {missing} yet."
    ),
    "core.coverage.missing_rules": "built-in code rules",
    "core.coverage.missing_both": "built-in code rules or endpoint inventory",
    "verdict.criterion.max_critical": "Critical findings",
    "verdict.criterion.max_secrets": "Secrets in the code or in the git history",
    "verdict.criterion.max_unauth_write_endpoints": "Write endpoints without authentication",
    "verdict.criterion.max_patchable_critical_deps": (
        "Dependencies with a critical vulnerability and a fixed version available"
    ),
    "verdict.criterion.max_high": "High findings",
    "core.verdict.unknown_threshold": "Unknown threshold: {names}.",
    "core.verdict.invalid_value": "Invalid value for {name}: {value}.",
    "core.config.legacy": (
        "{path} is from an earlier version (keys in Spanish) and is no longer read. Rename or "
        "delete it and create a new one with `hdl config --init` (or from Settings in the app)."
    ),
    "core.config.no_ai_config": "There is no AI configuration {name}. Available: {known}.",
    "core.config.unknown_option": "Unknown option in {where}: {names}.",
    "core.config.incomplete": "Section {where} is incomplete: {error}.",
    "core.config.unreadable": "Could not read {path}: {error}",
    "core.config.unknown_section": "Unknown section in {file}: {names}.",
    "core.config.bad_language": (
        "Unsupported language in [general] language: {value}. Use {first} or {second}, or leave it "
        "empty."
    ),
    "core.config.bad_reasoning": (
        'Unsupported reasoning in the AI destination {name}: {value}. Use "off" or "on".'
    ),
    "core.profiles.custom_needs_module": "The custom profile needs at least one module.",
    "core.profiles.unknown_profile": "Unknown profile: {profile}. Options: {valid}.",
    "core.profiles.unknown_module": "Unknown module: {module}. Options: {valid}.",
    "storage.archived": (
        "The history from an earlier version was archived ({name}): this run starts a new baseline."
    ),
    "storage.archived_exclusions": (
        "The saved folder exclusions of this project use an old format and were archived "
        "({name}): set them again if you still need them."
    ),
    "storage.suppression_expired": (
        "The suppression of {id} expired on {date}: the finding counts again."
    ),
    "storage.error.data_inside_folder": (
        "The Heimdall Guardian data directory is inside the analyzed folder; choose a more "
        "specific folder."
    ),
    "storage.error.no_runs": "There are no saved runs for this project.",
    "storage.error.no_such_run": "Run {run} does not exist in this project.",
    "storage.error.no_such_finding": "Finding {id} does not exist in this project.",
    "storage.error.bad_suppression_status": "A suppression can only be accepted or false positive.",
    "storage.error.justification_required": "A justification is required.",
    "storage.error.bad_baseline_file": "Not a valid baseline file: {error}",
    "storage.error.bad_baseline_format": "Unsupported baseline format: {format}.",
    "storage.error.digest_mismatch": (
        "The fingerprint does not match: the file was modified or is damaged."
    ),
    "storage.error.bad_imported_status": "Invalid suppression status: {status}.",
    "storage.error.imported_without_justification": "An imported suppression has no justification.",
    "bases.error.nothing_to_export": (
        "There are no local databases to export: run `hdl databases --update` first."
    ),
    "bases.error.bad_package": "The file is not a valid database package: {name}",
    "bases.state.updated": "updated",
    "bases.state.not_installed": "not installed",
    "bases.state.failed": "could not update: {detail}",
    "bases.downloading": "Downloading the {name} database ({step} of {total})…",
    "bases.size_notice": (
        "The vulnerability databases weigh about 2 GB. On a slow connection the download "
        "can take a long while, even if nothing seems to move; let it finish."
    ),
    "bases.still_downloading": "{step} {elapsed}",
    "bases.elapsed.minutes": "{minutes} min {seconds} s",
    "bases.elapsed.seconds": "{seconds} s",
    "bases.lock.waiting": (
        "Another Heimdall window or command is updating the databases; waiting for it to finish…"
    ),
    "bases.lock.timeout": (
        "The databases are still being updated by another Heimdall window or command. "
        "Try again when it finishes."
    ),
    "core.paths.data": "Data folder: {path}{source}",
    "core.paths.bases": "Databases folder: {path}{source}",
    "core.paths.from_env": " (set by {variable})",
    "cli.hint.app": (
        "Tip: on this computer you can also analyze with a click in the Heimdall Guardian app: "
        "{url}"
    ),
    "ui.bases.download_label": "download",
    "thresholds.error.no_pin": "There is no PIN yet: set one before changing the thresholds.",
    "thresholds.error.pin_mismatch": "The PIN does not match.",
    "thresholds.error.pin_too_short": "The PIN must be at least {minimum} characters long.",
    "thresholds.archived": (
        "The verdict thresholds file from an earlier version was archived ({names}); the "
        "default thresholds apply and the PIN was not carried over: set a new one before "
        "changing them."
    ),
    "thresholds.log.pin_set": "PIN set",
    "thresholds.log.pin_changed": "PIN changed",
    "thresholds.log.changed": "thresholds changed",
    "adapter.timeout": "time limit exceeded ({seconds} s)",
    "adapter.run_failed": "could not run {command}: {error}",
    "adapter.binary_missing": "{binary} is not installed",
    "adapter.failed": "{tool} failed: {detail}",
    "adapter.unreadable_report": "{tool}: unreadable report ({error})",
    "adapter.unreadable_output": "{tool}: unreadable output ({error})",
    "adapter.db.missing": (
        "The vulnerability databases are missing on this computer, so dependencies were not "
        'checked. Download them by ticking "Update the databases when analyzing" in the app, or '
        "with --update-databases in the terminal (about 2 GB the first time). "
        "Looked in: {path}.{hint}"
    ),
    # Starts with a space: it is appended after the sentence that ends with the path.
    "adapter.db.isolated_hint": (
        " HDL_DATA_DIR is set, so the databases are looked up there; point HDL_BASES_DIR at "
        "your usual databases to reuse them."
    ),
    "adapter.db.missing_short": "the vulnerability database is missing",
    "adapter.gitleaks.no_history": (
        "No git history: secrets were only searched for in the current files."
    ),
    "adapter.opengrep.no_rules": "no built-in rules found in {path}",
    "adapter.osv.db_of": "the database for {names}",
    "adapter.osv.db_of_one": "the database for an ecosystem",
    "adapter.osv.db_missing": (
        "OSV does not have {named} on this computer; update the databases to check those "
        "dependencies. Looked in: {path}.{hint}"
    ),
    "updates.status.error": "could not check ({error})",
    "updates.status.not_installed": "not installed; the latest is {latest}",
    "updates.status.no_release": "no published version",
    "updates.status.newer": "a newer one is available: {latest}",
    "updates.status.up_to_date": "up to date",
    "cli.version.help": "shows the installed version (--check compares it with the latest release)",
    "cli.version.check": "checks online for a newer release (sends nothing from your code)",
    "cli.version.latest": "Latest release: {latest} ({status})",
    "cli.version.page": "Release page: {page}",
    "cli.version.update": (
        "To update a command installed with install_hdl.py, download {wheel} from that page "
        "and run:\n  python3 install_hdl.py --wheel {wheel}\n"
        "Once the package is on PyPI you can run: python3 install_hdl.py --version {latest}"
    ),
    "updates.self.error": "could not check ({error})",
    "updates.self.no_release": "no published release yet",
    "updates.self.newer": "a newer version is available: {latest}",
    "updates.self.ahead": "newer than the latest release ({latest})",
    "updates.self.current": "up to date",
    "ui.about.update_check": "Check for updates",
    "ui.about.update_checking": "Checking...",
    "ui.about.update_open": "Open release page",
    "ui.about.update_line": "Installed {installed}: {status}",
    "llm.ai_label": "AI suggestion — needs human validation",
    "llm.destination.invalid_url": "Invalid target URL: {url}.",
    "llm.destination.credentials": "The target URL must not include credentials.",
    "llm.destination.not_local": (
        "The target {host} is not local and is not in allowed_hosts: it is rejected so the code "
        "does not leave the local network."
    ),
    "llm.destination.https_required": "The target {host} is not local: it must use HTTPS.",
    "llm.model.cloud": (
        "The model {model} runs in the cloud: it is rejected so the code does not leave the local "
        "network."
    ),
    "llm.client.token_missing": (
        "The target {name} requires a token and there is none in the keychain."
    ),
    "llm.client.http_error": "HTTP {code}: {detail}",
    "llm.client.no_connection": "no connection to {name}: {error}",
    "llm.client.unreadable": "unreadable reply from the target",
    "llm.client.empty": "reply with no content",
    "llm.problem": "{name}: {error}",
    "llm.limit.fallback": "AI: the target {destination} was used ({problems}).",
    "llm.limit.generic": "AI: {error}",
    "llm.limit.query_failed": "AI: a query failed ({error}).",
    "llm.limit.cancelled": "AI: cancelled after reviewing {done} of {total} targets.",
    "llm.limit.no_triage_model": "AI: no triage model configured.",
    "llm.limit.no_endpoint_model": "AI: no endpoint review model configured.",
    "llm.limit.no_summary": "AI: the executive summary was not generated ({error}).",
    "llm.detail.disabled": "AI is turned off in the settings",
    "llm.detail.no_destinations": "no AI targets are configured",
    "llm.detail.problems": "{problems}",
    "llm.detail.stopped": "the target stopped responding: {error}",
    "llm.detail.cancelled": "review cancelled",
    "llm.invalid_reply": "The model did not give a valid reply.",
    "llm.finding.title": "{label}: possible {what} in {route}",
    "llm.finding.what_idor": "access to other people's records by changing an identifier",
    "llm.finding.what_flow": "process steps that can be skipped or repeated",
    "llm.finding.any_method": "any",
    "llm.finding.title_sink": "{label}: {what} in {file}",
    "llm.finding.what_sql": "possible SQL injection",
    "llm.finding.what_exec": "possible command injection",
    "llm.finding.what_path": "possible path traversal",
    "llm.finding.what_ssrf": "possible SSRF",
    "llm.finding.what_redirect": "possible open redirect",
    "llm.finding.what_deser": "possible unsafe deserialization",
    "llm.finding.what_xxe": "possible XML external entity injection",
    "llm.finding.description_sink": "{explanation}\n\nInput: {source}",
    "llm.finding.recommendation_sink": (
        "Review the code manually. If confirmed, do not build the operation from user data: "
        "use parameters, an allow-list or a strict conversion before it reaches this point."
    ),
    "llm.finding.recommendation": (
        "Review the handler manually. If confirmed, validate that the record belongs to whoever is "
        "asking and that each step verifies the state of the process."
    ),
    "authz.note.unreadable": "Could not read {file}.",
    "authz.note.not_python": "Could not read {file} as Python.",
    "authz.note.module_not_found": "The routes module {module} was not found.",
    "authz.note.too_large": "{file} is too large for the Node.js inventory.",
    "authz.note.node_routes": (
        "Could not interpret {file} ({error}): its routes are not in the inventory."
    ),
    "authz.note.non_literal_route": "{file}:{line}: non-literal route ({route}); skipped.",
    "authz.note.non_literal_chain": "{file}:{line}: non-literal route(); skipped.",
    "authz.note.unresolved_router": (
        "Could not resolve the router {router} mounted at {scope} ({file}): its routes, if "
        "analyzed, are left without that prefix."
    ),
    "authz.note.unmounted_router": (
        "The router {name} in {file} is not mounted in any analyzed file: its routes are left "
        "without a prefix."
    ),
    "authz.note.node_controllers": (
        "Could not interpret {file} ({error}): its controllers are not in the inventory."
    ),
    "authz.limit.extractor_failed": (
        "The {name} endpoint inventory failed ({error}): reduced coverage in AUTHZ."
    ),
    "owasp.coverage.yes": "Yes",
    "owasp.coverage.partial": "Partly",
    "owasp.coverage.no": "No",
    "report.disclaimer": (
        "This analysis is static. It does not replace penetration testing or a manual review of "
        "business logic."
    ),
    "report.tool_status.ran": "ran",
    "report.tool_status.skipped": "skipped",
    "report.tool_status.error": "error",
    "report.db.none": "no database",
    "report.db.unused": "not used",
    "report.undetermined": "Undetermined",
    "report.yes": "Yes",
    "report.no": "No",
    "report.any_method": "any",
    "report.ai.verdict.likely_real": "probably real",
    "report.ai.verdict.likely_false": "probably false",
    "report.ai.verdict.uncertain": "uncertain",
    "report.ai.level.high": "high",
    "report.ai.level.medium": "medium",
    "report.ai.level.low": "low",
    "report.ai.risk_level.high": "high",
    "report.ai.risk_level.medium": "medium",
    "report.ai.risk_level.low": "low",
    "report.ai.risk_level.none": "none",
    "report.html.lang": "en",
    "report.html.title": "Security report · {project}",
    "report.html.kicker": "{tagline} · Static security analysis report",
    "report.html.date": "Date",
    "report.profile": "Profile",
    "report.run": "Run",
    "report.run_number": "no. {run}",
    "report.no_baseline": "no baseline",
    "report.files": "Files analyzed",
    "report.version": "Heimdall Guardian version",
    "report.rules_version": "Rules version",
    "report.html.rules": "rules {version}",
    "report.html.hash": "Hash of the analyzed code (SHA-256)",
    "report.verdict.title": "Delivery verdict",
    "report.verdict.criterion": "Criterion",
    "report.verdict.found": "Found",
    "report.verdict.maximum": "Maximum",
    "report.verdict.result": "Result",
    "report.verdict.exceeded": "Exceeded",
    "report.verdict.exceeded_blocking": "Exceeded · blocking",
    "report.verdict.within": "Met",
    "report.verdict.custom_thresholds": (
        "The applied thresholds differ from the institutional default values."
    ),
    "report.verdict.issuer": "Issued by: {issuer} · {date}",
    "report.verdict.signature": "Verdict fingerprint",
    "report.light.rojo": "red",
    "report.light.amarillo": "yellow",
    "report.light.verde": "green",
    "report.light.label": "Traffic light: {color}",
    "report.light.rojo.text": "Needs immediate attention: there are open critical findings.",
    "report.light.amarillo.text": "Needs a remediation plan: there are open high findings.",
    "report.light.verde.text": "No open critical or high findings.",
    "report.summary.open_total": (
        "Open findings: {count}. It does not include accepted ones or those marked as false "
        "positives."
    ),
    "report.ai.summary_heading": "Executive summary · {label}",
    "report.ai.summary_note": (
        "Written by the model {model} from aggregate figures; it did not receive code."
    ),
    "report.plan.title": "Where to start",
    "report.plan.help": "Grouped by common cause, worst first. AI suggestions are not included.",
    "report.plan.update": "Update {package} to {version}: resolves {findings} in {files}",
    "report.plan.review": "Review {package}: no fixed version is known yet ({findings})",
    "report.plan.rule": "{title}: {findings} in {files}",
    "report.plan.findings.one": "{count} finding",
    "report.plan.findings.other": "{count} findings",
    "report.plan.files.one": "{count} file",
    "report.plan.files.other": "{count} files",
    "report.plan.col.number": "#",
    "report.plan.col.action": "Action",
    "report.plan.col.findings": "Findings",
    "report.plan.col.files": "Files",
    "report.plan.col.ids": "IDs",
    "ui.plan.button": "Where to start",
    "report.risks.title": "Top risks",
    "report.risks.detail": "— {cases} in {files}",
    "report.no_open": "No open findings.",
    "report.compare.title": "Comparison with the previous run",
    "report.compare.new": "New",
    "report.compare.persistent": "Persistent",
    "report.compare.fixed": "Fixed",
    "report.compare.accepted": "Accepted risk",
    "report.compare.false_positive": "False positive",
    "report.compare.first_run": (
        "First run of the project: all findings are new. The comparison will be available on the "
        "next one."
    ),
    "report.compare.no_baseline": "Run without a baseline.",
    "report.trend.title": "Open findings trend",
    "report.trend.aria": "Open findings per run",
    "report.trend.bar": "Run {run} ({date}): {label} {count}",
    "report.coverage.title": "What Heimdall Guardian checks",
    "report.coverage.what_is": "What OWASP is",
    "report.coverage.category": "Category",
    "report.coverage.meaning": "What it means",
    "report.coverage.example": "An everyday example",
    "report.coverage.coverage": "Heimdall Guardian coverage",
    "report.coverage.open": "Open findings",
    "report.owasp_map.title": "OWASP Top 10 category map",
    "report.owasp.unclassified": "Unclassified",
    "report.endpoints.title": "Endpoint inventory",
    "report.endpoints.summary": "{total} endpoints detected; {open} without authentication.",
    "report.endpoints.method": "Method",
    "report.endpoints.route": "Route",
    "report.endpoints.handler": "Handler",
    "report.endpoints.requires_auth": "Does it require authentication?",
    "report.endpoints.has_auth": "Does it have authentication?",
    "report.endpoints.idor": "IDOR risk",
    "report.endpoints.source": "Source",
    "report.endpoints.public_by_design": "Looks public by design",
    "report.endpoints.no_write": "No · write",
    "report.endpoints.not_evaluated": "Not evaluated",
    "report.endpoints.ai": "AI",
    "report.findings.title": "Detailed findings",
    "report.findings.search": "Search by file, rule or text",
    "report.findings.search_aria": "Search",
    "report.findings.severity": "Severity",
    "report.findings.any_severity": "All severities",
    "report.findings.category": "Category",
    "report.findings.any_category": "All categories",
    "report.findings.status": "Status",
    "report.findings.any_status": "All statuses",
    "report.findings.origin": "Origin",
    "report.findings.any_origin": "All origins",
    "report.findings.of": " of ",
    "report.findings.none": "No findings were found in the code.",
    "report.finding.what": "What and why",
    "report.finding.fix": "How to fix it",
    "report.finding.classification": "Classification",
    "report.finding.origin": "Origin",
    "report.finding.rule": "rule {rule}",
    "report.finding.confidence": "confidence {level}",
    "report.finding.verify": "How to verify it",
    "report.finding.references": "References",
    "report.ai.verdict": "Verdict",
    "report.ai.confidence": "confidence {level}",
    "report.ai.risk_idor": "Risk of access to other people's records",
    "report.ai.risk_flow": "of skipping or repeating steps",
    "report.ai.suggested_fix": "Suggested fix:",
    "report.ai.reachable": "Reachable from user input",
    "report.ai.reachable.yes": "yes",
    "report.ai.reachable.no": "no",
    "report.ai.reachable.unclear": "unclear",
    "report.ai.source": "Input",
    "report.ai.risk_sink": "Risk of an attack through this operation",
    "report.ai.model_note": "Model: {model}. It does not change the finding's severity or status.",
    "report.ai.unknown_model": "unknown",
    "report.dependencies.title": "Vulnerable dependencies",
    "report.dependencies.severity": "Severity",
    "report.dependencies.package": "Package",
    "report.dependencies.vulnerability": "Vulnerability",
    "report.dependencies.fix": "Fix",
    "report.dependencies.file": "File",
    "report.dependencies.status": "Status",
    "report.dependencies.none": "No dependencies with known vulnerabilities were found.",
    "report.fixed.title": "Fixed since the previous run",
    "report.fixed.finding": "Finding",
    "report.fixed.previous_location": "Previous location",
    "report.annex.title": "Technical annex",
    "report.annex.tool": "Tool",
    "report.annex.version": "Version",
    "report.annex.status": "Status",
    "report.annex.findings": "Findings",
    "report.annex.database": "Vulnerability database",
    "report.annex.detail": "Detail",
    "report.annex.limitations": "Limitations of this run",
    "report.omitted.title": "Omitted from this analysis",
    "report.omitted.folders.one": "{count} folder",
    "report.omitted.folders.other": "{count} folders",
    "report.omitted.files.one": "{count} file",
    "report.omitted.files.other": "{count} files",
    "report.omitted.and": "{first} and {second}",
    "report.omitted.left_out": "Not analyzed: {parts}.",
    "report.omitted.more": "and {count} more",
    "report.omitted.findings.one": (
        "{count} finding from earlier analyses is in an omitted place: "
        "it keeps its status and is not counted as fixed."
    ),
    "report.omitted.findings.other": (
        "{count} findings from earlier analyses are in omitted places: "
        "they keep their status and are not counted as fixed."
    ),
    "report.omitted.type.folder": "Folder",
    "report.omitted.type.file": "File",
    "report.omitted.type": "Type",
    "report.omitted.path": "Path",
    "report.omitted.sheet": "Omitted",
    "cli.summary.omitted": "Omitted: {text}",
    "ui.facts.omitted": "Not analyzed: {parts}.",
    "report.annex.none": "None.",
    "report.annex.excluded": "Excluded paths",
    "report.annex.stack": "Detected stack",
    "report.annex.no_stack": "none",
    "report.sbom.note": (
        "Component inventory (SBOM, CycloneDX {version}): {count} components. It is delivered as a "
        "separate file."
    ),
    "report.scope": "Scope.",
    "report.risk.vulnerable_dependency": "Vulnerable dependency: {package}",
    "report.pdf.title": "Security report - {project}",
    "report.pdf.running_header": "Heimdall Guardian - {project}",
    "report.pdf.page": "Page {page} of {total}",
    "report.pdf.analyzed_project": "Analyzed project",
    "report.pdf.analysis_date": "Analysis date",
    "report.pdf.hash": "Code hash (SHA-256)",
    "report.pdf.exceeded_blocking": "Exceeded (blocking)",
    "report.pdf.custom_thresholds": (
        "The applied thresholds differ from the institutional default values; the changes are "
        "recorded in the verdict log."
    ),
    "report.pdf.accepted_intro": (
        "Findings that do not count toward the verdict because the risk was accepted or they were "
        "dismissed as false positives:"
    ),
    "report.pdf.issuer": "Issued by",
    "report.pdf.analyzed_code": "Analyzed code",
    "report.pdf.sign_here": "Name and signature of the issuer",
    "report.pdf.summary": "Summary",
    "report.pdf.by_severity": (
        "Open findings by severity. It does not include accepted ones or those dismissed as false "
        "positives."
    ),
    "report.pdf.compared": (
        "Compared with run {previous}: {new} new, {persistent} persistent, {fixed} fixed, "
        "{accepted} with accepted risk and {false_positive} dismissed as false positives."
    ),
    "report.pdf.ai_summary_intro": (
        "Summary written by AI (needs human validation; it was written using only aggregate "
        "figures):"
    ),
    "report.pdf.example": "Everyday example",
    "report.pdf.coverage": "Coverage",
    "report.pdf.open": "Open",
    "report.pdf.code_findings": "Findings in the code ({count})",
    "report.pdf.ai_suggestion": " - AI suggestion",
    "report.pdf.truncated": (
        "The first {max} are shown; the rest is in the HTML report or the Excel file."
    ),
    "report.pdf.dependencies": "Vulnerable dependencies ({count})",
    "report.pdf.fixed_version": "Fixed version",
    "report.pdf.no_patch": "no patch",
    "report.pdf.endpoints": "Endpoints without authentication ({open} of {total})",
    "report.pdf.methods": "Methods",
    "report.pdf.write": "Write",
    "report.pdf.all_authenticated": "All the detected endpoints require authentication.",
    "report.pdf.fixed": "Fixed since the previous run ({count})",
    "report.xlsx.id": "ID",
    "report.xlsx.severity": "Severity",
    "report.xlsx.baseline_status": "Baseline status",
    "report.xlsx.category": "Category",
    "report.xlsx.title": "Title",
    "report.xlsx.file": "File",
    "report.xlsx.line": "Line",
    "report.xlsx.description": "Description",
    "report.xlsx.recommendation": "Recommendation",
    "report.xlsx.rule": "Rule",
    "report.xlsx.cwe": "CWE",
    "report.xlsx.owasp": "OWASP",
    "report.xlsx.origin": "Origin",
    "report.xlsx.detected_by": "Detected by",
    "report.xlsx.owner": "Owner",
    "report.xlsx.due_date": "Due date",
    "report.xlsx.handling_status": "Handling status",
    "report.xlsx.notes": "Notes",
    "report.xlsx.sheet.findings": "Findings",
    "report.xlsx.sheet.summary": "Summary",
    "report.xlsx.sheet.owasp": "OWASP Top 10",
    "report.xlsx.sheet.endpoints": "Endpoints",
    "report.xlsx.owasp.category": "Category",
    "report.xlsx.owasp.name": "Name",
    "report.xlsx.owasp.covers": "What it covers",
    "report.xlsx.summary.project": "Project",
    "report.xlsx.summary.hash": "Hash of the analyzed code",
    "report.xlsx.summary.by_severity": "Open findings by severity",
    "report.xlsx.summary.by_status": "Findings by status",
    "report.xlsx.summary.limitations": "Run limitations",
    "report.xlsx.endpoints.requires_auth": "Requires authentication",
    "report.xlsx.endpoints.has_auth": "Has authentication",
    "report.xlsx.endpoints.evidence": "Evidence",
    "report.error.no_sbom": (
        "This run did not generate an SBOM: use the vendor profile or the SBOM module."
    ),
    "report.error.unsupported_format": "Unsupported format: {name}. Extensions: {valid}.",
    "report.risks.cases.one": "{count} case",
    "report.risks.cases.other": "{count} cases",
    "report.risks.files.one": "{count} file",
    "report.risks.files.other": "{count} files",
    "core.limit.large_code.one": (
        "{count} text file weighs more than {limit} KB ({examples}). It was analyzed, but check "
        "whether it is generated or minified code: it is easy to hide something there."
    ),
    "core.limit.large_code.other": (
        "{count} text files weigh more than {limit} KB ({examples}). They were analyzed, but check "
        "whether they are generated or minified code: it is easy to hide something there."
    ),
    "core.limit.oversized.one": (
        "{count} binary file larger than {limit} KB was not analyzed because it contains no code "
        "({examples})."
    ),
    "core.limit.oversized.other": (
        "{count} binary files larger than {limit} KB were not analyzed because they contain no "
        "code ({examples})."
    ),
    "core.limit.symlinks.one": "{count} symbolic link was ignored.",
    "core.limit.symlinks.other": "{count} symbolic links were ignored.",
    "core.limit.pattern_skipped.one": (
        "{count} file was left out by the file patterns ({patterns}), {examples}. "
        "Manifests and lockfiles are always analyzed, and secrets are searched in every file."
    ),
    "core.limit.pattern_skipped.other": (
        "{count} files were left out by the file patterns ({patterns}), {examples}. "
        "Manifests and lockfiles are always analyzed, and secrets are searched in every file."
    ),
    "core.limit.dropped.one": (
        "{count} finding from the tools was left out because it is in a skipped folder "
        '({examples}). If it matters, remove that folder from "Folders to skip".'
    ),
    "core.limit.dropped.other": (
        "{count} findings from the tools were left out because they are in skipped folders "
        '({examples}). If any of them matter, remove the folder from "Folders to skip".'
    ),
    "core.limit.direct_only.one": (
        "{count} manifest lists only direct dependencies, with no lockfile next to it "
        "({examples}): its transitive dependencies were not checked. Generate a lockfile "
        "(npm install --package-lock-only, composer update --lock, pip-compile or uv lock, ...) "
        "in your own environment and analyze again."
    ),
    "core.limit.direct_only.other": (
        "{count} manifests list only direct dependencies, with no lockfile next to them "
        "({examples}): their transitive dependencies were not checked. Generate lockfiles "
        "(npm install --package-lock-only, composer update --lock, pip-compile or uv lock, ...) "
        "in your own environment and analyze again."
    ),
    "core.limit.vendored_found.one": (
        "{count} library copied into the project was recognized by its version header "
        "({examples}). It is checked against the vulnerability database and its code is left "
        "out of the code rules."
    ),
    "core.limit.vendored_found.other": (
        "{count} libraries copied into the project were recognized by their version header "
        "({examples}). They are checked against the vulnerability database and their code is "
        "left out of the code rules."
    ),
    "core.limit.vendored_sast.one": (
        "{count} code-rule finding inside a copied library was left out ({examples}): it is "
        "third-party code. Its known vulnerabilities are reported by version instead."
    ),
    "core.limit.vendored_sast.other": (
        "{count} code-rule findings inside copied libraries were left out ({examples}): they are "
        "third-party code. Their known vulnerabilities are reported by version instead."
    ),
    "core.limit.untracked_versioned.one": (
        "{count} finding on a file that git does not track was left out ({examples}): the "
        "rule only applies to versioned files. If the file is shared by other means, "
        "remove its secrets as well."
    ),
    "core.limit.untracked_versioned.other": (
        "{count} findings on files that git does not track were left out ({examples}): the "
        "rule only applies to versioned files. If the files are shared by other means, "
        "remove their secrets as well."
    ),
    "adapter.opengrep.partial.one": "Opengrep could not fully analyze {count} file or rule.",
    "adapter.opengrep.partial.other": "Opengrep could not fully analyze {count} files or rules.",
    "llm.limit.triage_budget.one": "AI: {count} finding was not triaged because of the run budget.",
    "llm.limit.triage_budget.other": (
        "AI: {count} findings were not triaged because of the run budget."
    ),
    "llm.limit.sink_budget.one": "AI: {count} risk point was not reviewed because of the budget.",
    "llm.limit.sink_budget.other": (
        "AI: {count} risk points were not reviewed because of the budget."
    ),
    "llm.limit.endpoint_budget.one": "AI: {count} endpoint was not reviewed because of the budget.",
    "llm.limit.endpoint_budget.other": (
        "AI: {count} endpoints were not reviewed because of the budget."
    ),
    "authz.limit.undetermined.one": (
        "{count} endpoint with undetermined protection: review the inventory."
    ),
    "authz.limit.undetermined.other": (
        "{count} endpoints with undetermined protection: review the inventory."
    ),
    "report.verdict.accepted.one": (
        "{count} finding does not count because the risk was accepted or it was dismissed: {ids}."
    ),
    "report.verdict.accepted.other": (
        "{count} findings do not count because the risk was accepted or they were dismissed: {ids}."
    ),
    "report.pdf.mediums.one": (
        "There is also {count} open medium-severity finding, accepted on the commitment to fix it."
    ),
    "report.pdf.mediums.other": (
        "There are also {count} open medium-severity findings, accepted on the commitment to fix "
        "them."
    ),
    "owasp.what_is": (
        "OWASP is a non-profit foundation dedicated to improving software security. Using data "
        'from thousands of real applications, it publishes the most common risks. Its "Top 10" '
        "list is the most widely used reference for talking about application security; the latest "
        "edition is the 2025 one."
    ),
    "owasp.scope_warning": (
        "Covering Top 10 categories does not mean other risks do not exist. Heimdall Guardian "
        "reads the code without running it: it does not replace a human review or penetration "
        "testing."
    ),
    "owasp.A01.name": "Broken Access Control",
    "owasp.A01.explanation": (
        "Someone can see or do something they are not allowed to. It also includes the system "
        "making requests to addresses chosen by an attacker."
    ),
    "owasp.A01.example": (
        "Someone changes a number in the web address and sees another person's data."
    ),
    "owasp.A01.coverage_note": (
        "Inventory of endpoints without authentication, rules for access to other people's "
        "objects, file paths, redirects and requests to user-chosen addresses. The AI endpoint "
        "review only suggests."
    ),
    "owasp.A02.name": "Security Misconfiguration",
    "owasp.A02.explanation": (
        "The system is left with factory or development settings that expose it."
    ),
    "owasp.A02.example": (
        "A production application is still in test mode and shows its internal errors."
    ),
    "owasp.A02.coverage_note": (
        "Configuration rules (debug mode, CORS, cookies, visible errors) and a review of "
        "configuration files and infrastructure as code."
    ),
    "owasp.A03.name": "Software Supply Chain Failures",
    "owasp.A03.explanation": (
        "Third-party components with known flaws are used, or the way the software is built and "
        "delivered is compromised."
    ),
    "owasp.A03.example": (
        "The application uses a library with a public flaw that already has a fix."
    ),
    "owasp.A03.coverage_note": (
        "Dependencies with known vulnerabilities and a component inventory (SBOM). It does not "
        "check the integrity of the build or publishing process."
    ),
    "owasp.A04.name": "Cryptographic Failures",
    "owasp.A04.explanation": (
        "Sensitive data is poorly protected or not protected at all: weak encryption, visible keys "
        "or carelessly stored passwords."
    ),
    "owasp.A04.example": (
        "Users' passwords are stored with a method that can be cracked in minutes."
    ),
    "owasp.A04.coverage_note": (
        "Weak cryptography, predictable randomness and secrets written in the code. It does not "
        "check encryption in transit or at rest in the infrastructure."
    ),
    "owasp.A05.name": "Injection",
    "owasp.A05.explanation": (
        "Data typed by the user is interpreted as an instruction and the system runs it. It "
        "includes SQL, command and in-page code (XSS) injection."
    ),
    "owasp.A05.example": (
        "Someone types an instruction in a search field and gets the whole database."
    ),
    "owasp.A05.coverage_note": (
        "Rules for SQL, NoSQL, command, code and in-page script (XSS) injection for the supported "
        "languages."
    ),
    "owasp.A06.name": "Insecure Design",
    "owasp.A06.explanation": (
        "The problem is not a programming mistake but how the system was conceived: controls are "
        "missing from the design."
    ),
    "owasp.A06.example": (
        "A process lets a discount coupon be reused without limit because nobody foresaw the abuse."
    ),
    "owasp.A06.coverage_note": (
        "Only AI suggestions about business flows and a few design rules (file upload, mass "
        "assignment). Design needs a human review."
    ),
    "owasp.A07.name": "Authentication Failures",
    "owasp.A07.explanation": (
        "The system does not properly check who each person is, or lets someone pretend to be "
        "another person."
    ),
    "owasp.A07.example": "An access key was left in the code and anyone with the file can get in.",
    "owasp.A07.coverage_note": (
        "Exposed secrets, poorly verified JWT tokens, and insecure sessions and cookies. It does "
        "not test weak passwords or two-factor authentication."
    ),
    "owasp.A08.name": "Software or Data Integrity Failures",
    "owasp.A08.explanation": (
        "The system trusts code or data that nobody verified and that could have been tampered "
        "with."
    ),
    "owasp.A08.example": (
        "The application rebuilds objects from received data and an attacker manipulates them."
    ),
    "owasp.A08.coverage_note": (
        "Insecure deserialization of external data. It does not check update signatures or "
        "delivery channels."
    ),
    "owasp.A09.name": "Security Logging and Alerting Failures",
    "owasp.A09.explanation": (
        "Important events are not recorded, or nobody finds out about an attack in time."
    ),
    "owasp.A09.example": (
        "Someone tries thousands of passwords for a week and nobody gets a warning."
    ),
    "owasp.A09.coverage_note": (
        "A code analysis cannot know whether monitoring and alerts are in place in production."
    ),
    "owasp.A10.name": "Mishandling of Exceptional Conditions",
    "owasp.A10.explanation": (
        "The system reacts badly to errors or unexpected situations: it crashes, opens up or "
        "reveals information."
    ),
    "owasp.A10.example": (
        "On an error, the system lets the operation through instead of blocking it."
    ),
    "owasp.A10.coverage_note": (
        "Heimdall Guardian has no rules for this category: a code analysis cannot see how the "
        "system reacts to failures in production."
    ),
    "owasp.hint.CWE-16": (
        "Open the production environment's configuration file and compare the value with the "
        "recommended one: debug mode off, restricted origins and no test values."
    ),
    "owasp.hint.CWE-20": (
        "Follow the data from where it enters to where it is used and confirm that its type, "
        "length and format are validated before use."
    ),
    "owasp.hint.CWE-22": (
        "Follow the parameter to the function that opens the file and confirm that the path is "
        "normalized and limited to a base directory. Try `../` in a test environment."
    ),
    "owasp.hint.CWE-78": (
        "Check whether the command text is built from user data. Use an argument list with no "
        "shell and with allowed values."
    ),
    "owasp.hint.CWE-79": (
        "Find where the data is printed on the page and confirm that it is escaped for its context "
        "(HTML, attribute or script). In testing, try a text like `<b>x</b>`."
    ),
    "owasp.hint.CWE-89": (
        "Check whether the query is built by joining text with user data. It should use bound "
        "parameters; confirm that no data reaches the query as text."
    ),
    "owasp.hint.CWE-94": (
        "Look for any external data reaching a function that runs code. Replace it with a closed "
        "list of allowed operations."
    ),
    "owasp.hint.CWE-95": (
        "Look for any external data reaching `eval` or an equivalent. Replace it with a closed "
        "list of operations or a safe parser for the data."
    ),
    "owasp.hint.CWE-98": (
        "Check whether the path of the included file depends on external data. It should be chosen "
        "from a fixed list, never built from the input."
    ),
    "owasp.hint.CWE-209": (
        "Cause an error in a test environment and check whether the response shows paths, queries "
        "or traces. Production should only show a generic message."
    ),
    "owasp.hint.CWE-259": (
        "Find the password written in the code and confirm whether it is still valid. If it is, "
        "change it and move it to a secrets manager."
    ),
    "owasp.hint.CWE-285": (
        "Confirm that the action checks the requester's permission, not just that they signed in. "
        "Test with an account that lacks that permission."
    ),
    "owasp.hint.CWE-295": (
        "Check whether certificate validation is turned off. The chain of trust and the server "
        "name should always be validated."
    ),
    "owasp.hint.CWE-306": (
        "Check the route and its decorators, middleware or global filters. Send the request "
        "without credentials in a test environment: it should answer 401 or 403."
    ),
    "owasp.hint.CWE-311": (
        "Confirm with the infrastructure team whether the data travels or is stored unencrypted "
        "and which encryption mechanism is used."
    ),
    "owasp.hint.CWE-319": (
        "Check the server and client configuration: communication should use TLS. Confirm that "
        "there are no `http://` addresses to services that handle data."
    ),
    "owasp.hint.CWE-312": (
        "Check where the data is stored: on the device, SharedPreferences and GetStorage are "
        "readable files. Sensitive data should go in the keychain (flutter_secure_storage)."
    ),
    "owasp.hint.CWE-326": (
        "Check the key size or length in use and compare it with the algorithm's current guidance "
        "(for example, AES with 128 bits or more and RSA with 2048 or more)."
    ),
    "owasp.hint.CWE-327": (
        "Identify what the algorithm is used for. If it protects passwords or data, replace it "
        "with a current one (Argon2, bcrypt or scrypt; AES-GCM). MD5 or SHA-1 are only fine for "
        "checksums with no security value."
    ),
    "owasp.hint.CWE-330": (
        "Confirm whether the random value protects anything (token, temporary password). If it "
        "does, it should come from a cryptographic generator, not a general-purpose one."
    ),
    "owasp.hint.CWE-345": (
        "Check whether the data is accepted without verifying its origin or integrity. A signature "
        "or an authentication code should be verified before using it."
    ),
    "owasp.hint.CWE-347": (
        "Check how the token is decoded: the signature should be verified with the right key and a "
        "fixed algorithm, never the one the token itself indicates."
    ),
    "owasp.hint.CWE-352": (
        "Check whether the action changes data and whether it requires an anti-CSRF token or a "
        "SameSite cookie. In testing, send the request from another site."
    ),
    "owasp.hint.CWE-377": (
        "Check how temporary files are created: they should use functions that generate "
        "unpredictable names and restricted permissions."
    ),
    "owasp.hint.CWE-400": (
        "Check whether there are limits on size, time or number of requests for the flagged "
        "operation, and test with a large input in testing."
    ),
    "owasp.hint.CWE-434": (
        "Check the validation of the uploaded file: real type, allowed extension, maximum size, "
        "regenerated name and a folder outside the one the web server serves."
    ),
    "owasp.hint.CWE-477": (
        "Find the obsolete component in the code and in the dependencies. Confirm in the vendor's "
        "documentation which one replaces it and which version no longer receives fixes."
    ),
    "owasp.hint.CWE-489": (
        "Confirm in the production environment that debug mode is off and that no development "
        "console is reachable."
    ),
    "owasp.hint.CWE-502": (
        "Identify where the deserialized data comes from. If it is not fully trusted, use a simple "
        "data format (JSON) with schema validation."
    ),
    "owasp.hint.CWE-601": (
        "Check whether the redirect destination comes from request data. It should be compared "
        "with a list of allowed destinations or limited to internal paths."
    ),
    "owasp.hint.CWE-605": (
        "Check whether the service listens on all interfaces and whether that is needed; limit the "
        "listening address to the one required."
    ),
    "owasp.hint.CWE-611": (
        "Check the XML parser: external entities and document type definitions should be turned "
        "off."
    ),
    "owasp.hint.CWE-614": (
        "Check the session cookie's attributes: it should carry `Secure` and `HttpOnly`. Confirm "
        "it in the browser's developer tools."
    ),
    "owasp.hint.CWE-639": (
        "Test with two different accounts in a test environment: account A asks for the identifier "
        "of one of B's records and should get 403 or 404."
    ),
    "owasp.hint.CWE-703": (
        "Check what happens when the operation fails: the error should not be silently ignored or "
        "leave the system in a state that allows access."
    ),
    "owasp.hint.CWE-732": (
        "Check the file or resource permissions: only whoever needs to should be able to read or "
        "write it."
    ),
    "owasp.hint.CWE-532": (
        "Check which values reach print, debugPrint or the logger. Tokens, passwords and card data "
        "should not appear; run the app and read the log with `adb logcat`."
    ),
    "owasp.hint.CWE-749": (
        "Check which app functions the WebView page can call. They should be the minimum, with the "
        "page limited to your domain over https and every message validated."
    ),
    "owasp.hint.CWE-798": (
        "Look for the value in the version history and confirm whether it is still valid. If it "
        "is, rotate it right away and move it to a secrets manager."
    ),
    "owasp.hint.CWE-841": (
        "Walk through the business flow step by step in testing and verify that each step checks "
        "the state of the previous one; try skipping or repeating steps."
    ),
    "owasp.hint.CWE-915": (
        "Check which fields the model accepts from the request. There should be an explicit list "
        "of allowed fields; confirm that, for example, a role cannot be sent."
    ),
    "owasp.hint.CWE-916": (
        "Check how passwords are stored: they should use a slow algorithm with a salt (Argon2, "
        "bcrypt or scrypt), never MD5, SHA-1 or plain SHA-256."
    ),
    "owasp.hint.CWE-918": (
        "Check whether the address the server fetches comes from the request. It should be "
        "validated against a list of allowed destinations, blocking internal addresses."
    ),
    "owasp.hint.CWE-926": (
        'Open AndroidManifest.xml and check each component with android:exported="true": does it '
        "need to receive calls from other apps? If not, set it to false; if it does, require a "
        "signature permission and test with `adb shell am start` that it rejects invalid data."
    ),
    "owasp.hint.CWE-927": (
        "Look for PendingIntents and confirm they carry FLAG_IMMUTABLE and an explicit Intent. For "
        "broadcasts, confirm that what is sent is not sensitive or that only your app receives it "
        "(setPackage or a signature permission)."
    ),
    "owasp.hint.CWE-942": (
        "Check the CORS configuration: origins should be a specific list; an open origin with "
        "credentials lets other sites read session data."
    ),
    "owasp.hint.CWE-943": (
        "Check whether the query filter is built from objects sent by the user. Validate that each "
        "value is of the expected type (text, number) before using it."
    ),
    "owasp.hint.CWE-80": (
        "Find where the data is printed on the page and confirm that HTML special characters "
        "are escaped. In testing, try a text like `<b>x</b>`."
    ),
    "owasp.hint.CWE-155": (
        "Check whether user data reaches a pattern or wildcard (glob, shell expansion) and "
        "confirm that wildcard characters are escaped or rejected."
    ),
    "owasp.hint.CWE-284": (
        "Check who can reach the resource and confirm that the access check runs on the server "
        "for every request, not only in the interface."
    ),
    "owasp.hint.CWE-494": (
        "Check what is downloaded and how it is verified. The code or file should be checked "
        "against a pinned checksum or signature before it is used."
    ),
    "owasp.hint.CWE-838": (
        "Check where the data is written (HTML, URL, script, query) and confirm that it is "
        "encoded for that context before it is printed."
    ),
    "owasp.hint.CWE-1004": (
        "Check the session cookie's attributes: it should carry `HttpOnly` so that scripts on the "
        "page cannot read it."
    ),
    "adapter.opengrep.default_recommendation": "Review and fix the flagged code.",
    "adapter.bandit.recommendation": (
        "Review the flagged use and apply the safe alternative described in the reference."
    ),
    "adapter.gitleaks.title_code": "Secret in the code: {rule}",
    "adapter.gitleaks.title_history": "Secret in the git history: {rule}",
    "adapter.gitleaks.description_code": "Secret embedded in the current code.{detector}",
    "adapter.gitleaks.description_history": (
        "Secret present in the git history (commit {commit}, {date}). Deleting it from the code"
        " does not remove it from the repository.{detector}"
    ),
    "adapter.gitleaks.detector": " Detector: {detail}.",
    "adapter.gitleaks.rec_code": (
        "Revoke and rotate the credential immediately. Remove it from the code and load it from"
        " environment variables or a secrets manager."
    ),
    "adapter.gitleaks.rec_history": (
        "Revoke and rotate the credential even if it is no longer in the code: it can still be"
        " recovered from the git history."
    ),
    "adapter.dependency.title": "{package} {installed} has a known vulnerability ({id})",
    "adapter.dependency.description": "Dependency with a known vulnerability. {summary}",
    "adapter.dependency.rec_no_fix": (
        "No fixed version has been published yet: evaluate mitigations or replace the dependency."
    ),
    "adapter.osv.rec_fixed": "Update {package} to a fixed version: {versions}.",
    "adapter.vendored.rec_fixed": (
        "Replace the copied file of {package} with version {versions} or later, or load it "
        "through a package manager so it stays audited."
    ),
    "adapter.vendored.rec_no_fix": (
        "No fixed version of {package} has been published yet: evaluate mitigations or replace "
        "the copied library."
    ),
    "adapter.trivy.rec_fixed": "Update {package} to version {version} or later.",
    "adapter.trivy.default_resolution": "Fix the flagged configuration.",
    "authz.kind.write": "write",
    "authz.kind.read": "read",
    "authz.route": "{methods} {path}",
    "authz.finding.title": "{kind} endpoint without authentication: {route}",
    "authz.finding.description": (
        "The {kind} endpoint {path} (methods: {methods}), served by {handler}, does not require"
        " authentication: {evidence}.{declared}{note}"
    ),
    "authz.finding.declared_in": " The route is declared in {file}.",
    "authz.finding.note_public": " By its name it could be public by design; confirm it.",
    "authz.finding.note_any_method": " It declares no methods, so it accepts any.",
    "authz.finding.recommendation": (
        "Require authentication on the endpoint (decorator, mixin, attribute or middleware,"
        " depending on the framework) and also validate the permission on the resource. If it"
        " must be public, accept the finding with a justification."
    ),
    "authz.ev.login_middleware": "LoginRequiredMiddleware in settings",
    "authz.ev.drf_default_open": "no permission_classes and no restrictive default permission",
    "authz.ev.drf_default_settings": "DEFAULT_PERMISSION_CLASSES in settings",
    "authz.ev.django_no_decorator": "no authentication decorator",
    "authz.ev.django_no_mixin": "no authentication mixin",
    "authz.ev.django_admin": "Django admin site",
    "authz.ev.django_generic_no_mixin": "Django generic view without a mixin",
    "authz.ev.view_not_found": "the view could not be located",
    "authz.ev.url_wrapper": "{wrappers}(...) in {file}",
    "authz.ev.net_anonymous_action": "[AllowAnonymous] on the action",
    "authz.ev.net_authorize_action": "[Authorize] on the action",
    "authz.ev.net_anonymous_controller": "[AllowAnonymous] on the controller",
    "authz.ev.net_authorize_controller": "[Authorize] on the controller",
    "authz.ev.net_global_policy": "global authorization policy",
    "authz.ev.net_none": "no [Authorize] and no global policy",
    "authz.ev.net_anonymous_route": "AllowAnonymous on the route",
    "authz.ev.net_require_route": "RequireAuthorization on the route",
    "authz.ev.net_route_none": "no RequireAuthorization and no global policy",
    "authz.ev.laravel_constructor": "authentication middleware in the controller constructor",
    "authz.ev.laravel_outside": "outside a group or chain with authentication middleware",
    "authz.ev.php_session": "checks the session in the file itself",
    "authz.ev.php_basic_auth": "checks HTTP basic authentication credentials in the file itself",
    "authz.ev.php_includes": "includes {file}",
    "authz.ev.php_none": "no session check and no include of an access file",
    "authz.ev.php_script": (
        "runs code when loaded (looks like a scheduled or maintenance script) "
        "with no session check and no command-line-only guard"
    ),
    "authz.ev.guard_empty": "<empty>",
    "authz.ev.guard_inline": "<anonymous middleware that checks session or token>",
    "authz.ev.guard_handler": "check inside the handler",
    "authz.ev.guard_item": "{text} ({origin})",
    "authz.ev.guard_auth": "authentication {noun}: {items}",
    "authz.ev.guard_unknown": "unidentified {noun} that might authenticate: {items}",
    "authz.ev.origin_route": "on the route",
    "authz.ev.origin_global_guard": "global guard",
    "authz.ev.origin_use_guards": "@UseGuards on {where}",
    "authz.ev.where_method": "the method",
    "authz.ev.where_class": "the class",
    "authz.ev.express_none": (
        "no authentication middleware on the route or in earlier {router}.use() calls"
    ),
    "authz.ev.nest_public": "{decorator} on {where}: public by decorator",
    "authz.ev.nest_public_guarded": (
        "{decorator} on {where}, but explicit guards also exist: review"
    ),
    "authz.ev.nest_none": "no authentication @UseGuards and no global guard",
    "core.ai_stats.profile": "Analysis profile",
    "core.ai_stats.files": "Files analyzed",
    "core.ai_stats.stacks": "Technologies detected",
    "core.ai_stats.none": "none",
    "core.ai_stats.open_total": "Open findings in total",
    "core.ai_stats.by_severity": "Findings of severity {name}",
    "core.ai_stats.by_category": "Findings of category {name}",
    "core.ai_stats.endpoints": "Endpoints detected",
    "core.ai_stats.endpoints_open": "Endpoints without authentication",
    "core.ai_stats.ai_new": "Possible problems found by the AI beyond the rules",
    "core.ai_stats.frequent": "Most frequent finding types",
    "cli.rules.help": "checks your own rule files (extra folders in config.toml or --dir)",
    "cli.rules.check": "validates the rule files and reports problems (the default action)",
    "cli.rules.dir": "folder with rule files; repeat it for several (default: the configured ones)",
    "cli.rules.none": (
        "No extra rule folders are configured. Add [rules] extra_dirs to config.toml or use --dir."
    ),
    "cli.rules.ok": "OK     ",
    "cli.rules.invalid": "INVALID",
    "cli.rules.no_engine": "The rule engine could not validate the syntax: {error}",
    "core.limit.user_rule_problem": "Your own rules were skipped. {file}: {detail}",
    "adapter.opengrep.user_rule_invalid": (
        "Your rule file {file} was skipped because the engine rejected it: {detail}"
    ),
    "core.user_rules.missing_dir": "The rules folder {dir} does not exist.",
    "core.user_rules.inside_project": (
        "The rules folder {dir} is inside the analyzed project, so it was ignored: the "
        "analyzed code cannot configure the analysis."
    ),
    "core.user_rules.too_many_files": (
        "The rules folder {dir} has more than {limit} files; only the first {limit} were read."
    ),
    "core.user_rules.file_too_big": "The file is larger than {limit_kb} KB.",
    "core.user_rules.unreadable": "The file cannot be read: {error}",
    "core.user_rules.bad_yaml": "The file is not valid YAML: {error}",
    "core.user_rules.no_rules": "The file must be a mapping with a non-empty `rules` list.",
    "core.user_rules.rule_not_mapping": "Rule {rule}: each rule must be a mapping.",
    "core.user_rules.missing_field": "Rule {rule}: `{field}` is missing or empty.",
    "core.user_rules.bad_id": (
        "Rule {rule}: the ID must look like PREFIX-TAG-001 (capital letters, three digits)."
    ),
    "core.user_rules.reserved_id": (
        "Rule {rule}: the AI- prefix and the CAND tag are reserved for Heimdall Guardian."
    ),
    "core.user_rules.builtin_id": "Rule {rule}: the ID is already used by a built-in rule.",
    "core.user_rules.duplicate_id": "Rule {rule}: the ID is defined more than once in your rules.",
    "core.user_rules.no_matcher": (
        "Rule {rule}: it needs `pattern`, `patterns`, `pattern-either`, `pattern-regex`, or "
        "taint mode with `pattern-sources` and `pattern-sinks`."
    ),
    "core.user_rules.bad_cwe": "Rule {rule}: `metadata.cwe` must look like CWE-89, not {value}.",
    "core.user_rules.owasp_2021": (
        "Rule {rule}: {value} is an OWASP 2021 label; use the 2025 one: {suggestion}."
    ),
    "core.user_rules.bad_owasp": (
        "Rule {rule}: {value} is not an OWASP Top 10:2025 label (for example A05:2025 Injection)."
    ),
    "core.user_rules.bad_value": "Rule {rule}: `{field}` is {value}; use one of: {expected}.",
}
