from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .dependency_explanations import dependency_meaning, dependency_why_it_matters
from .models import (
    AiDependencyGuidance,
    AiFileRecommendation,
    AiRecommendations,
    AiWorkPackage,
    ScanReport,
)
from .ollama_client import DEFAULT_OLLAMA_URL, call_ollama_text

PROMPT_VERSION = "phase3-rec-v2"


def generate_ai_recommendations(
    report: ScanReport,
    provider: str,
    model: str,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout_seconds: int = 60,
) -> AiRecommendations:
    provider_name = provider.strip().lower()
    if provider_name != "ollama":
        raise ValueError(f"Unsupported LLM provider: {provider}")

    fallback = _build_deterministic_recommendations(report, provider="ollama", model=model)
    payload = _build_payload(report, fallback)
    system_prompt, user_prompt = _build_prompt(payload)
    try:
        response_text = call_ollama_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            url=ollama_url,
            timeout_seconds=timeout_seconds,
            num_predict=800,
        )
    except RuntimeError as exc:
        fallback.summary_markdown = (
            fallback.summary_markdown
            + "\n- AI model advisory enhancement was unavailable for this run, so these recommendations use the deterministic fallback only."
            + f" Failure detail: `{str(exc).strip()}`."
        )
        return fallback
    parsed = _parse_model_response(response_text)
    if not parsed:
        fallback.summary_markdown = (
            fallback.summary_markdown
            + "\n- AI model advisory enhancement returned an unusable response, so these recommendations use the deterministic fallback only."
        )
        return fallback
    return _merge_with_fallback(parsed, fallback)


def write_ai_recommendations_markdown(recommendations: AiRecommendations, output_path: Path) -> None:
    front_matter = [
        "# AI Recommendation Advisory",
        "",
        f"- Provider: `{recommendations.provider}`",
        f"- Model: `{recommendations.model}`",
        f"- Prompt version: `{recommendations.prompt_version}`",
        f"- Generated at (UTC): `{recommendations.generated_at_utc}`",
        f"- Advisory only: `{str(recommendations.advisory_only).lower()}`",
        "",
    ]
    body_lines: List[str] = [recommendations.summary_markdown.strip(), "", "## Top File Recommendations"]
    for item in recommendations.file_recommendations:
        body_lines.append(f"- `{item.path}` [{item.priority}]: {item.recommendation} {item.rationale}")
    body_lines.append("")
    body_lines.append("## Work Packages")
    for package in recommendations.work_packages:
        body_lines.append(f"- `{package.name}`: {package.rationale}")
    body_lines.append("")
    body_lines.append("## Dependency Guidance")
    for item in recommendations.dependency_guidance:
        body_lines.append(f"- `{item.name}`: {item.meaning} {item.why_it_matters}")
    output_path.write_text("\n".join(front_matter + body_lines).rstrip() + "\n", encoding="utf-8")


def _build_payload(report: ScanReport, fallback: AiRecommendations) -> Dict[str, Any]:
    return {
        "root_path": report.root_path,
        "scan_domains": report.scan_domains,
        "files_scanned": report.files_scanned,
        "files_with_pqc": report.files_with_pqc,
        "total_pqc_findings": report.total_pqc_findings,
        "pqc_totals_by_category": report.pqc_totals_by_category,
        "pqc_migration_class_totals": report.pqc_migration_class_totals,
        "top_files": [
            {
                "path": item.path,
                "context": item.classification.context,
                "layer": item.classification.layer,
                "pqc_categories": item.pqc_summary_by_category,
                "recommended_action": item.pqc_recommended_change_action,
                "likely_change_target": item.pqc_likely_change_target,
                "complexity": item.pqc_complexity.rating if item.pqc_complexity else "",
                "dependencies": sorted({dep.name for dep in item.dependency_references if dep.related_categories})[:4],
                "notes": item.notes[:2],
            }
            for item in _ranked_pqc_files(report)[:5]
        ],
        "dependency_guidance_seed": [
            {
                "name": item.name,
                "meaning": item.meaning,
                "why_it_matters": item.why_it_matters,
            }
            for item in fallback.dependency_guidance[:5]
        ],
        "deterministic_fallback": {
            "summary_markdown": fallback.summary_markdown,
            "file_recommendations": [
                {
                    "path": item.path,
                    "priority": item.priority,
                    "recommendation": item.recommendation,
                    "rationale": item.rationale,
                }
                for item in fallback.file_recommendations[:5]
            ],
            "work_packages": [
                {
                    "name": item.name,
                    "rationale": item.rationale,
                    "related_categories": item.related_categories,
                    "target_paths": item.target_paths,
                }
                for item in fallback.work_packages[:5]
            ],
        },
    }


