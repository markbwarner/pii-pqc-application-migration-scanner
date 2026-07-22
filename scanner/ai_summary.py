from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .models import AiSummary, ScanReport
from .ollama_client import DEFAULT_OLLAMA_URL, call_ollama_text


DEFAULT_OLLAMA_MODEL = "llama3.2:1b"
PROMPT_VERSION = "phase3-v7"
REQUIRED_HEADINGS = [
    "## Overall Assessment",
    "## Top Hotspots",
    "## Implementation Vs Reference Findings",
    "## Suggested Work Packages",
    "## Recommended Next Steps",
    "## Caveats",
]


def generate_ai_summary(
    report: ScanReport,
    provider: str,
    model: str,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout_seconds: int = 60,
) -> AiSummary:
    provider_name = provider.strip().lower()
    if provider_name != "ollama":
        raise ValueError(f"Unsupported LLM provider: {provider}")

    deterministic_summary = _build_deterministic_summary(report)
    system_prompt, user_prompt = _build_prompt(report)
    try:
        ai_response = call_ollama_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            url=ollama_url,
            timeout_seconds=timeout_seconds,
            num_predict=550,
        )
    except RuntimeError as exc:
        summary_markdown = (
            deterministic_summary
            + "\n\n- AI model advisory enhancement was unavailable for this run, so this summary uses the deterministic fallback only."
            + f" Failure detail: `{str(exc).strip()}`."
        )
    else:
        if _looks_usable(ai_response):
            summary_markdown = ai_response.strip()
        else:
            summary_markdown = _merge_summary_sections(ai_response, deterministic_summary)
    return AiSummary(
        provider="ollama",
        model=model,
        summary_markdown=summary_markdown.strip(),
        prompt_version=PROMPT_VERSION,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        advisory_only=True,
    )


def write_ai_summary_markdown(summary: AiSummary, output_path: Path) -> None:
    front_matter = [
        "# AI Migration Summary",
        "",
        f"- Provider: `{summary.provider}`",
        f"- Model: `{summary.model}`",
        f"- Prompt version: `{summary.prompt_version}`",
        f"- Generated at (UTC): `{summary.generated_at_utc}`",
        f"- Advisory only: `{str(summary.advisory_only).lower()}`",
        "",
    ]
    output_path.write_text("\n".join(front_matter) + summary.summary_markdown.strip() + "\n", encoding="utf-8")


def _build_prompt(report: ScanReport) -> tuple[str, str]:
    payload = {
        "root_path": report.root_path,
        "scan_domains": report.scan_domains,
        "files_scanned": report.files_scanned,
        "files_with_findings": report.files_with_findings,
        "files_with_pqc": report.files_with_pqc,
        "total_pqc_findings": report.total_pqc_findings,
        "files_with_pii": report.files_with_pii,
        "total_pii_matches": report.total_pii_matches,
        "top_pqc_categories": list(sorted(report.pqc_totals_by_category.items(), key=lambda item: (-item[1], item[0])))[:4],
        "top_pqc_migration_classes": list(sorted(report.pqc_migration_class_totals.items(), key=lambda item: (-item[1], item[0])))[:4],
        "recommended_actions_summary": _recommended_actions_summary(report),
        "cbom_ecosystem_summary": _cbom_ecosystem_summary(report),
        "hotspots": _compact_hotspot_payload(report),
        "reference_examples": _compact_reference_payload(report),
    }
    system_prompt = """
Write a concise markdown migration summary for security and architecture stakeholders.
Use exactly these headings and no others:
## Overall Assessment
## Top Hotspots
## Implementation Vs Reference Findings
## Suggested Work Packages
## Recommended Next Steps
## Caveats
Stay grounded in the facts.
Do not invent teams, approvals, environments, or process details.
Return markdown only.
""".strip()
    user_prompt = (
        "Use the JSON facts below to produce the summary. Keep it specific, compact, and practical.\n\n"
        + "Facts:\n```json\n"
        + json.dumps(payload, separators=(",", ":"))
        + "\n```\n"
    )
    return system_prompt, user_prompt


def _build_deterministic_summary(report: ScanReport) -> str:
    lines: List[str] = []

    lines.append("## Overall Assessment")
    lines.extend(_overall_assessment_lines(report))
    lines.append("")

    lines.append("## Top Hotspots")
    lines.extend(_top_hotspot_lines(report))
    lines.append("")

    lines.append("## Implementation Vs Reference Findings")
    lines.extend(_implementation_vs_reference_lines(report))
    lines.append("")

    lines.append("## Suggested Work Packages")
    lines.extend(_work_package_lines(report))
    lines.append("")

    lines.append("## Recommended Next Steps")
    lines.extend(_next_step_lines(report))
    lines.append("")

    lines.append("## Caveats")
    lines.extend(_caveat_lines(report))
    lines.append("")

    return "\n".join(lines).strip()


