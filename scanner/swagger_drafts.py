from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_SWAGGER_DRAFT_DIR = Path(__file__).resolve().parent.parent / "config" / "pqc" / "examples" / "customwrapper-example" / "swagger-drafts"
EXCLUDED_PATH_PARTS = (
    "/health",
    "/healthz",
    "/status",
    "/metrics",
    "/ready",
    "/readiness",
    "/live",
    "/liveness",
    "/ping",
    "/version",
    "/secrets/health",
)
SIGNAL_WORDS = (
    "protect",
    "reveal",
    "token",
    "tokenize",
    "detokenize",
    "encrypt",
    "decrypt",
    "sign",
    "verify",
    "mac",
    "sensitive",
    "crypto",
    "mask",
    "redact",
    "replace",
)


def generate_swagger_drafts(swagger_path: Path, output_dir: Path | None = None) -> list[Path]:
    payload = json.loads(swagger_path.read_text(encoding="utf-8"))
    draft_dir = (output_dir or DEFAULT_SWAGGER_DRAFT_DIR).resolve()
    draft_dir.mkdir(parents=True, exist_ok=True)

    title = str(((payload.get("info") or {}).get("title") or swagger_path.stem)).strip() or swagger_path.stem
    family_label = f"Custom {title}"
    base_name = _sanitize_file_stem(swagger_path.stem)

    included_paths, excluded_paths, operations = _extract_operations(payload)
    family_patterns = _build_family_patterns(included_paths, operations)
    explanations = _build_explanations(included_paths, operations)
    pqc_rule_candidates = _build_pqc_rule_candidates(included_paths, operations)

    outputs: list[Path] = []

    cbom_payload = {
        "vendor_families": [
            {
                "label": family_label,
                "patterns": family_patterns,
            }
        ],
        "fallback_label": "Other / General",
    }
    cbom_path = draft_dir / f"{base_name}_cbom-vendor-families.json"
    cbom_path.write_text(json.dumps(cbom_payload, indent=2) + "\n", encoding="utf-8")
    outputs.append(cbom_path)

    hints_payload = {
        "crypto_package_hints": {
            "KMS_OR_HSM_ASYMMETRIC": family_patterns
        }
    }
    hints_path = draft_dir / f"{base_name}_dependency-hints.json"
    hints_path.write_text(json.dumps(hints_payload, indent=2) + "\n", encoding="utf-8")
    outputs.append(hints_path)

    explanations_payload = {
        "exact_meanings": explanations,
        "partial_meanings": [],
        "category_why": {
            "KMS_OR_HSM_ASYMMETRIC": "Draft Swagger-derived service routes or request markers that may indicate managed protection, reveal, tokenization, or cryptographic service usage. Review before merging into live scanner config."
        },
    }
    explanations_path = draft_dir / f"{base_name}_dependency-explanations.json"
    explanations_path.write_text(json.dumps(explanations_payload, indent=2) + "\n", encoding="utf-8")
    outputs.append(explanations_path)

    pqc_payload = {
        "pqc_rules": pqc_rule_candidates
    }
    pqc_path = draft_dir / f"{base_name}_pqc-rules.json"
    pqc_path.write_text(json.dumps(pqc_payload, indent=2) + "\n", encoding="utf-8")
    outputs.append(pqc_path)

    review_path = draft_dir / f"{base_name}_review.md"
    review_path.write_text(_build_review_markdown(swagger_path, title, family_label, included_paths, excluded_paths, family_patterns, outputs), encoding="utf-8")
    outputs.append(review_path)

    return outputs


def _extract_operations(payload: dict[str, Any]) -> tuple[list[str], list[str], list[dict[str, str]]]:
    included_paths: list[str] = []
    excluded_paths: list[str] = []
    operations: list[dict[str, str]] = []
    paths = payload.get("paths", {})
    if not isinstance(paths, dict):
        return included_paths, excluded_paths, operations

    for raw_path, path_item in sorted(paths.items()):
        path_value = str(raw_path).strip()
        if not path_value:
            continue
        if _should_exclude_path(path_value):
            excluded_paths.append(path_value)
            continue
        included_paths.append(path_value)
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue
            summary = str(operation.get("summary", "")).strip()
            description = str(operation.get("description", "")).strip()
            operation_id = str(operation.get("operationId", "")).strip()
            operations.append({
                "path": path_value,
                "method": str(method).upper(),
                "summary": summary,
                "description": description,
                "operationId": operation_id,
            })
    return included_paths, excluded_paths, operations