def _build_prompt(payload: Dict[str, Any]) -> tuple[str, str]:
    system_prompt = """
You are a cybersecurity migration advisor.
Use the provided structured scan facts to improve recommendation quality for a post-quantum migration report.
Do not invent findings, files, dependencies, or categories.
Keep recommendations grounded in the supplied data.
Keep the response concise and practical.
Return JSON only with these keys:
summary_markdown, file_recommendations, work_packages, dependency_guidance.
""".strip()
    user_prompt = (
        "Facts:\n```json\n"
        + json.dumps(payload, separators=(",", ":"))
        + "\n```\n\n"
        + "Requirements:\n"
        + "- Each file_recommendations item must contain: path, priority, recommendation, rationale.\n"
        + "- Each work_packages item must contain: name, rationale, related_categories, target_paths.\n"
        + "- Each dependency_guidance item must contain: name, meaning, why_it_matters.\n"
        + "- Prefer at most 5 file_recommendations, 5 work_packages, and 8 dependency_guidance items.\n"
    )
    return system_prompt, user_prompt


def _build_deterministic_recommendations(report: ScanReport, provider: str, model: str) -> AiRecommendations:
    files = _build_file_recommendations(report)
    work_packages = _build_work_packages(report)
    dependency_guidance = _build_dependency_guidance(report)
    summary_lines = [
        "## Recommendation Overview",
        f"- Focus first on `{len([item for item in files if item.priority == 'high'])}` high-priority PQC change targets with explicit signing, certificate, protocol, or KMS/HSM impact.",
        f"- The dominant migration themes in this scan are {', '.join(f'`{key}`' for key, _ in list(sorted(report.pqc_totals_by_category.items(), key=lambda item: (-item[1], item[0])))[:4])}.",
        "- Use the suggested work packages to separate certificate lifecycle, application signing, protocol-stack, and dependency-driven remediation so review effort stays organized.",
    ]
    return AiRecommendations(
        provider=provider,
        model=model,
        summary_markdown="\n".join(summary_lines),
        file_recommendations=files,
        work_packages=work_packages,
        dependency_guidance=dependency_guidance,
        prompt_version=PROMPT_VERSION,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        advisory_only=True,
    )


def _build_file_recommendations(report: ScanReport) -> List[AiFileRecommendation]:
    recommendations: List[AiFileRecommendation] = []
    for file_report in _ranked_pqc_files(report)[:6]:
        priority = file_report.pqc_complexity.rating if file_report.pqc_complexity else "medium"
        categories = ", ".join(f"`{key}`" for key in list(sorted(file_report.pqc_summary_by_category.keys()))[:4]) or "`none`"
        dependencies = sorted({dep.name for dep in file_report.dependency_references if dep.related_categories})[:4]
        dependency_text = f" Key dependencies include {', '.join(f'`{name}`' for name in dependencies)}." if dependencies else ""
        recommendations.append(
            AiFileRecommendation(
                path=file_report.path,
                priority=priority,
                recommendation=f"Review `{file_report.pqc_recommended_change_action or 'needs_manual_review'}` for this file and confirm the true implementation boundary.",
                rationale=f"This file is ranked as `{priority}` complexity with PQC categories {categories}.{dependency_text}",
            )
        )
    return recommendations