def _compact_hotspot_payload(report: ScanReport) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for item in _top_hotspot_payload(report)[:4]:
        items.append(
            {
                "path": item["path"],
                "context": item["context"],
                "pqc_findings": item["pqc_findings"],
                "pqc_categories": item["pqc_categories"],
                "pqc_recommended_change_action": item["pqc_recommended_change_action"],
                "pqc_complexity": item["pqc_complexity"],
                "top_dependencies": item["top_dependencies"][:3],
                "notes": item["notes"][:1],
            }
        )
    return items


def _compact_reference_payload(report: ScanReport) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for item in _reference_only_payload(report)[:3]:
        items.append(
            {
                "path": item["path"],
                "context": item["context"],
                "pqc_recommended_change_action": item["pqc_recommended_change_action"],
                "pqc_categories": item["pqc_categories"],
            }
        )
    return items


def _merge_summary_sections(ai_response: str, deterministic_summary: str) -> str:
    ai_sections = _split_sections(ai_response)
    deterministic_sections = _split_sections(deterministic_summary)
    merged_lines: List[str] = []
    used_ai = False

    for heading in REQUIRED_HEADINGS:
        merged_lines.append(heading)
        ai_body = ai_sections.get(heading, "").strip()
        deterministic_body = deterministic_sections.get(heading, "").strip()
        if ai_body and _section_looks_usable(ai_body):
            merged_lines.append(ai_body)
            used_ai = True
        else:
            merged_lines.append(deterministic_body)
        merged_lines.append("")

    if used_ai:
        caveat_index = merged_lines.index("## Caveats") + 2
        merged_lines.insert(caveat_index, "- AI advisory content was partially blended with deterministic sections because the model response did not fully match the required report structure.")
    else:
        caveat_index = merged_lines.index("## Caveats") + 2
        merged_lines.insert(caveat_index, "- AI model advisory enhancement returned an unusable response, so this summary uses the deterministic fallback structure.")

    return "\n".join(line for line in merged_lines).strip()


def _split_sections(markdown_text: str) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    current_heading: str | None = None
    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        if line in REQUIRED_HEADINGS:
            current_heading = line
            sections.setdefault(current_heading, [])
            continue
        if current_heading is not None:
            sections[current_heading].append(line)
    return {heading: "\n".join(lines).strip() for heading, lines in sections.items()}


def _section_looks_usable(text: str) -> bool:
    normalized = text.strip()
    if not normalized:
        return False
    if len(normalized) < 40:
        return False
    return "- " in normalized or "1. " in normalized


def _overall_assessment_lines(report: ScanReport) -> List[str]:
    lines = [
        f"- The scan covered `{report.files_scanned}` files and produced findings in `{report.files_with_findings}` files across the domains `{', '.join(report.scan_domains)}`.",
        f"- PQC findings are concentrated in `{report.files_with_pqc}` files with `{report.total_pqc_findings}` total findings and `{report.pqc_likely_change_target_total}` likely PQC change targets." if "pqc" in report.scan_domains else f"- PII findings are concentrated in `{report.files_with_pii}` files with `{report.total_pii_matches}` total matches.",
        f"- Dependency enrichment observed `{report.dependency_reference_total}` references and `{len(report.cbom_components)}` CBOM components across ecosystems such as {', '.join(_top_ecosystems(report))}." if report.cbom_components else "- No CBOM components were observed in this run.",
    ]
    if report.files_with_pqc:
        lines.append(
            "- The highest-volume PQC categories are "
            + ", ".join(f"`{category}` ({count})" for category, count in list(sorted(report.pqc_totals_by_category.items(), key=lambda item: (-item[1], item[0])))[:4])
            + "."
        )
    if report.files_with_pii:
        lines.append(
            "- The highest-volume PII categories are "
            + ", ".join(f"`{category}` ({count})" for category, count in list(sorted(report.totals_by_category.items(), key=lambda item: (-item[1], item[0])))[:4])
            + "."
        )
    context_summary = _pqc_file_context_summary(report)
    if context_summary:
        lines.append(
            "- PQC-heavy files are distributed across contexts "
            + ", ".join(f"`{context}` ({count})" for context, count in list(sorted(context_summary.items(), key=lambda item: (-item[1], item[0]))))
            + "."
        )
    complexity_summary = _pqc_complexity_distribution(report)
    if complexity_summary:
        lines.append(
            "- PQC migration complexity trends are "
            + ", ".join(f"`{rating}` ({count})" for rating, count in list(sorted(complexity_summary.items(), key=lambda item: (-item[1], item[0]))))
            + "."
        )
    return lines[:6]


