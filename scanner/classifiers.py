from __future__ import annotations

from pathlib import Path
from collections import Counter
from typing import Dict, Iterable, Tuple

from .config import BACKEND_HINTS, DATA_ACCESS_HINTS, FRONTEND_HINTS
from .models import FileClassification


DOC_EXTENSIONS = {".md", ".txt", ".rst", ".adoc", ".pdf"}
CONFIG_EXTENSIONS = {".yaml", ".yml", ".json", ".xml", ".properties", ".conf", ".ini", ".csproj", ".mod"}
SCRIPT_EXTENSIONS = {".sh", ".ps1", ".bat"}
TEST_PATH_TOKENS = {"test", "tests", "spec", "specs", "__tests__"}
DOC_PATH_TOKENS = {"docs", "doc", "readme"}
INFRA_PATH_TOKENS = {"k8s", "helm", "ingress", "terraform", "ansible"}
MANIFEST_FILENAMES = {"package.json", "requirements.txt", "go.mod", "pom.xml", "cargo.toml", "cargo.lock", "composer.json", "composer.lock", "build.sbt"}


def _count_hits(content: str, patterns: Iterable[str]) -> int:
    lowered = content.lower()
    return sum(lowered.count(pattern.lower()) for pattern in patterns)


def _count_hits_breakdown(content: str, patterns: Iterable[str]) -> Dict[str, int]:
    lowered = content.lower()
    counts = Counter()
    for pattern in patterns:
        count = lowered.count(pattern.lower())
        if count:
            counts[pattern] += count
    return dict(counts)


def classify_file(path: Path, content: str) -> FileClassification:
    suffix = path.suffix.lower()
    lower_name = path.name.lower()
    frontend_score = 0
    backend_score = 0
    data_score = 0
    reasons = []

    if suffix in {".js", ".jsx", ".ts", ".tsx", ".html", ".htm"}:
        frontend_score += 2
        reasons.append(f"{suffix} extension is commonly used for front-end code")
    if suffix in {".java", ".kt", ".kts", ".cs", ".go", ".py", ".rb", ".rs", ".php", ".jsp", ".scala", ".c", ".cc", ".cpp", ".h", ".hpp"}:
        backend_score += 2
        reasons.append(f"{suffix} extension is commonly used for back-end code")
    if suffix in {".sql", ".properties", ".xml", ".csproj", ".mod", ".conf", ".ini", ".toml", ".sbt"} or lower_name in MANIFEST_FILENAMES:
        data_score += 2
        reasons.append(f"{path.name} looks like configuration, manifest, or data-access metadata")

    frontend_hits = sum(_count_hits(content, values) for values in FRONTEND_HINTS.values())
    backend_hits = sum(_count_hits(content, values) for values in BACKEND_HINTS.values())
    data_hits = sum(_count_hits(content, values) for values in DATA_ACCESS_HINTS.values())
    frontend_score += frontend_hits
    backend_score += backend_hits
    data_score += data_hits

    if frontend_hits:
        reasons.append(f"Found {frontend_hits} front-end markers")
    if backend_hits:
        reasons.append(f"Found {backend_hits} back-end markers")
    if data_hits:
        reasons.append(f"Found {data_hits} data-access or integration markers")

    ranked = sorted(
        [
            ("frontend", frontend_score),
            ("backend", backend_score),
            ("data_access", data_score),
        ],
        key=lambda item: item[1],
        reverse=True,
    )

    top_label, top_score = ranked[0]
    second_score = ranked[1][1]
    if top_score == 0:
        layer = "unknown"
        confidence = 0.2
        reasons = ["No strong framework or layer markers found"]
    else:
        if top_label == "frontend" and data_score > 0:
            layer = "frontend_with_service_calls"
        elif top_label == "backend" and data_score > 0:
            layer = "backend_with_data_access"
        else:
            layer = top_label
        confidence = min(0.95, 0.5 + (top_score - second_score) * 0.08 + top_score * 0.02)

    context = classify_file_context(path, content, layer)
    return FileClassification(layer=layer, context=context, confidence=round(confidence, 2), reasons=reasons[:5])


def classify_file_context(path: Path, content: str, layer: str) -> str:
    suffix = path.suffix.lower()
    lower_name = path.name.lower()
    path_tokens = {part.lower() for part in path.parts}
    name_tokens = _split_name_tokens(path)

    if path_tokens & TEST_PATH_TOKENS or name_tokens & TEST_PATH_TOKENS:
        return "test"
    if path_tokens & DOC_PATH_TOKENS or suffix in DOC_EXTENSIONS or lower_name == "readme.md":
        return "docs"
    if path_tokens & INFRA_PATH_TOKENS or suffix in CONFIG_EXTENSIONS or lower_name in MANIFEST_FILENAMES:
        return "infrastructure_config"
    if suffix in SCRIPT_EXTENSIONS:
        return "batch_integration"
    if layer.startswith("frontend"):
        return "frontend"
    if layer in {"backend", "backend_with_data_access", "data_access"}:
        return "backend"
    if suffix in {".java", ".kt", ".kts", ".cs", ".go", ".py", ".rb", ".rs", ".php", ".scala", ".c", ".cc", ".cpp", ".h", ".hpp"}:
        return "shared_library"
    return "unknown"


def _split_name_tokens(path: Path) -> set[str]:
    stem = path.stem.lower().replace("-", "_")
    return {token for token in stem.split("_") if token}


def analyze_hint_breakdowns(content: str) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
    frontend_breakdown: Dict[str, int] = {}
    backend_breakdown: Dict[str, int] = {}
    data_breakdown: Dict[str, int] = {}

    for values in FRONTEND_HINTS.values():
        for pattern, count in _count_hits_breakdown(content, values).items():
            frontend_breakdown[pattern] = frontend_breakdown.get(pattern, 0) + count
    for values in BACKEND_HINTS.values():
        for pattern, count in _count_hits_breakdown(content, values).items():
            backend_breakdown[pattern] = backend_breakdown.get(pattern, 0) + count
    for values in DATA_ACCESS_HINTS.values():
        for pattern, count in _count_hits_breakdown(content, values).items():
            data_breakdown[pattern] = data_breakdown.get(pattern, 0) + count

    return frontend_breakdown, backend_breakdown, data_breakdown


def count_integration_markers(content: str) -> Tuple[int, int, int, int]:
    lowered = content.lower()
    rest_calls = sum(lowered.count(token) for token in ["fetch(", "axios", "resttemplate", "webclient", "httpclient", "requests.", "graphql", "apollo"])
    sql_count = sum(lowered.count(token) for token in ["select ", "insert ", "update ", "delete ", "preparedstatement", "jdbctemplate", "jdbc:"])
    endpoint_count = sum(lowered.count(token) for token in ["@getmapping", "@postmapping", "@requestmapping", "app.get(", "app.post(", "router.get(", "router.post("])
    jdbc_count = sum(lowered.count(token) for token in ["jdbctemplate", "drivermanager.getconnection", "datasource", "preparedstatement", "jdbc:", "resultset"])
    return rest_calls, sql_count, endpoint_count, jdbc_count
