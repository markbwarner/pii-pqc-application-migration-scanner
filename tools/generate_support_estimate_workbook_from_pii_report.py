from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PureWindowsPath
from typing import Iterable

from generate_support_estimate_workbook import (
    Cell,
    cell,
    content_types_xml,
    root_rels_xml,
    styles_xml,
    workbook_rels_xml,
    workbook_xml,
    worksheet_xml,
)
from zipfile import ZIP_DEFLATED, ZipFile

DEFAULT_OUTPUT_DIR = Path("docs/pii/assessment/generated")
RATING_ORDER = {"low": 1, "medium": 2, "high": 3}
DEFAULT_COMPLEXITY_HOURS = {"low": 3.0, "medium": 7.5, "high": 15.5}
DEFAULT_READINESS_BY_COMPLEXITY = {"low": "High", "medium": "Medium", "high": "Low"}
DEFAULT_CRITICALITY_BY_CONTEXT = {
    "frontend": "BusinessHours",
    "docs": "BusinessHours",
    "backend": "Near24x7",
    "data_access": "Near24x7",
    "infrastructure_config": "HighlyCritical",
    "unknown": "BusinessHours",
}
DEFAULT_DATA_PERF_BY_FINDINGS = (
    (0, "Low"),
    (10, "Moderate"),
    (25, "High"),
)


@dataclass
class DerivedApplication:
    name: str
    path_prefix: str
    file_count: int
    target_file_count: int
    total_findings: int
    jdbc_candidate_total: int
    code_change_candidate_total: int
    complexity_rating: str
    dominant_action: str
    dominant_owner: str
    dominant_context: str
    default_readiness: str
    default_criticality: str
    default_data_perf: str
    notes: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a scan-informed CRDP support-estimate workbook from a PII file-reports JSON export."
    )
    parser.add_argument("--pii-file-reports", required=True, help="Path to a PII file-reports JSON export.")
    parser.add_argument("--label", help="Optional short label for the workbook title and output filename.")
    parser.add_argument("--output", help="Optional output .xlsx path.")
    return parser.parse_args()