def _top_hotspot_lines(report: ScanReport) -> List[str]:
    lines: List[str] = []
    for item in _top_hotspot_payload(report)[:10]:
        reasons: List[str] = []
        if item["pqc_categories"]:
            reasons.append("PQC categories " + ", ".join(f"`{key}`={value}" for key, value in sorted(item["pqc_categories"].items())))
        if item["pii_categories"]:
            reasons.append("PII categories " + ", ".join(f"`{key}`={value}" for key, value in sorted(item["pii_categories"].items())[:4]))
        if item["pqc_migration_classes"]:
            reasons.append("migration classes " + ", ".join(f"`{key}`={value}" for key, value in sorted(item["pqc_migration_classes"].items())))
        if item["pqc_recommended_change_action"]:
            reasons.append(f"recommended PQC action `{item['pqc_recommended_change_action']}`")
        if item["pii_recommended_change_action"]:
            reasons.append(f"recommended PII action `{item['pii_recommended_change_action']}`")
        if item["pqc_complexity"]:
            reasons.append(f"PQC complexity `{item['pqc_complexity']['rating']}` ({item['pqc_complexity']['score']})")
        elif item["pii_complexity"]:
            reasons.append(f"PII complexity `{item['pii_complexity']['rating']}` ({item['pii_complexity']['score']})")
        if item["top_dependencies"]:
            reasons.append("crypto-relevant dependencies " + ", ".join(f"`{name}`" for name in item["top_dependencies"][:4]))
        if item["pqc_vulnerable_algorithms"]:
            reasons.append("algorithms or key types " + ", ".join(f"`{name}`" for name in item["pqc_vulnerable_algorithms"][:4]))
        if item["notes"]:
            reasons.append("notes " + ", ".join(f"`{note}`" for note in item["notes"][:2]))
        lines.append(f"- `{item['path']}`: " + "; ".join(reasons[:6]) + ".")
    return lines or ["- No hotspot files were identified from the current scan."]


def _implementation_vs_reference_lines(report: ScanReport) -> List[str]:
    lines: List[str] = []
    implementation = [item for item in _top_hotspot_payload(report) if item["pqc_likely_change_target"] or item["pii_likely_change_target"]]
    reference_only = _reference_only_payload(report)
    for item in implementation[:6]:
        action = item["pqc_recommended_change_action"] or item["pii_recommended_change_action"] or "needs_manual_review"
        complexity = item["pqc_complexity"]["rating"] if item["pqc_complexity"] else item["pii_complexity"]["rating"] if item["pii_complexity"] else "unknown"
        lines.append(
            f"- Likely implementation owner: `{item['path']}` with action `{action}` in context `{item['context']}`; complexity `{complexity}`; "
            f"findings split `{item['pqc_findings']}` PQC and `{item['pii_matches']}` PII."
        )
    for item in reference_only[:5]:
        action = item["pqc_recommended_change_action"] or item["pii_recommended_change_action"] or "reference_only_or_low_priority"
        categories = item["pqc_categories"]
        category_text = ", ".join(f"`{key}`={value}" for key, value in sorted(categories.items())[:3]) if categories else "no dominant category"
        lines.append(
            f"- Likely reference-only or secondary file: `{item['path']}` with action `{action}` in context `{item['context']}`; "
            f"dominant PQC categories {category_text}."
        )
    action_summary = _pqc_recommended_change_action_summary(report)
    if action_summary:
        lines.append(
            "- Recommended-action distribution across the scan is "
            + ", ".join(
                f"`{action}` ({count})"
                for action, count in list(sorted(action_summary.items(), key=lambda item: (-item[1], item[0])))[:6]
            )
            + "."
        )
    return lines or ["- The current scan did not provide enough evidence to separate implementation-heavy files from reference-only files."]


