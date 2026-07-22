from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

from .models import FileReport, ScanReport


RATING_ORDER = {"low": 1, "medium": 2, "high": 3}


def render_console_report(
    report: ScanReport,
    show_hint_breakdown: bool = False,
    include_file_reports: bool = False,
) -> str:
    lines: List[str] = []
    lines.append(f"Root path: {report.root_path}")
    lines.append(f"Scan domains: {', '.join(report.scan_domains)}")
    lines.append(f"Files scanned: {report.files_scanned}")
    lines.append(f"Files with findings: {report.files_with_findings}")
    if "pqc" in report.scan_domains:
        lines.append(f"Dependency references: {report.dependency_reference_total}")
        if report.imported_cbom_component_total:
            lines.append(f"Imported CBOM components: {report.imported_cbom_component_total}")
    if report.ai_summary:
        lines.append(f"AI summary enabled: provider={report.ai_summary.provider}, model={report.ai_summary.model}")
    if report.ai_recommendations:
        lines.append(f"AI recommendations enabled: provider={report.ai_recommendations.provider}, model={report.ai_recommendations.model}")
    if "pii" in report.scan_domains:
        lines.append(f"Files with PII indicators: {report.files_with_pii}")
        lines.append(f"Total PII matches: {report.total_pii_matches}")
        lines.append(f"Potential JDBC-driver candidates: {report.jdbc_candidate_total}")
        lines.append(f"Potential code-change candidates: {report.code_change_candidate_total}")
    if "pqc" in report.scan_domains:
        lines.append(f"Files with PQC indicators: {report.files_with_pqc}")
        lines.append(f"Total PQC findings: {report.total_pqc_findings}")
        lines.append(f"PQC likely change targets: {report.pqc_likely_change_target_total}")
    lines.append("")

    summary = _build_executive_summary(report)
    lines.extend(_render_executive_summary(summary))

    if report.ai_summary:
        lines.append("AI advisory summary:")
        for line in report.ai_summary.summary_markdown.splitlines()[:18]:
            lines.append(f"  {line}" if line else "")
        lines.append("")

    if report.ai_recommendations:
        lines.append("AI recommendation highlights:")
        for line in report.ai_recommendations.summary_markdown.splitlines()[:8]:
            lines.append(f"  {line}" if line else "")
        for item in report.ai_recommendations.file_recommendations[:3]:
            lines.append(f"  - [{item.priority}] {item.path}: {item.recommendation}")
        lines.append("")

    if not include_file_reports:
        return "\n".join(lines).rstrip() + "\n"

    for file_report in report.file_reports:
        lines.append(f"File: {file_report.path}")
        lines.append(
            f"  Layer: {file_report.classification.layer} "
            f"(context {file_report.classification.context}, confidence {file_report.classification.confidence})"
        )
        lines.append(f"  Overall change likelihood: {_overall_change_likelihood(file_report)}")
        if file_report.dependency_references:
            lines.append(f"  Dependency references: {len(file_report.dependency_references)}")
        if file_report.pii_matches:
            lines.append(
                f"  PII summary: matches={len(file_report.pii_matches)}, jdbc candidates={file_report.jdbc_candidate_count}, "
                f"code-change candidates={file_report.code_change_candidate_count}"
            )
        if file_report.pqc_findings:
            lines.append(
                f"  PQC summary: findings={len(file_report.pqc_findings)}, action={file_report.pqc_recommended_change_action}, "
                f"complexity={file_report.pqc_complexity.rating if file_report.pqc_complexity else ''}"
            )
        if show_hint_breakdown:
            if file_report.service_call_hint_breakdown:
                lines.append("  Service-call hint breakdown: " + _format_breakdown(file_report.service_call_hint_breakdown))
            if file_report.backend_hint_breakdown:
                lines.append("  Back-end hint breakdown: " + _format_breakdown(file_report.backend_hint_breakdown))
            if file_report.integration_hint_breakdown:
                lines.append("  Data-access/integration hint breakdown: " + _format_breakdown(file_report.integration_hint_breakdown))
        if file_report.dependency_references:
            lines.append("  Dependencies:")
            for reference in file_report.dependency_references[:10]:
                suffix = f" {reference.version}" if reference.version else ""
                cats = f" categories={','.join(reference.related_categories)}" if reference.related_categories else ""
                lines.append(f"    - {reference.name}{suffix} [{reference.ecosystem}/{reference.reference_type}]{cats}")
        if file_report.notes:
            lines.append("  Notes:")
            for note in file_report.notes:
                lines.append(f"    - {note}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_json_report(report: ScanReport, output_path: Path, include_file_reports: bool = False) -> None:
    output_path.write_text(json.dumps(_serialize_report(report, include_file_reports=include_file_reports), indent=2), encoding="utf-8")


def write_json_summary(report: ScanReport, output_path: Path) -> None:
    output_path.write_text(json.dumps(_serialize_summary_report(report), indent=2), encoding="utf-8")


def write_json_file_reports(report: ScanReport, output_path: Path) -> None:
    output_path.write_text(
        json.dumps(
            [_serialize_file_report(file_report, report.scan_domains) for file_report in report.file_reports],
            indent=2,
        ),
        encoding="utf-8",
    )


def write_change_targets_csv(report: ScanReport, output_path: Path) -> None:
    fieldnames = [
        "path",
        "finding_domains",
        "context",
        "overall_change_likelihood",
        "likely_change_target",
        "recommended_change_action",
        "pii_likely_change_target",
        "pii_recommended_change_action",
        "pqc_likely_change_target",
        "pqc_recommended_change_action",
        "dependency_reference_count",
        "dependency_packages",
        "dependency_categories",
        "jdbc_candidate_count",
        "code_change_candidate_count",
        "complexity_rating",
        "complexity_score",
        "pqc_complexity_rating",
        "pqc_complexity_score",
        "pqc_vulnerable_algorithms",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for file_report in report.file_reports:
            pii_target = bool(file_report.ownership and file_report.ownership.likely_change_target)
            pqc_target = file_report.pqc_likely_change_target
            if not pii_target and not pqc_target:
                continue
            writer.writerow(
                {
                    "path": file_report.path,
                    "finding_domains": ",".join(_finding_domains(file_report)),
                    "context": file_report.classification.context,
                    "overall_change_likelihood": _overall_change_likelihood(file_report),
                    "likely_change_target": True,
                    "recommended_change_action": _combined_change_action(file_report),
                    "pii_likely_change_target": pii_target,
                    "pii_recommended_change_action": file_report.ownership.recommended_change_action if file_report.ownership else "",
                    "pqc_likely_change_target": file_report.pqc_likely_change_target,
                    "pqc_recommended_change_action": file_report.pqc_recommended_change_action,
                    "dependency_reference_count": len(file_report.dependency_references),
                    "dependency_packages": " | ".join(sorted({item.name for item in file_report.dependency_references})),
                    "dependency_categories": " | ".join(sorted({cat for item in file_report.dependency_references for cat in item.related_categories})),
                    "jdbc_candidate_count": file_report.jdbc_candidate_count,
                    "code_change_candidate_count": file_report.code_change_candidate_count,
                    "complexity_rating": file_report.complexity.rating if file_report.complexity else "",
                    "complexity_score": file_report.complexity.score if file_report.complexity else "",
                    "pqc_complexity_rating": file_report.pqc_complexity.rating if file_report.pqc_complexity else "",
                    "pqc_complexity_score": file_report.pqc_complexity.score if file_report.pqc_complexity else "",
                    "pqc_vulnerable_algorithms": " | ".join(file_report.pqc_vulnerable_algorithms),
                }
            )


def write_file_reports_csv(report: ScanReport, output_path: Path) -> None:
    fieldnames = [
        "path",
        "finding_domains",
        "layer",
        "context",
        "classification_confidence",
        "overall_change_likelihood",
        "pii_matches",
        "pqc_findings",
        "dependency_reference_count",
        "dependency_packages",
        "dependency_categories",
        "likely_change_target",
        "recommended_change_action",
        "complexity_rating",
        "complexity_score",
        "pqc_complexity_rating",
        "pqc_complexity_score",
        "notes",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for file_report in report.file_reports:
            writer.writerow(
                {
                    "path": file_report.path,
                    "finding_domains": ",".join(_finding_domains(file_report)),
                    "layer": file_report.classification.layer,
                    "context": file_report.classification.context,
                    "classification_confidence": file_report.classification.confidence,
                    "overall_change_likelihood": _overall_change_likelihood(file_report),
                    "pii_matches": len(file_report.pii_matches),
                    "pqc_findings": len(file_report.pqc_findings),
                    "dependency_reference_count": len(file_report.dependency_references),
                    "dependency_packages": " | ".join(sorted({item.name for item in file_report.dependency_references})),
                    "dependency_categories": " | ".join(sorted({cat for item in file_report.dependency_references for cat in item.related_categories})),
                    "likely_change_target": bool((file_report.ownership and file_report.ownership.likely_change_target) or file_report.pqc_likely_change_target),
                    "recommended_change_action": _combined_change_action(file_report),
                    "complexity_rating": file_report.complexity.rating if file_report.complexity else "",
                    "complexity_score": file_report.complexity.score if file_report.complexity else "",
                    "pqc_complexity_rating": file_report.pqc_complexity.rating if file_report.pqc_complexity else "",
                    "pqc_complexity_score": file_report.pqc_complexity.score if file_report.pqc_complexity else "",
                    "notes": " | ".join(file_report.notes),
                }
            )


def write_dba_planning_sql(report: ScanReport, output_path: Path) -> None:
    lines: List[str] = []
    lines.append("-- DBA planning SQL generated from jdbc_candidate files")
    lines.append("")
    jdbc_tables = _collect_jdbc_candidate_tables(report)
    for table_name, details in jdbc_tables.items():
        columns = details["columns"]
        source_files = details["source_files"]
        lines.append(f"-- Table: {table_name}")
        lines.append(f"-- Source files: {', '.join(source_files)}")
        lines.append(f"describe {table_name};")
        lines.append("")
        if columns:
            lines.append("select")
            lines.append(",\n".join(f"  max(length({column})) as max_{column}_length" for column in columns))
            lines.append(f"from {table_name};")
            lines.append("")
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _serialize_report(report: ScanReport, include_file_reports: bool = False) -> Dict:
    payload = {
        "root_path": report.root_path,
        "scan_domains": report.scan_domains,
        "files_scanned": report.files_scanned,
        "files_with_findings": report.files_with_findings,
        "executive_summary": _build_executive_summary(report),
        "ai_summary": {
            "provider": report.ai_summary.provider,
            "model": report.ai_summary.model,
            "prompt_version": report.ai_summary.prompt_version,
            "generated_at_utc": report.ai_summary.generated_at_utc,
            "advisory_only": report.ai_summary.advisory_only,
            "summary_markdown": report.ai_summary.summary_markdown,
        } if report.ai_summary else None,
        "ai_recommendations": {
            "provider": report.ai_recommendations.provider,
            "model": report.ai_recommendations.model,
            "prompt_version": report.ai_recommendations.prompt_version,
            "generated_at_utc": report.ai_recommendations.generated_at_utc,
            "advisory_only": report.ai_recommendations.advisory_only,
            "summary_markdown": report.ai_recommendations.summary_markdown,
            "file_recommendations": [
                {
                    "path": item.path,
                    "priority": item.priority,
                    "recommendation": item.recommendation,
                    "rationale": item.rationale,
                }
                for item in report.ai_recommendations.file_recommendations
            ],
            "work_packages": [
                {
                    "name": item.name,
                    "rationale": item.rationale,
                    "related_categories": item.related_categories,
                    "target_paths": item.target_paths,
                }
                for item in report.ai_recommendations.work_packages
            ],
            "dependency_guidance": [
                {
                    "name": item.name,
                    "meaning": item.meaning,
                    "why_it_matters": item.why_it_matters,
                }
                for item in report.ai_recommendations.dependency_guidance
            ],
        } if report.ai_recommendations else None,
    }
    if "pii" in report.scan_domains:
        payload.update(
            {
                "files_with_pii": report.files_with_pii,
                "total_pii_matches": report.total_pii_matches,
                "jdbc_candidate_total": report.jdbc_candidate_total,
                "code_change_candidate_total": report.code_change_candidate_total,
                "totals_by_category": report.totals_by_category,
                "tables_summary": report.tables_summary,
            }
        )
    if "pqc" in report.scan_domains:
        payload.update(
            {
                "files_with_pqc": report.files_with_pqc,
                "total_pqc_findings": report.total_pqc_findings,
                "pqc_totals_by_category": report.pqc_totals_by_category,
                "pqc_migration_class_totals": report.pqc_migration_class_totals,
                "pqc_likely_change_target_total": report.pqc_likely_change_target_total,
                "dependency_reference_total": report.dependency_reference_total,
                "dependency_package_summary": report.dependency_package_summary,
                "imported_cbom_component_total": report.imported_cbom_component_total,
                "cbom_components": [
                    {
                        "name": component.name,
                        "ecosystem": component.ecosystem,
                        "version": component.version,
                        "type": component.component_type,
                        "origin": component.origin,
                        "source_files": component.source_files,
                        "related_categories": component.related_categories,
                    }
                    for component in report.cbom_components
                ],
            }
        )
    if include_file_reports:
        payload["file_reports"] = [_serialize_file_report(file_report, report.scan_domains) for file_report in report.file_reports]
    return payload


def _serialize_summary_report(report: ScanReport) -> Dict:
    return _serialize_report(report, include_file_reports=False)


def _build_executive_summary(report: ScanReport) -> Dict:
    payload: Dict[str, Dict] = {}
    if "pqc" in report.scan_domains:
        payload["dependencies"] = {
            "dependency_reference_total": report.dependency_reference_total,
            "dependency_package_summary": report.dependency_package_summary,
            "cbom_component_total": len(report.cbom_components),
            "imported_cbom_component_total": report.imported_cbom_component_total,
        }
    if "pii" in report.scan_domains:
        payload["pii"] = {
            "likely_change_owner_summary": dict(sorted(Counter(
                file_report.ownership.likely_change_owner
                for file_report in report.file_reports
                if file_report.ownership
            ).items())),
            "recommended_change_action_summary": dict(sorted(Counter(
                file_report.ownership.recommended_change_action
                for file_report in report.file_reports
                if file_report.ownership
            ).items())),
            "role_in_flow_summary": dict(sorted(Counter(
                file_report.ownership.role_in_flow
                for file_report in report.file_reports
                if file_report.ownership
            ).items())),
            "complexity_distribution": dict(sorted(Counter(
                file_report.complexity.rating
                for file_report in report.file_reports
                if file_report.complexity
            ).items())),
            "tables_summary": report.tables_summary,
        }
    if "pqc" in report.scan_domains:
        payload["pqc"] = {
            "categories": dict(sorted(report.pqc_totals_by_category.items())),
            "migration_class_totals": dict(sorted(report.pqc_migration_class_totals.items())),
            "file_context_summary": dict(sorted(Counter(
                file_report.classification.context
                for file_report in report.file_reports
                if file_report.pqc_findings
            ).items())),
            "complexity_distribution": dict(sorted(Counter(
                file_report.pqc_complexity.rating
                for file_report in report.file_reports
                if file_report.pqc_complexity
            ).items())),
            "recommended_change_action_summary": dict(sorted(Counter(
                file_report.pqc_recommended_change_action
                for file_report in report.file_reports
                if file_report.pqc_findings
            ).items())),
        }
    if report.ai_summary:
        payload["ai_summary_metadata"] = {
            "provider": report.ai_summary.provider,
            "model": report.ai_summary.model,
            "prompt_version": report.ai_summary.prompt_version,
            "advisory_only": report.ai_summary.advisory_only,
        }
    if report.ai_recommendations:
        payload["ai_recommendations_metadata"] = {
            "provider": report.ai_recommendations.provider,
            "model": report.ai_recommendations.model,
            "prompt_version": report.ai_recommendations.prompt_version,
            "advisory_only": report.ai_recommendations.advisory_only,
            "file_recommendation_count": len(report.ai_recommendations.file_recommendations),
            "work_package_count": len(report.ai_recommendations.work_packages),
        }
    return payload


def _render_executive_summary(summary: Dict) -> List[str]:
    lines: List[str] = ["Executive summary:"]
    dependency_summary = summary.get("dependencies", {})
    if dependency_summary:
        lines.append("  Dependency enrichment summary:")
        lines.append(f"    - dependency_reference_total: {dependency_summary.get('dependency_reference_total', 0)}")
        lines.append(f"    - cbom_component_total: {dependency_summary.get('cbom_component_total', 0)}")
        lines.append(f"    - imported_cbom_component_total: {dependency_summary.get('imported_cbom_component_total', 0)}")
        for package_name, count in list(dependency_summary.get("dependency_package_summary", {}).items())[:8]:
            lines.append(f"    - package {package_name}: {count}")

    pii_summary = summary.get("pii", {})
    if pii_summary:
        lines.append("  PII complexity distribution:")
        for key, value in pii_summary.get("complexity_distribution", {}).items():
            lines.append(f"    - {key}: {value}")

    pqc_summary = summary.get("pqc", {})
    if pqc_summary:
        lines.append("  PQC recommended change action summary:")
        for key, value in pqc_summary.get("recommended_change_action_summary", {}).items():
            lines.append(f"    - {key}: {value}")
        lines.append("  PQC category summary:")
        for key, value in pqc_summary.get("categories", {}).items():
            lines.append(f"    - {key}: {value}")

    ai_summary_metadata = summary.get("ai_summary_metadata", {})
    if ai_summary_metadata:
        lines.append("  AI summary metadata:")
        lines.append(f"    - provider: {ai_summary_metadata.get('provider', '')}")
        lines.append(f"    - model: {ai_summary_metadata.get('model', '')}")
        lines.append(f"    - prompt_version: {ai_summary_metadata.get('prompt_version', '')}")
        lines.append(f"    - advisory_only: {ai_summary_metadata.get('advisory_only', True)}")

    ai_recommendations_metadata = summary.get("ai_recommendations_metadata", {})
    if ai_recommendations_metadata:
        lines.append("  AI recommendations metadata:")
        lines.append(f"    - provider: {ai_recommendations_metadata.get('provider', '')}")
        lines.append(f"    - model: {ai_recommendations_metadata.get('model', '')}")
        lines.append(f"    - prompt_version: {ai_recommendations_metadata.get('prompt_version', '')}")
        lines.append(f"    - advisory_only: {ai_recommendations_metadata.get('advisory_only', True)}")
        lines.append(f"    - file_recommendation_count: {ai_recommendations_metadata.get('file_recommendation_count', 0)}")
        lines.append(f"    - work_package_count: {ai_recommendations_metadata.get('work_package_count', 0)}")

    lines.append("")
    return lines


def _serialize_file_report(file_report: FileReport, active_domains: List[str] | None = None) -> Dict:
    domains = set(active_domains or [])
    payload = {
        "path": file_report.path,
        "finding_domains": _finding_domains(file_report),
        "overall_change_likelihood": _overall_change_likelihood(file_report),
        "lines_of_code": file_report.lines_of_code,
        "classification": {
            "layer": file_report.classification.layer,
            "context": file_report.classification.context,
            "confidence": file_report.classification.confidence,
            "reasons": file_report.classification.reasons,
        },
        "notes": file_report.notes,
    }
    if "pii" in domains:
        payload["pii_summary"] = {
            "total_findings": len(file_report.pii_matches),
            "summary_by_category": file_report.summary_by_category,
            "jdbc_candidate_count": file_report.jdbc_candidate_count,
            "code_change_candidate_count": file_report.code_change_candidate_count,
            "complexity": {
                "score": file_report.complexity.score,
                "rating": file_report.complexity.rating,
                "rationale": file_report.complexity.rationale,
            } if file_report.complexity else None,
            "ownership": {
                "likely_change_owner": file_report.ownership.likely_change_owner,
                "likely_change_target": file_report.ownership.likely_change_target,
                "recommended_change_action": file_report.ownership.recommended_change_action,
                "ownership_confidence": file_report.ownership.ownership_confidence,
                "role_in_flow": file_report.ownership.role_in_flow,
                "frontend_reference_only": file_report.ownership.frontend_reference_only,
                "backend_owner_confidence": file_report.ownership.backend_owner_confidence,
                "jdbc_substitution_candidate": file_report.ownership.jdbc_substitution_candidate,
                "endpoint_correlation_score": file_report.ownership.endpoint_correlation_score,
                "matched_endpoints": file_report.ownership.matched_endpoints,
                "matched_payload_fields": file_report.ownership.matched_payload_fields,
                "likely_system_of_record_path": file_report.ownership.likely_system_of_record_path,
                "related_files": file_report.ownership.related_files,
                "rationale": file_report.ownership.rationale,
            } if file_report.ownership else None,
        }
        payload["pii_matches"] = [
            {
                "line_number": match.line_number,
                "attribute": match.attribute,
                "category": match.category,
                "detector": match.detector,
                "confidence": match.confidence,
                "impact_hint": match.impact_hint,
                "pattern_name": match.pattern_name,
            }
            for match in file_report.pii_matches
        ]
    if "pqc" in domains:
        payload["dependency_references"] = [
            {
                "name": item.name,
                "ecosystem": item.ecosystem,
                "reference_type": item.reference_type,
                "source": item.source,
                "line_number": item.line_number,
                "version": item.version,
                "related_categories": item.related_categories,
            }
            for item in file_report.dependency_references
        ]
        payload["pqc_summary"] = {
            "total_findings": len(file_report.pqc_findings),
            "categories": file_report.pqc_summary_by_category,
            "migration_classes": file_report.pqc_migration_classes,
            "vulnerable_algorithms": file_report.pqc_vulnerable_algorithms,
            "implementation_findings": file_report.pqc_implementation_finding_count,
            "reference_findings": file_report.pqc_reference_finding_count,
            "likely_change_target": file_report.pqc_likely_change_target,
            "recommended_change_action": file_report.pqc_recommended_change_action,
            "migration_complexity": {
                "score": file_report.pqc_complexity.score,
                "rating": file_report.pqc_complexity.rating,
                "rationale": file_report.pqc_complexity.rationale,
            } if file_report.pqc_complexity else None,
        }
        payload["pqc_findings"] = [
            {
                "line_number": finding.line_number,
                "category": finding.category,
                "algorithm": finding.algorithm,
                "matched_text": finding.matched_text,
                "finding_kind": finding.finding_kind,
                "migration_class": finding.migration_class,
                "confidence": finding.confidence,
                "severity": finding.severity,
            }
            for finding in file_report.pqc_findings
        ]
    return payload


def _collect_jdbc_candidate_tables(report: ScanReport) -> Dict[str, Dict[str, List[str]]]:
    tables: Dict[str, Dict[str, List[str]]] = {}
    for file_report in report.file_reports:
        if not file_report.ownership:
            continue
        if file_report.ownership.recommended_change_action != "review_jdbc_substitution":
            continue
        for table_name, columns in sorted(file_report.sensitive_tables.items()):
            entry = tables.setdefault(table_name, {"columns": [], "source_files": []})
            entry["columns"] = sorted(set(entry["columns"]) | set(columns))
            entry["source_files"] = sorted(set(entry["source_files"]) | {Path(file_report.path).name})
    return tables


def _finding_domains(file_report: FileReport) -> List[str]:
    domains: List[str] = []
    if file_report.pii_matches:
        domains.append("pii")
    if file_report.pqc_findings:
        domains.append("pqc")
    return domains


def _combined_change_action(file_report: FileReport) -> str:
    actions: List[str] = []
    if file_report.ownership and file_report.ownership.likely_change_target:
        actions.append(file_report.ownership.recommended_change_action)
    if file_report.pqc_likely_change_target:
        actions.append(file_report.pqc_recommended_change_action)
    if not actions and file_report.pqc_findings:
        return file_report.pqc_recommended_change_action or "reference_only_or_low_priority"
    return " | ".join(actions)


def _overall_change_likelihood(file_report: FileReport) -> str:
    ratings: List[str] = []
    if file_report.complexity:
        ratings.append(file_report.complexity.rating)
    if file_report.pqc_complexity:
        ratings.append(file_report.pqc_complexity.rating)
    if not ratings:
        return "low"
    return max(ratings, key=lambda item: RATING_ORDER.get(item, 0))


def _format_breakdown(breakdown: Dict[str, int]) -> str:
    items = sorted(breakdown.items(), key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{pattern}({count})" for pattern, count in items)