def load_file_reports(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Expected a file-reports JSON array.")
    return payload


def normalize_path(value: str) -> PureWindowsPath:
    return PureWindowsPath(value)


def derive_application_key(report_path: str) -> tuple[str, str]:
    parts = list(normalize_path(report_path).parts)
    lowered = [part.lower() for part in parts]
    if "sample_code" in lowered:
        start = lowered.index("sample_code") + 1
        relative = parts[start:]
    else:
        relative = parts[-4:]
    if len(relative) >= 2 and relative[0].lower() in {"backend", "frontend", "infra", "ops"}:
        key_parts = relative[:2]
    elif relative:
        key_parts = relative[:1]
    else:
        key_parts = [Path(report_path).name]
    key = "/".join(key_parts)
    prefix = "\\".join(key_parts)
    return key, prefix


def choose_data_perf(total_findings: int) -> str:
    value = "Low"
    for threshold, label in DEFAULT_DATA_PERF_BY_FINDINGS:
        if total_findings >= threshold:
            value = label
    return value


def derive_notes(action: str, owner: str, contexts: Iterable[str], target_count: int, jdbc_count: int) -> str:
    context_set = sorted(set(contexts))
    notes: list[str] = []
    if owner == "frontend_reference_only":
        notes.append("Mostly front-end reference traffic; likely not the primary CRDP support owner.")
    if owner == "supporting_model":
        notes.append("Supporting-model or DTO-heavy area; often narrows out of true change-owner scope.")
    if action == "review_jdbc_substitution":
        notes.append("JDBC-style reduction candidate; application support burden may stay lower than direct wrapper changes.")
    if target_count > 0:
        notes.append(f"{target_count} likely change-target file(s) in this derived application bucket.")
    if jdbc_count > 0:
        notes.append(f"JDBC candidate count observed: {jdbc_count}.")
    if context_set:
        notes.append("Contexts: " + ", ".join(context_set) + ".")
    return " ".join(notes)


def derive_applications(file_reports: list[dict]) -> list[DerivedApplication]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    prefixes: dict[str, str] = {}
    for item in file_reports:
        if "pii_summary" not in item:
            continue
        key, prefix = derive_application_key(item.get("path", ""))
        grouped[key].append(item)
        prefixes[key] = prefix

    derived: list[DerivedApplication] = []
    for name, items in sorted(grouped.items()):
        action_counter: Counter[str] = Counter()
        owner_counter: Counter[str] = Counter()
        context_counter: Counter[str] = Counter()
        total_findings = 0
        jdbc_total = 0
        code_total = 0
        target_files = 0
        max_rating = "low"
        contexts: list[str] = []
        for item in items:
            pii = item.get("pii_summary") or {}
            ownership = pii.get("ownership") or {}
            complexity = pii.get("complexity") or {}
            total_findings += int(pii.get("total_findings") or 0)
            jdbc_total += int(pii.get("jdbc_candidate_count") or 0)
            code_total += int(pii.get("code_change_candidate_count") or 0)
            action = ownership.get("recommended_change_action") or "unknown"
            owner = ownership.get("likely_change_owner") or "unknown"
            context = ((item.get("classification") or {}).get("context") or "unknown")
            action_counter[action] += 1
            owner_counter[owner] += 1
            context_counter[context] += 1
            contexts.append(context)
            if ownership.get("likely_change_target"):
                target_files += 1
            rating = complexity.get("rating") or "low"
            if RATING_ORDER.get(rating, 0) >= RATING_ORDER.get(max_rating, 0):
                max_rating = rating
        dominant_action = action_counter.most_common(1)[0][0] if action_counter else "unknown"
        dominant_owner = owner_counter.most_common(1)[0][0] if owner_counter else "unknown"
        dominant_context = context_counter.most_common(1)[0][0] if context_counter else "unknown"
        derived.append(
            DerivedApplication(
                name=name,
                path_prefix=prefixes[name],
                file_count=len(items),
                target_file_count=target_files,
                total_findings=total_findings,
                jdbc_candidate_total=jdbc_total,
                code_change_candidate_total=code_total,
                complexity_rating=max_rating,
                dominant_action=dominant_action,
                dominant_owner=dominant_owner,
                dominant_context=dominant_context,
                default_readiness=DEFAULT_READINESS_BY_COMPLEXITY.get(max_rating, "Medium"),
                default_criticality=DEFAULT_CRITICALITY_BY_CONTEXT.get(dominant_context, "BusinessHours"),
                default_data_perf=choose_data_perf(total_findings),
                notes=derive_notes(dominant_action, dominant_owner, contexts, target_files, jdbc_total),
            )
        )
    return derived


def instructions_sheet(label: str, input_path: Path, app_count: int) -> list[list[Cell]]:
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    return [
        [cell("CRDP Support Effort Estimator (Scan-Informed)", style=1)],
        [cell("Purpose", style=1)],
        [cell("This workbook starts from a real PII file-reports JSON export and turns it into a scan-informed CRDP support-estimating workbook.")],
        [cell("Label", style=1), cell(label)],
        [cell("Generated at", style=1), cell(generated_at)],
        [cell("Input file", style=1), cell(str(input_path))],
        [cell("Derived application buckets", style=1), cell(app_count, kind="num")],
        [cell("How to use it", style=1)],
        [cell("1. Review the Input_Overview and Applications sheets to confirm the scan-derived starting point makes sense.")],
        [cell("2. On Derived_Scenarios, edit Readiness, Criticality, and Data / Performance if the operational reality differs from the defaults.")],
        [cell("3. Use Portfolio_Summary to compare total monthly and annual support effort after your edits.")],
        [cell("4. Treat this workbook as scan-informed, not fully automated: operational criticality and support maturity still require human judgement.")],
    ]


def overview_sheet(file_reports: list[dict], apps: list[DerivedApplication]) -> list[list[Cell]]:
    owner_counter = Counter()
    action_counter = Counter()
    context_counter = Counter()
    complexity_counter = Counter()
    likely_targets = 0
    total_findings = 0
    for item in file_reports:
        pii = item.get("pii_summary") or {}
        ownership = pii.get("ownership") or {}
        total_findings += int(pii.get("total_findings") or 0)
        owner_counter[ownership.get("likely_change_owner") or "unknown"] += 1
        action_counter[ownership.get("recommended_change_action") or "unknown"] += 1
        context_counter[((item.get("classification") or {}).get("context") or "unknown")] += 1
        complexity_counter[(pii.get("complexity") or {}).get("rating") or "unknown"] += 1
        if ownership.get("likely_change_target"):
            likely_targets += 1

    rows: list[list[Cell]] = [
        [cell("Input Overview", style=1)],
        [cell("Metric", style=1), cell("Value", style=1)],
        [cell("Files in input JSON"), cell(len(file_reports), kind="num")],
        [cell("Likely change-target files"), cell(likely_targets, kind="num")],
        [cell("Derived application buckets"), cell(len(apps), kind="num")],
        [cell("Total PII findings"), cell(total_findings, kind="num")],
        [],
        [cell("Owner summary", style=1), cell("Count", style=1)],
    ]
    rows.extend([[cell(name), cell(count, kind="num")] for name, count in sorted(owner_counter.items())])
    rows.extend([[], [cell("Recommended action summary", style=1), cell("Count", style=1)]])
    rows.extend([[cell(name), cell(count, kind="num")] for name, count in sorted(action_counter.items())])
    rows.extend([[], [cell("Context summary", style=1), cell("Count", style=1)]])
    rows.extend([[cell(name), cell(count, kind="num")] for name, count in sorted(context_counter.items())])
    rows.extend([[], [cell("Complexity summary", style=1), cell("Count", style=1)]])
    rows.extend([[cell(name), cell(count, kind="num")] for name, count in sorted(complexity_counter.items())])
    return rows


def applications_sheet(apps: list[DerivedApplication]) -> list[list[Cell]]:
    rows: list[list[Cell]] = [
        [cell("Derived Applications", style=1)],
        [
            cell("Application", style=1),
            cell("Path Prefix", style=1),
            cell("Files", style=1),
            cell("Likely Change Targets", style=1),
            cell("Total Findings", style=1),
            cell("JDBC Candidates", style=1),
            cell("Code-Change Candidates", style=1),
            cell("Complexity", style=1),
            cell("Dominant Action", style=1),
            cell("Dominant Owner", style=1),
            cell("Dominant Context", style=1),
            cell("Notes", style=1),
        ]
    ]
    for app in apps:
        rows.append([
            cell(app.name),
            cell(app.path_prefix),
            cell(app.file_count, kind="num"),
            cell(app.target_file_count, kind="num"),
            cell(app.total_findings, kind="num"),
            cell(app.jdbc_candidate_total, kind="num"),
            cell(app.code_change_candidate_total, kind="num"),
            cell(app.complexity_rating),
            cell(app.dominant_action),
            cell(app.dominant_owner),
            cell(app.dominant_context),
            cell(app.notes),
        ])
    return rows


def assumptions_sheet() -> list[list[Cell]]:
    return [
        [cell("Assumptions", style=1)],
        [],
        [cell("Base Complexity"), cell("Hours / App / Month", style=1), None, cell("Readiness"), cell("Multiplier", style=1), None, cell("Criticality"), cell("Multiplier", style=1), None, cell("Data / Performance"), cell("Multiplier", style=1)],
        [cell("Low"), cell(3.0, kind="num"), None, cell("High"), cell(0.95, kind="num"), None, cell("BusinessHours"), cell(1.0, kind="num"), None, cell("Low"), cell(1.0, kind="num")],
        [cell("Medium"), cell(7.5, kind="num"), None, cell("Medium"), cell(1.10, kind="num"), None, cell("Near24x7"), cell(1.3, kind="num"), None, cell("Moderate"), cell(1.2, kind="num")],
        [cell("High"), cell(15.5, kind="num"), None, cell("Low"), cell(1.50, kind="num"), None, cell("HighlyCritical"), cell(1.6, kind="num"), None, cell("High"), cell(1.5, kind="num")],
        [],
        [cell("Notes", style=1)],
        [cell("These defaults are editable and are intentionally similar to the static workbook so teams can compare static and scan-informed planning modes.")],
    ]


def derived_scenarios_sheet(apps: list[DerivedApplication]) -> list[list[Cell]]:
    rows: list[list[Cell]] = [
        [cell("Derived Support Scenarios", style=1)],
        [cell("Each row represents a scan-derived application bucket. Edit readiness, criticality, and data/performance labels if needed.")],
        [
            cell("Application", style=1),
            cell("File Count", style=1),
            cell("Likely Change Targets", style=1),
            cell("Complexity", style=1),
            cell("Base Complexity Hours / App / Month", style=1),
            cell("Readiness", style=1),
            cell("Readiness Multiplier", style=1),
            cell("Criticality", style=1),
            cell("Criticality Multiplier", style=1),
            cell("Data / Performance", style=1),
            cell("Data / Performance Multiplier", style=1),
            cell("Adjusted Monthly Hours / App", style=1),
            cell("Total Monthly Hours", style=1),
            cell("Notes", style=1),
        ],
    ]
    start_row = 4
    for offset, app in enumerate(apps):
        row_index = start_row + offset
        rows.append([
            cell(app.name),
            cell(app.file_count, kind="num"),
            cell(app.target_file_count, kind="num"),
            cell(app.complexity_rating),
            cell(f"VLOOKUP(D{row_index},Assumptions!$A$4:$B$6,2,FALSE)", kind="formula"),
            cell(app.default_readiness),
            cell(f"VLOOKUP(F{row_index},Assumptions!$D$4:$E$6,2,FALSE)", kind="formula"),
            cell(app.default_criticality),
            cell(f"VLOOKUP(H{row_index},Assumptions!$G$4:$H$6,2,FALSE)", kind="formula"),
            cell(app.default_data_perf),
            cell(f"VLOOKUP(J{row_index},Assumptions!$J$4:$K$6,2,FALSE)", kind="formula"),
            cell(f"E{row_index}*G{row_index}*I{row_index}*K{row_index}", kind="formula"),
            cell(f"C{row_index}*L{row_index}", kind="formula"),
            cell(app.notes),
        ])
    summary_row = start_row + len(apps) + 1
    rows.extend([
        [],
        [cell("Total derived applications", style=1), cell(f"COUNTA(A{start_row}:A{summary_row-2})", kind="formula")],
        [cell("Total monthly hours", style=1), cell(f"SUM(M{start_row}:M{summary_row-2})", kind="formula")],
        [cell("Total annual hours", style=1), cell(f"B{summary_row+1}*12", kind="formula")],
        [cell("Estimated monthly FTE (160h)", style=1), cell(f"B{summary_row+1}/160", kind="formula")],
    ])
    return rows


def portfolio_summary_sheet(apps: list[DerivedApplication]) -> list[list[Cell]]:
    return [
        [cell("Portfolio Summary", style=1)],
        [cell("This summary rolls up the scan-derived application buckets from the Derived_Scenarios sheet.")],
        [cell("Metric", style=1), cell("Value", style=1), cell("Interpretation", style=1)],
        [cell("Derived applications"), cell("Derived_Scenarios!B" + str(5 + len(apps)), kind="formula"), cell("Distinct scan-derived application buckets represented in this workbook.")],
        [cell("Total monthly hours"), cell("Derived_Scenarios!B" + str(6 + len(apps)), kind="formula"), cell("Editable planning total after readiness, criticality, and data/performance multipliers are applied.")],
        [cell("Total annual hours"), cell("Derived_Scenarios!B" + str(7 + len(apps)), kind="formula"), cell("Simple yearly rollup from the monthly total.")],
        [cell("Monthly FTE"), cell("Derived_Scenarios!B" + str(8 + len(apps)), kind="formula"), cell("Calculated using 160 hours per month as a planning assumption.")],
    ]


def write_workbook(path: Path, sheets: dict[str, str]) -> None:
    sheet_names = list(sheets.keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", content_types_xml(len(sheet_names)))
        workbook.writestr("_rels/.rels", root_rels_xml())
        workbook.writestr("xl/workbook.xml", workbook_xml(sheet_names))
        workbook.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(len(sheet_names)))
        workbook.writestr("xl/styles.xml", styles_xml())
        for index, sheet_name in enumerate(sheet_names, start=1):
            workbook.writestr(f"xl/worksheets/sheet{index}.xml", sheets[sheet_name])


def default_output_path(input_path: Path, label: str | None) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    stem = label or input_path.stem
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in stem).strip("_") or "scan_informed"
    return DEFAULT_OUTPUT_DIR / f"{safe}_crdp-support-estimator_{stamp}.xlsx"