def _work_package_lines(report: ScanReport) -> List[str]:
    lines: List[str] = []
    pqc_categories = report.pqc_totals_by_category
    if pqc_categories.get("JWT_OR_TOKEN_SIGNING"):
        lines.append("- JWT and application-signing work package: prioritize files marked `review_pqc_application_signing` and dependencies such as `jsonwebtoken`, `jose`, `io.jsonwebtoken.Jwts`, `io.jsonwebtoken.SignatureAlgorithm`, and `Microsoft.IdentityModel.Tokens`.")
    if pqc_categories.get("TLS_CONFIGURATION") or pqc_categories.get("CERTIFICATE_USAGE"):
        lines.append("- TLS and certificate lifecycle work package: review files tied to `TLS_CONFIGURATION` or `CERTIFICATE_USAGE`, especially mTLS, keystore, certificate, truststore, certificate loader, and ingress-related configuration.")
    if pqc_categories.get("KMS_OR_HSM_ASYMMETRIC"):
        lines.append("- KMS/HSM dependency work package: review `KMS_OR_HSM_ASYMMETRIC` findings and CBOM components such as `@aws-sdk/client-kms`, `Azure.Security.KeyVault.Keys`, `boto3`, and `cloud.google.com/go/kms/apiv1`; confirm whether keys are for signing, certificate issuance, or protocol termination.")
    if pqc_categories.get("SSH_USAGE"):
        lines.append("- SSH protocol work package: review `SSH_USAGE` findings including `golang.org/x/crypto/ssh`, `ssh2`, and `paramiko` for protocol and key-management readiness.")
    if pqc_categories.get("CODE_SIGNING"):
        lines.append("- Code-signing work package: review `CODE_SIGNING` findings and certificate-related dependencies such as `System.Security.Cryptography.Pkcs`.")
    ecosystem_summary = _cbom_ecosystem_summary(report)
    if ecosystem_summary:
        lines.append(
            "- Ecosystem coverage for this run includes "
            + ", ".join(f"`{ecosystem}` ({count})" for ecosystem, count in ecosystem_summary.items())
            + ", which helps separate remediation by platform."
        )
    if report.jdbc_candidate_total:
        lines.append("- JDBC substitution work package: prioritize files with `review_jdbc_substitution` and validate the affected sensitive tables for rollout readiness.")
    return lines[:8] or ["- No distinct work packages were identified from the current scan results."]


def _next_step_lines(report: ScanReport) -> List[str]:
    lines: List[str] = []
    hotspot_items = _top_hotspot_payload(report)[:5]
    for index, item in enumerate(hotspot_items[:4], start=1):
        action = item["pqc_recommended_change_action"] or item["pii_recommended_change_action"] or "needs_manual_review"
        categories = ", ".join(f"`{key}`" for key in list(sorted(item["pqc_categories"].keys()))[:4]) or "`none`"
        lines.append(
            f"{index}. Review `{item['path']}` first and confirm whether the suggested action `{action}` matches the real implementation boundary and the observed categories {categories}."
        )
    next_index = len(lines) + 1
    if report.pqc_totals_by_category:
        lines.append(f"{next_index}. Validate the highest-volume PQC categories against real deployment and key-management architecture, especially {', '.join(f'`{key}`' for key, _ in list(sorted(report.pqc_totals_by_category.items(), key=lambda item: (-item[1], item[0])))[:3])}.")
        next_index += 1
    if report.dependency_package_summary:
        lines.append(f"{next_index}. Use the CBOM and dependency summary to confirm whether packaged crypto dependencies match the source-level findings before planning remediation sequencing.")
        next_index += 1
    if _pqc_recommended_change_action_summary(report):
        lines.append(f"{next_index}. Group remediation planning by recommended change action so protocol, signing, KMS/HSM, and reference-only work do not get mixed into one backlog.")
        next_index += 1
    if report.tables_summary:
        lines.append(f"{next_index}. Review the detected sensitive tables and likely JDBC substitution candidates to separate data-access work from application-signing and protocol work.")
    return lines[:8] or ["1. Begin with the top hotspot files and confirm the recommended actions against the real architecture."]


def _caveat_lines(report: ScanReport) -> List[str]:
    lines = [
        "- This summary is advisory and is generated on top of deterministic scanner output rather than replacing it.",
        "- Static scanning can identify likely implementation points and reference-only files, but final ownership and remediation scope still need human review.",
    ]
    if _reference_only_payload(report):
        lines.append("- Some findings appear in frontend, documentation, or other reference-oriented files, so not every finding implies a primary implementation change.")
    if report.imported_cbom_component_total:
        lines.append("- Imported CBOM data can enrich the scan, but BOM presence alone does not prove the exact runtime usage path.")
    return lines[:5]


