from __future__ import annotations

import argparse
from argparse import SUPPRESS
from pathlib import Path
import sys

from .ai_recommendations import generate_ai_recommendations, write_ai_recommendations_markdown
from .ai_summary import DEFAULT_OLLAMA_MODEL, DEFAULT_OLLAMA_URL, generate_ai_summary, write_ai_summary_markdown
from .config import load_custom_rules
from .dependency import load_cbom_file, write_cbom_file
from .html_reporting import write_html_report
from .reporting import (
    render_console_report,
    write_change_targets_csv,
    write_dba_planning_sql,
    write_file_reports_csv,
    write_json_file_reports,
    write_json_report,
    write_json_summary,
)
from .scanner import scan_directory
from .swagger_drafts import DEFAULT_SWAGGER_DRAFT_DIR, generate_swagger_drafts

SUPPORTED_SCAN_DOMAINS = {"pii", "pqc"}
SUPPORTED_LLM_PROVIDERS = {"ollama"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan source code for likely PII references and PQC readiness impact."
    )
    parser.add_argument("path", nargs="?", help="Root directory to scan. Optional when using --swagger-only.")
    parser.add_argument(
        "--scan",
        default="pii",
        help="Comma-separated scan domains: pii, pqc, or pii,pqc. Default: pii.",
    )
    parser.add_argument("--json-out", dest="json_out", help="Optional path to write a JSON report")
    parser.add_argument(
        "--csv-out",
        dest="csv_out",
        help="Optional path to write an Excel-friendly CSV of likely change targets.",
    )
    parser.add_argument(
        "--json-summary-out",
        dest="json_summary_out",
        help="Optional path to write a summary-only JSON report.",
    )
    parser.add_argument(
        "--json-file-reports-out",
        dest="json_file_reports_out",
        help="Optional path to write only the file_reports array as JSON.",
    )
    parser.add_argument(
        "--csv-file-reports-out",
        dest="csv_file_reports_out",
        help="Optional path to write a flattened CSV of all file-level reports.",
    )
    parser.add_argument(
        "--sql-out",
        dest="sql_out",
        help="Optional path to write DBA planning SQL for jdbc_candidate tables.",
    )
    parser.add_argument(
        "--html-out",
        dest="html_out",
        help="Optional path to write an HTML executive report.",
    )
    parser.add_argument(
        "--cbom-out",
        dest="cbom_out",
        help="Optional path to write an observed CBOM-style JSON export.",
    )
    parser.add_argument(
        "--cbom-in",
        dest="cbom_in",
        help="Optional path to import an existing CBOM-style JSON file for enrichment.",
    )
    parser.add_argument(
        "--swagger-in",
        dest="swagger_in",
        help="Optional path to a raw Swagger JSON file used to generate review-first draft config artifacts.",
    )
    parser.add_argument(
        "--swagger-draft-out-dir",
        dest="swagger_draft_out_dir",
        help="Optional directory for generated Swagger draft files. Default: config/pqc/examples/customwrapper-example/swagger-drafts.",
    )
    parser.add_argument(
        "--swagger-only",
        action="store_true",
        help="Generate Swagger draft files only and skip the code scan.",
    )
    parser.add_argument(
        "--ai-summary",
        action="store_true",
        help=SUPPRESS,
    )
    parser.add_argument(
        "--ai-summary-out",
        dest="ai_summary_out",
        help=SUPPRESS,
    )
    parser.add_argument(
        "--ai-recommendations",
        action="store_true",
        help=SUPPRESS,
    )
    parser.add_argument(
        "--ai-recommendations-out",
        dest="ai_recommendations_out",
        help=SUPPRESS,
    )
    parser.add_argument(
        "--llm-provider",
        default="ollama",
        help=SUPPRESS,
    )
    parser.add_argument(
        "--llm-model",
        default=DEFAULT_OLLAMA_MODEL,
        help=SUPPRESS,
    )
    parser.add_argument(
        "--ollama-url",
        default=DEFAULT_OLLAMA_URL,
        help=SUPPRESS,
    )
    parser.add_argument(
        "--llm-timeout-seconds",
        type=int,
        default=60,
        help=SUPPRESS,
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory name to exclude. Can be supplied multiple times.",
    )
    parser.add_argument(
        "--custom-patterns",
        dest="custom_patterns",
        help="Optional JSON file containing customer-defined search patterns.",
    )
    parser.add_argument(
        "--custom-patterns-override-defaults",
        action="store_true",
        help="When a custom pattern matches, suppress the built-in keyword category for that same identifier.",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output during scanning.")
    parser.add_argument(
        "--show-hint-breakdown",
        action="store_true",
        help="Show per-file matched hint terms and counts used for classification.",
    )
    parser.add_argument(
        "--include-file-reports",
        action="store_true",
        help="Include detailed file-by-file findings in JSON output. Console output stays summary-first by default.",
    )
    parser.add_argument(
        "--console-include-file-reports",
        action="store_true",
        help="Include detailed file-by-file findings in console output. Default console output shows only the executive summary.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root_path = Path(args.path).resolve() if args.path else None
    swagger_input_path = Path(args.swagger_in).resolve() if args.swagger_in else None
    swagger_draft_out_dir = Path(args.swagger_draft_out_dir).resolve() if args.swagger_draft_out_dir else DEFAULT_SWAGGER_DRAFT_DIR.resolve()

    if args.swagger_only:
        if not swagger_input_path:
            parser.error("--swagger-only requires --swagger-in.")
        swagger_draft_outputs = generate_swagger_drafts(swagger_input_path, swagger_draft_out_dir)
        print("Swagger draft files generated:")
        for draft_path in swagger_draft_outputs:
            print(f"  - {draft_path}")
        return 0

    if root_path is None:
        parser.error("path is required unless --swagger-only is used.")
    if not root_path.exists() or not root_path.is_dir():
        parser.error(f"Path does not exist or is not a directory: {root_path}")

    scan_domains = _parse_scan_domains(args.scan, parser)
    json_output_path = Path(args.json_out).resolve() if args.json_out else None
    csv_output_path = Path(args.csv_out).resolve() if args.csv_out else None
    json_summary_output_path = Path(args.json_summary_out).resolve() if args.json_summary_out else None
    json_file_reports_output_path = Path(args.json_file_reports_out).resolve() if args.json_file_reports_out else None
    csv_file_reports_output_path = Path(args.csv_file_reports_out).resolve() if args.csv_file_reports_out else None
    sql_output_path = Path(args.sql_out).resolve() if args.sql_out else None
    html_output_path = Path(args.html_out).resolve() if args.html_out else None
    cbom_output_path = Path(args.cbom_out).resolve() if args.cbom_out else None
    cbom_input_path = Path(args.cbom_in).resolve() if args.cbom_in else None
    ai_summary_output_path = Path(args.ai_summary_out).resolve() if args.ai_summary_out else None
    ai_recommendations_output_path = Path(args.ai_recommendations_out).resolve() if args.ai_recommendations_out else None

    custom_rules, custom_regex_rules = load_custom_rules(Path(args.custom_patterns).resolve()) if args.custom_patterns else ([], [])
    imported_cbom_components = load_cbom_file(cbom_input_path) if cbom_input_path else []
    swagger_draft_outputs = generate_swagger_drafts(swagger_input_path, swagger_draft_out_dir) if swagger_input_path else []

    if args.ai_summary or args.ai_recommendations:
        _validate_llm_provider(args.llm_provider, parser)

    def emit_progress(message: str) -> None:
        print(message, file=sys.stderr)

    report = scan_directory(
        root_path,
        exclude_dirs=args.exclude_dir,
        exclude_paths=[
            path
            for path in (
                json_output_path,
                csv_output_path,
                json_summary_output_path,
                json_file_reports_output_path,
                csv_file_reports_output_path,
                sql_output_path,
                html_output_path,
                cbom_output_path,
                ai_summary_output_path,
                ai_recommendations_output_path,
            )
            if path
        ],
        custom_rules=custom_rules,
        custom_regex_rules=custom_regex_rules,
        suppress_default_on_custom_match=args.custom_patterns_override_defaults,
        progress_callback=None if args.quiet else emit_progress,
        scan_domains=scan_domains,
        imported_cbom_components=imported_cbom_components,
    )

    if args.ai_summary:
        report.ai_summary = generate_ai_summary(
            report,
            provider=args.llm_provider,
            model=args.llm_model,
            ollama_url=args.ollama_url,
            timeout_seconds=args.llm_timeout_seconds,
        )
    if args.ai_recommendations:
        report.ai_recommendations = generate_ai_recommendations(
            report,
            provider=args.llm_provider,
            model=args.llm_model,
            ollama_url=args.ollama_url,
            timeout_seconds=args.llm_timeout_seconds,
        )

    console_output = render_console_report(
        report,
        show_hint_breakdown=args.show_hint_breakdown,
        include_file_reports=args.console_include_file_reports,
    )
    if swagger_draft_outputs:
        console_output = console_output.rstrip() + "\nSwagger draft files generated:\n" + "\n".join(f"  - {path}" for path in swagger_draft_outputs) + "\n"
    print(console_output)

    if args.json_out:
        write_json_report(report, json_output_path, include_file_reports=args.include_file_reports)
    if args.csv_out:
        write_change_targets_csv(report, csv_output_path)
    if args.json_summary_out:
        write_json_summary(report, json_summary_output_path)
    if args.json_file_reports_out:
        write_json_file_reports(report, json_file_reports_output_path)
    if args.csv_file_reports_out:
        write_file_reports_csv(report, csv_file_reports_output_path)
    if args.sql_out:
        write_dba_planning_sql(report, sql_output_path)
    if args.html_out:
        write_html_report(report, html_output_path)
    if args.cbom_out:
        write_cbom_file(cbom_output_path, report)
    if args.ai_summary_out and report.ai_summary:
        write_ai_summary_markdown(report.ai_summary, ai_summary_output_path)
    if args.ai_recommendations_out and report.ai_recommendations:
        write_ai_recommendations_markdown(report.ai_recommendations, ai_recommendations_output_path)

    return 0


def _parse_scan_domains(raw_value: str, parser: argparse.ArgumentParser) -> list[str]:
    scan_domains = sorted({item.strip().lower() for item in raw_value.split(",") if item.strip()})
    if not scan_domains:
        return ["pii"]
    unsupported = [item for item in scan_domains if item not in SUPPORTED_SCAN_DOMAINS]
    if unsupported:
        parser.error(
            "Unsupported scan domains: "
            + ", ".join(unsupported)
            + ". Supported values are: pii, pqc, pii,pqc."
        )
    return scan_domains


def _validate_llm_provider(raw_value: str, parser: argparse.ArgumentParser) -> None:
    provider = raw_value.strip().lower()
    if provider not in SUPPORTED_LLM_PROVIDERS:
        parser.error(
            "Unsupported LLM provider: "
            + raw_value
            + ". Supported values are: "
            + ", ".join(sorted(SUPPORTED_LLM_PROVIDERS))
            + "."
        )