def main() -> int:
    args = parse_args()
    input_path = Path(args.pii_file_reports).resolve()
    file_reports = load_file_reports(input_path)
    apps = derive_applications(file_reports)
    label = args.label or input_path.stem
    output_path = Path(args.output).resolve() if args.output else default_output_path(input_path, args.label)

    sheets = {
        "Instructions": worksheet_xml(instructions_sheet(label, input_path, len(apps)), column_widths=[28, 110]),
        "Input_Overview": worksheet_xml(overview_sheet(file_reports, apps), column_widths=[34, 18]),
        "Applications": worksheet_xml(applications_sheet(apps), column_widths=[24, 28, 10, 16, 14, 14, 20, 12, 22, 20, 18, 90]),
        "Assumptions": worksheet_xml(assumptions_sheet(), column_widths=[22, 18, 4, 18, 12, 4, 18, 12, 4, 20, 12]),
        "Derived_Scenarios": worksheet_xml(derived_scenarios_sheet(apps), column_widths=[24, 10, 16, 12, 24, 14, 18, 16, 18, 18, 22, 22, 18, 80]),
        "Portfolio_Summary": worksheet_xml(portfolio_summary_sheet(apps), column_widths=[24, 18, 90]),
    }
    write_workbook(output_path, sheets)
    print(f"Wrote scan-informed workbook to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