def _top_hotspot_payload(report: ScanReport) -> List[Dict[str, Any]]:
    ranked = sorted(
        report.file_reports,
        key=lambda item: (
            -_combined_severity_score(item),
            -(len(item.pqc_findings) + len(item.pii_matches)),
            item.path.lower(),
        ),
    )
    items: List[Dict[str, Any]] = []
    for file_report in ranked[:16]:
        items.append(
            {
                "path": file_report.path,
                "context": file_report.classification.context,
                "layer": file_report.classification.layer,
                "pii_matches": len(file_report.pii_matches),
                "pqc_findings": len(file_report.pqc_findings),
                "pii_recommended_change_action": file_report.ownership.recommended_change_action if file_report.ownership else "",
                "pqc_recommended_change_action": file_report.pqc_recommended_change_action,
                "pii_likely_change_target": bool(file_report.ownership and file_report.ownership.likely_change_target),
                "pqc_likely_change_target": file_report.pqc_likely_change_target,
                "pii_complexity": {
                    "rating": file_report.complexity.rating,
                    "score": file_report.complexity.score,
                } if file_report.complexity else None,
                "pqc_complexity": {
                    "rating": file_report.pqc_complexity.rating,
                    "score": file_report.pqc_complexity.score,
                } if file_report.pqc_complexity else None,
                "pii_categories": file_report.summary_by_category,
                "pqc_categories": file_report.pqc_summary_by_category,
                "pqc_migration_classes": file_report.pqc_migration_classes,
                "pqc_vulnerable_algorithms": file_report.pqc_vulnerable_algorithms,
                "top_dependencies": sorted({item.name for item in file_report.dependency_references if item.related_categories})[:6],
                "notes": file_report.notes[:2],
            }
        )
    return items


def _reference_only_payload(report: ScanReport) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for file_report in report.file_reports:
        if file_report.classification.context in {"frontend", "docs", "test"} or (
            file_report.pqc_findings and not file_report.pqc_likely_change_target
        ):
            items.append(
                {
                    "path": file_report.path,
                    "context": file_report.classification.context,
                    "pii_recommended_change_action": file_report.ownership.recommended_change_action if file_report.ownership else "",
                    "pqc_recommended_change_action": file_report.pqc_recommended_change_action,
                    "pqc_categories": file_report.pqc_summary_by_category,
                    "notes": file_report.notes[:2],
                }
            )
    return items[:10]



def _pqc_file_context_summary(report: ScanReport) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for file_report in report.file_reports:
        if not file_report.pqc_findings:
            continue
        context = file_report.classification.context
        counts[context] = counts.get(context, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _pqc_complexity_distribution(report: ScanReport) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for file_report in report.file_reports:
        if not file_report.pqc_complexity:
            continue
        rating = file_report.pqc_complexity.rating
        counts[rating] = counts.get(rating, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _pqc_recommended_change_action_summary(report: ScanReport) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for file_report in report.file_reports:
        action = file_report.pqc_recommended_change_action
        if not action:
            continue
        counts[action] = counts.get(action, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _recommended_actions_summary(report: ScanReport) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for file_report in report.file_reports:
        actions = []
        if file_report.ownership and file_report.ownership.recommended_change_action:
            actions.append(file_report.ownership.recommended_change_action)
        if file_report.pqc_recommended_change_action:
            actions.append(file_report.pqc_recommended_change_action)
        for action in actions:
            counts[action] = counts.get(action, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _cbom_ecosystem_summary(report: ScanReport) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for component in report.cbom_components:
        ecosystem = component.ecosystem or "unknown"
        counts[ecosystem] = counts.get(ecosystem, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _top_ecosystems(report: ScanReport) -> List[str]:
    return [name for name, _ in list(_cbom_ecosystem_summary(report).items())[:4]]


def _combined_severity_score(file_report) -> float:
    score = 0.0
    if file_report.complexity:
        score += file_report.complexity.score
    if file_report.pqc_complexity:
        score += file_report.pqc_complexity.score * 1.25
    score += len(file_report.pqc_findings) * 1.5
    score += len(file_report.pii_matches) * 0.5
    if file_report.pqc_likely_change_target:
        score += 8.0
    if file_report.ownership and file_report.ownership.likely_change_target:
        score += 5.0
    return score


def _looks_usable(summary_text: str) -> bool:
    normalized = summary_text.strip()
    if not normalized:
        return False
    if not all(heading in normalized for heading in REQUIRED_HEADINGS):
        return False
    if normalized.count("`") < 10:
        return False
    if normalized.count("- ") < 10:
        return False
    return True