def _build_work_packages(report: ScanReport) -> List[AiWorkPackage]:
    packages: List[AiWorkPackage] = []
    ranked_files = _ranked_pqc_files(report)
    category_to_package = [
        ("JWT_OR_TOKEN_SIGNING", "Application Signing", "Prioritize JWT and token-signing implementations, especially where asymmetric signing choices are explicit."),
        ("CERTIFICATE_USAGE", "Certificate Lifecycle", "Review certificate loading, keystore usage, trust chains, and mTLS dependencies that may drive PQC migration effort."),
        ("TLS_CONFIGURATION", "Protocol Stack", "Review TLS or mTLS configuration and protocol-edge changes that may need coordinated rollout planning."),
        ("SSH_USAGE", "SSH Review", "Review SSH clients, servers, and SSH key-management usage for post-quantum readiness."),
        ("KMS_OR_HSM_ASYMMETRIC", "KMS And HSM", "Review managed key and asymmetric key-provider dependencies for support and migration sequencing."),
        ("CODE_SIGNING", "Code Signing", "Review code-signing and signed-artifact workflows that may depend on certificate or PKCS/CMS processes."),
    ]
    for category, name, rationale in category_to_package:
        if not report.pqc_totals_by_category.get(category):
            continue
        target_paths = [file_report.path for file_report in ranked_files if category in file_report.pqc_summary_by_category][:4]
        packages.append(
            AiWorkPackage(
                name=name,
                rationale=rationale,
                related_categories=[category],
                target_paths=target_paths,
            )
        )
    return packages[:6]


def _build_dependency_guidance(report: ScanReport) -> List[AiDependencyGuidance]:
    items: List[AiDependencyGuidance] = []
    seen: set[str] = set()
    for component in report.cbom_components:
        if not component.related_categories:
            continue
        key = component.name.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(
            AiDependencyGuidance(
                name=component.name,
                meaning=dependency_meaning(component.name, component.ecosystem, component.related_categories),
                why_it_matters=dependency_why_it_matters(component.related_categories),
            )
        )
    return items[:10]


def _ranked_pqc_files(report: ScanReport):
    return sorted(
        [item for item in report.file_reports if item.pqc_findings],
        key=lambda item: (
            -(item.pqc_complexity.score if item.pqc_complexity else 0.0),
            -len(item.pqc_findings),
            item.path.lower(),
        ),
    )


def _parse_model_response(response_text: str) -> Dict[str, Any] | None:
    raw = response_text.strip()
    if not raw:
        return None
    candidates = [raw]
    if "```json" in raw:
        start = raw.find("```json") + len("```json")
        end = raw.find("```", start)
        if end != -1:
            candidates.insert(0, raw[start:end].strip())
    elif "```" in raw:
        start = raw.find("```") + 3
        end = raw.find("```", start)
        if end != -1:
            candidates.insert(0, raw[start:end].strip())
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and payload.get("summary_markdown"):
            return payload
    return None


def _merge_with_fallback(payload: Dict[str, Any], fallback: AiRecommendations) -> AiRecommendations:
    file_recommendations: List[AiFileRecommendation] = []
    for item in payload.get("file_recommendations", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        recommendation = str(item.get("recommendation", "")).strip()
        rationale = str(item.get("rationale", "")).strip()
        priority = str(item.get("priority", "medium")).strip().lower() or "medium"
        if path and recommendation and rationale:
            file_recommendations.append(AiFileRecommendation(path=path, priority=priority, recommendation=recommendation, rationale=rationale))
    work_packages: List[AiWorkPackage] = []
    for item in payload.get("work_packages", []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        rationale = str(item.get("rationale", "")).strip()
        related_categories = [str(value).strip() for value in item.get("related_categories", []) if str(value).strip()]
        target_paths = [str(value).strip() for value in item.get("target_paths", []) if str(value).strip()]
        if name and rationale:
            work_packages.append(AiWorkPackage(name=name, rationale=rationale, related_categories=related_categories, target_paths=target_paths))
    dependency_guidance: List[AiDependencyGuidance] = []
    for item in payload.get("dependency_guidance", []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        meaning = str(item.get("meaning", "")).strip()
        why_it_matters = str(item.get("why_it_matters", "")).strip()
        if name and meaning and why_it_matters:
            dependency_guidance.append(AiDependencyGuidance(name=name, meaning=meaning, why_it_matters=why_it_matters))
    return AiRecommendations(
        provider=fallback.provider,
        model=fallback.model,
        summary_markdown=str(payload.get("summary_markdown") or fallback.summary_markdown).strip(),
        file_recommendations=file_recommendations or fallback.file_recommendations,
        work_packages=work_packages or fallback.work_packages,
        dependency_guidance=dependency_guidance or fallback.dependency_guidance,
        prompt_version=PROMPT_VERSION,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        advisory_only=True,
    )