def _build_family_patterns(paths: list[str], operations: list[dict[str, str]]) -> list[str]:
    patterns: list[str] = []
    for path in paths:
        patterns.append(path)
    for operation in operations:
        op_id = operation.get("operationId", "")
        summary = operation.get("summary", "")
        if _contains_signal(op_id):
            patterns.append(op_id)
        if _contains_signal(summary):
            patterns.append(_compact_identifier(summary))
    return _unique_non_empty(patterns)


def _build_explanations(paths: list[str], operations: list[dict[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for operation in operations:
        path = operation["path"].lower()
        summary = operation.get("summary") or "Swagger-discovered custom service endpoint."
        description = operation.get("description") or ""
        result[path] = _summarize_route(summary, description)
        operation_id = operation.get("operationId", "")
        if operation_id and _contains_signal(operation_id):
            result[operation_id.lower()] = _summarize_operation(operation_id, summary, description)
    return result


def _build_pqc_rule_candidates(paths: list[str], operations: list[dict[str, str]]) -> list[dict[str, Any]]:
    candidates = [path for path in paths if _contains_signal(path)]
    candidates.extend(operation["operationId"] for operation in operations if _contains_signal(operation.get("operationId", "")))
    candidates = _unique_non_empty(candidates)
    if not candidates:
        return []
    escaped = []
    for item in candidates:
        if item.startswith("/"):
            escaped.append(re.escape(item))
        else:
            escaped.append(re.escape(item).replace("_", "_"))
    return [
        {
            "category": "KMS_OR_HSM_ASYMMETRIC",
            "algorithm": "Swagger-discovered service route",
            "migration_class": "DEPENDENCY_DRIVEN",
            "severity": "medium",
            "confidence": 0.7,
            "pattern": "|".join(escaped),
            "draft_only": True,
        }
    ]


def _build_review_markdown(swagger_path: Path, title: str, family_label: str, included_paths: list[str], excluded_paths: list[str], family_patterns: list[str], outputs: list[Path]) -> str:
    lines = [
        "# Swagger Draft Review",
        "",
        f"Source file: `{swagger_path}`",
        f"Swagger title: `{title}`",
        f"Generated family label: `{family_label}`",
        "",
        "## Included Paths",
    ]
    if included_paths:
        lines.extend(f"- `{item}`" for item in included_paths)
    else:
        lines.append("- None")
    lines.extend(["", "## Excluded Paths"])
    if excluded_paths:
        lines.extend(f"- `{item}`" for item in excluded_paths)
    else:
        lines.append("- None")
    lines.extend(["", "## Draft Patterns"])
    if family_patterns:
        lines.extend(f"- `{item}`" for item in family_patterns)
    else:
        lines.append("- None")
    lines.extend(["", "## Generated Files"])
    lines.extend(f"- `{path.name}`" for path in outputs)
    lines.extend(["", "## Review Notes", "- These files are drafts only and were not merged into live config.", "- Health and status style routes were excluded automatically.", "- Review generic paths, operation IDs, and summaries before promoting any pattern into live scanner config.", ""])
    return "\n".join(lines)


def _should_exclude_path(path_value: str) -> bool:
    lowered = path_value.lower()
    return any(part in lowered for part in EXCLUDED_PATH_PARTS)


def _contains_signal(value: str) -> bool:
    lowered = str(value or "").lower()
    return any(word in lowered for word in SIGNAL_WORDS)


def _compact_identifier(value: str) -> str:
    compact = re.sub(r"[^A-Za-z0-9]+", "_", value.strip())
    return compact.strip("_")


def _sanitize_file_stem(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._-") or "swagger"


def _unique_non_empty(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in values:
        cleaned = str(item or "").strip()
        if not cleaned:
            continue
        if cleaned not in seen:
            seen.add(cleaned)
            ordered.append(cleaned)
    return ordered


def _summarize_route(summary: str, description: str) -> str:
    text = summary.strip() or description.strip() or "Swagger-discovered service endpoint."
    if description and description.strip() and description.strip() != summary.strip():
        text = f"{summary.strip() or 'Swagger-discovered service endpoint.'} {description.strip()}".strip()
    return " ".join(text.split())


def _summarize_operation(operation_id: str, summary: str, description: str) -> str:
    lead = summary.strip() or operation_id
    detail = description.strip()
    if detail:
        return " ".join(f"{lead} {detail}".split())
    return f"Swagger-discovered operation `{operation_id}` associated with the custom API surface."
