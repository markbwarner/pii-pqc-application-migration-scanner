from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
from urllib.parse import urlparse

from .models import CbomComponent, DependencyReference, PqcFinding


PYTHON_IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z0-9_., ]+)")
PYTHON_FROM_RE = re.compile(r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+")
JS_REQUIRE_RE = re.compile(r"require\([\"\']([^\"\']+)[\"\']\)")
JS_IMPORT_RE = re.compile(r"from\s+[\"\']([^\"\']+)[\"\']|import\s+[\"\']([^\"\']+)[\"\']")
JS_FUNCTION_DECL_RE = re.compile(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_]*)\b")
JS_CLASS_DECL_RE = re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\b")
JS_CONST_FUNC_RE = re.compile(r"^\s*const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s+)?(?:function\b|\()")
JAVA_IMPORT_RE = re.compile(r"^\s*import\s+(?:static\s+)?([A-Za-z0-9_.*]+);")
JAVA_CLASS_DECL_RE = re.compile(
    r"^\s*(?:public\s+|protected\s+|private\s+|abstract\s+|final\s+|sealed\s+|non-sealed\s+)*"
    r"(?:class|interface|enum|record)\s+([A-Za-z_][A-Za-z0-9_]*)\b"
)
JAVA_ROUTE_LITERAL_RE = re.compile(r'"(/[A-Za-z0-9_./-]+)"')
PYTHON_DEF_RE = re.compile(r"^\s*(?:async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)\b")
PYTHON_CLASS_RE = re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\b")
CSHARP_USING_RE = re.compile(r"^\s*using\s+([A-Za-z0-9_.]+);")
CSHARP_CLASS_DECL_RE = re.compile(
    r"^\s*(?:public|internal|private|protected)\s+(?:sealed\s+|abstract\s+|partial\s+)*class\s+([A-Za-z_][A-Za-z0-9_]*)\b"
)
GO_IMPORT_BLOCK_RE = re.compile(r"import\s*\((.*?)\)", re.DOTALL)
GO_IMPORT_LINE_RE = re.compile(r"^\s*(?:[A-Za-z0-9_]+\s+)?\"([^\"]+)\"", re.MULTILINE)
GO_SINGLE_IMPORT_RE = re.compile(r"^\s*import\s+\"([^\"]+)\"", re.MULTILINE)
C_INCLUDE_RE = re.compile(r'^\s*#\s*include\s+[<"]([^>"]+)[>"]', re.MULTILINE)
C_FUNCTION_DECL_RE = re.compile(
    r"^\s*(?:static\s+)?(?:const\s+)?(?:unsigned\s+|signed\s+)?[A-Za-z_][A-Za-z0-9_\s\*]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*\{?"
)
C_ROUTE_LITERAL_RE = re.compile(r'"(/[A-Za-z0-9_./-]+)"')
SCRIPT_ROUTE_LITERAL_RE = re.compile(r'([/][A-Za-z0-9_./-]+)')
SCRIPT_HTTP_CALL_RE = re.compile(r"\b(curl|wget|invoke-restmethod|invoke-webrequest)\b", re.IGNORECASE)
SCRIPT_URL_RE = re.compile(r'https?://[^\s"\']+')
REQUIREMENTS_LINE_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)(?:\[.*?\])?(?:\s*[=<>!~]=\s*([^\s]+))?", re.MULTILINE)
GO_MOD_REQUIRE_RE = re.compile(r"^\s*([A-Za-z0-9./_-]+)\s+v([^\s]+)", re.MULTILINE)
RUBY_REQUIRE_RE = re.compile(r"^\s*require(?:_relative)?\s+[\"']([^\"']+)[\"']")
RUBY_GEMFILE_RE = re.compile(r"^\s*gem\s+[\"']([^\"']+)[\"'](?:\s*,\s*[\"']([^\"']+)[\"'])?")
RUBY_GEMSPEC_NAME_RE = re.compile(r"^\s*s\.name\s*=\s*[\"']([^\"']+)[\"']")
RUBY_GEMSPEC_DEP_RE = re.compile(r"^\s*s\.add(?:_runtime)?_dependency\s+[\"']([^\"']+)[\"'](?:\s*,\s*[\"']([^\"']+)[\"'])?")
RUBY_GEMFILE_LOCK_RE = re.compile(r"^\s{4}([A-Za-z0-9_.-]+) \(([^)]+)\)$", re.MULTILINE)
RUBY_CLASS_DECL_RE = re.compile(r"^\s*(?:class|module)\s+([A-Za-z_][A-Za-z0-9_:]*)\b", re.MULTILINE)
RUST_USE_RE = re.compile(r"^\s*use\s+([A-Za-z0-9_:\{\},\s]+);", re.MULTILINE)
RUST_EXTERN_CRATE_RE = re.compile(r"^\s*extern\s+crate\s+([A-Za-z0-9_]+);", re.MULTILINE)
RUST_CARGO_DEP_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*=\s*(?:\{[^}]*version\s*=\s*\"([^\"]+)\"[^}]*\}|\"([^\"]+)\")", re.MULTILINE)
RUST_CARGO_LOCK_PACKAGE_RE = re.compile(r"\[\[package\]\]\s+name\s*=\s*\"([^\"]+)\"\s+version\s*=\s*\"([^\"]+)\"", re.MULTILINE)
RUST_STRUCT_DECL_RE = re.compile(r"^\s*(?:pub\s+)?(?:struct|enum|trait)\s+([A-Za-z_][A-Za-z0-9_]*)\b", re.MULTILINE)
RUST_FN_DECL_RE = re.compile(r"^\s*(?:pub\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\b", re.MULTILINE)
PHP_USE_RE = re.compile(r"^\s*use\s+([A-Za-z0-9_\\]+)", re.MULTILINE)
SCALA_IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z0-9_.*{}\s,]+)", re.MULTILINE)
SBT_DEP_RE = re.compile(r'"([^"]+)"\s*%%?\s*"([^"]+)"\s*%\s*"([^"]+)"')
PHP_CLASS_DECL_RE = re.compile(r"^\s*(?:final\s+|abstract\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)\b", re.MULTILINE)
SCALA_CLASS_DECL_RE = re.compile(r"^\s*(?:final\s+)?(?:class|object|trait)\s+([A-Za-z_][A-Za-z0-9_]*)\b", re.MULTILINE)
DEPENDENCY_HINTS_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "dependency-hints.json"
DEFAULT_CRYPTO_PACKAGE_HINTS: Dict[str, List[str]] = {
    "JWT_OR_TOKEN_SIGNING": [
        "jsonwebtoken",
        "jjwt",
        "jose",
        "System.IdentityModel.Tokens.Jwt",
        "Microsoft.IdentityModel",
        "golang-jwt",
        "firebase/php-jwt",
    ],
    "SSH_USAGE": [
        "paramiko",
        "ssh2",
        "SSH.NET",
        "Renci.SshNet",
        "golang.org/x/crypto/ssh",
        "jsch",
        "apache-sshd",
        "phpseclib",
    ],
    "KMS_OR_HSM_ASYMMETRIC": [
        "@aws-sdk/client-kms",
        "boto3",
        "botocore",
        "AWSKMS",
        "Amazon.KeyManagementService",
        "Amazon.CloudHSM",
        "cloudhsm",
        "cloudhsmv2",
        "cloudhsm_pkcs11",
        "libcloudhsm_pkcs11",
        "cavium",
        "Azure.Security.KeyVault.Keys",
        "Azure.Security.KeyVault.Cryptography",
        "Azure.Security.KeyVault.Administration",
        "ManagedHsm",
        "managedhsm",
        "Google.Cloud.Kms",
        "cloud.google.com/go/kms",
        "pkcs11",
        "hsm",
        "CipherTrust.CADP.NETCore",
        "CADP_for_JAVA",
        "io.github.thalescpl-io.cadp",
        "com.ingrian",
        "IngrianProvider",
        "NAESession",
        "NAEKey",
        "NAEPrivateKey",
        "NAEPublicKey",
        "com.gemalto.ps.keysecure.crypto",
        "com.centralmanagement",
        "ciphertrust",
        "cadp",
        "keysecure",
    ],
    "CODE_SIGNING": [
        "signtool",
        "codesign",
        "cosign",
        "SignedCms",
        "System.Security.Cryptography.Pkcs",
        "jarsigner",
        "gpg",
        "BouncyCastle",
        "org.bouncycastle",
        "bcprov",
        "bcpkix",
        "NAEPrivateKey",
        "NAEPublicKey",
        "SignVerifySpec",
        "CMSSign",
    ],
    "CERTIFICATE_USAGE": [
        "cryptography",
        "pyOpenSSL",
        "openssl",
        "x509",
        "KeyStore",
        "org.bouncycastle",
        "bcprov",
        "bcpkix",
        "BouncyCastleProvider",
        "PKCS12",
        "JKS",
        "JCEKS",
        "CertList",
    ],
}


def _load_crypto_package_hints() -> Dict[str, List[str]]:
    try:
        raw = json.loads(DEPENDENCY_HINTS_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CRYPTO_PACKAGE_HINTS

    if not isinstance(raw, dict):
        return DEFAULT_CRYPTO_PACKAGE_HINTS

    hints_raw = raw.get("crypto_package_hints", {})
    if not isinstance(hints_raw, dict):
        return DEFAULT_CRYPTO_PACKAGE_HINTS

    parsed: Dict[str, List[str]] = {}
    for category, hints in hints_raw.items():
        if not isinstance(category, str) or not isinstance(hints, list):
            continue
        cleaned = [str(hint).strip() for hint in hints if str(hint).strip()]
        if cleaned:
            parsed[category.strip()] = cleaned

    return parsed or DEFAULT_CRYPTO_PACKAGE_HINTS


CRYPTO_PACKAGE_HINTS = _load_crypto_package_hints()


def extract_dependency_references(path: Path, content: str) -> List[DependencyReference]:
    lower_name = path.name.lower()
    suffix = path.suffix.lower()

    if lower_name == "package.json":
        return _parse_package_json(path, content)
    if lower_name == "requirements.txt":
        return _parse_requirements(path, content)
    if lower_name == "composer.json":
        return _parse_composer_json(path, content)
    if lower_name == "composer.lock":
        return _parse_composer_lock(path, content)
    if lower_name == "build.sbt":
        return _parse_build_sbt(path, content)
    if lower_name == "pom.xml":
        return _parse_pom_xml(path, content)
    if lower_name == "gemfile":
        return _parse_gemfile(path, content)
    if lower_name == "gemfile.lock":
        return _parse_gemfile_lock(path, content)
    if lower_name == "cargo.toml":
        return _parse_cargo_toml(path, content)
    if lower_name == "cargo.lock":
        return _parse_cargo_lock(path, content)
    if suffix == ".gemspec":
        return _parse_gemspec(path, content)
    if suffix == ".csproj":
        return _parse_csproj(path, content)
    if lower_name == "go.mod" or suffix == ".mod":
        return _parse_go_mod(path, content)

    if suffix == ".py":
        return _parse_python_imports(path, content)
    if suffix == ".rb":
        return _parse_ruby_requires(path, content)
    if suffix == ".php":
        return _parse_php_uses(path, content)
    if suffix == ".rs":
        return _parse_rust_uses(path, content)
    if suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return _parse_js_imports(path, content)
    if suffix in {".java", ".kt", ".kts"}:
        return _parse_java_imports(path, content)
    if suffix == ".scala":
        return _parse_scala_imports(path, content)
    if suffix == ".cs":
        return _parse_csharp_usings(path, content)
    if suffix == ".go":
        return _parse_go_imports(path, content)
    if suffix in {".c", ".h", ".hpp", ".cpp", ".cc"}:
        return _parse_c_includes(path, content)
    if suffix in {".sh", ".ps1", ".bat"}:
        return _parse_script_calls(path, content)
    return []


def dependency_refs_to_pqc_findings(
    dependency_references: Sequence[DependencyReference],
    file_context: str,
) -> List[PqcFinding]:
    findings: List[PqcFinding] = []
    for reference in dependency_references:
        for category in reference.related_categories:
            algorithm = _algorithm_label_for_category(category, reference.name)
            migration_class = _migration_class_for_category(category)
            finding_kind = "dependency" if reference.reference_type == "manifest" else "dependency"
            severity = "medium"
            confidence = 0.83 if reference.reference_type == "manifest" else 0.77
            if category in {"JWT_OR_TOKEN_SIGNING", "CODE_SIGNING", "KMS_OR_HSM_ASYMMETRIC"}:
                severity = "high"
            if file_context == "frontend" and category not in {"JWT_OR_TOKEN_SIGNING"}:
                migration_class = "LOW_RELEVANCE_REFERENCE"
                finding_kind = "reference_only"
            findings.append(
                PqcFinding(
                    line_number=reference.line_number,
                    category=category,
                    algorithm=algorithm,
                    matched_text=reference.name + (f" {reference.version}" if reference.version else ""),
                    finding_kind=finding_kind,
                    migration_class=migration_class,
                    confidence=confidence,
                    severity=severity,
                )
            )
    return _dedupe_pqc_findings(findings)


def aggregate_dependency_summary(file_reports) -> tuple[int, dict[str, int]]:
    package_counts: Counter[str] = Counter()
    fallback_counts: Counter[str] = Counter()
    total = 0
    for file_report in file_reports:
        for reference in file_report.dependency_references:
            total += 1
            fallback_counts[reference.name] += 1
            if reference.related_categories:
                package_counts[reference.name] += 1
    selected_counts = package_counts or fallback_counts
    return total, dict(sorted(selected_counts.items(), key=lambda item: (-item[1], item[0]))[:50])


def build_cbom_components(
    file_reports,
    imported_components: Sequence[CbomComponent] | None = None,
) -> List[CbomComponent]:
    by_key: Dict[tuple[str, str, str], CbomComponent] = {}
    for file_report in file_reports:
        for reference in file_report.dependency_references:
            key = (reference.ecosystem, reference.name, reference.version)
            entry = by_key.setdefault(
                key,
                CbomComponent(
                    name=reference.name,
                    ecosystem=reference.ecosystem,
                    version=reference.version,
                    component_type="library",
                    source_files=[],
                    related_categories=[],
                    origin="observed",
                ),
            )
            if file_report.path not in entry.source_files:
                entry.source_files.append(file_report.path)
            for category in reference.related_categories:
                if category not in entry.related_categories:
                    entry.related_categories.append(category)

    for component in imported_components or []:
        key = (component.ecosystem, component.name, component.version)
        entry = by_key.setdefault(
            key,
            CbomComponent(
                name=component.name,
                ecosystem=component.ecosystem,
                version=component.version,
                component_type=component.component_type,
                source_files=list(component.source_files),
                related_categories=list(component.related_categories),
                origin="imported",
            ),
        )
        entry.origin = "observed+imported" if entry.origin == "observed" else entry.origin
        for source_file in component.source_files:
            if source_file not in entry.source_files:
                entry.source_files.append(source_file)
        for category in component.related_categories:
            if category not in entry.related_categories:
                entry.related_categories.append(category)

    components = list(by_key.values())
    components.sort(key=lambda item: (item.ecosystem, item.name.lower(), item.version))
    return components


def write_cbom_file(output_path: Path, report) -> None:
    payload = {
        "bomFormat": "thales-phase2-cbom",
        "specVersion": "1.0",
        "metadata": {
            "root_path": report.root_path,
            "scan_domains": report.scan_domains,
        },
        "components": [
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
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_cbom_file(input_path: Path) -> List[CbomComponent]:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("components"), list):
        return _parse_cbom_components(raw["components"])
    if isinstance(raw, list):
        return _parse_cbom_components(raw)
    return []


def _parse_cbom_components(items: Sequence[dict]) -> List[CbomComponent]:
    components: List[CbomComponent] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        ecosystem = str(item.get("ecosystem") or item.get("purl") or item.get("group") or "unknown")
        components.append(
            CbomComponent(
                name=name,
                ecosystem=ecosystem,
                version=str(item.get("version", "") or ""),
                component_type=str(item.get("type", "library") or "library"),
                source_files=list(item.get("source_files", [])),
                related_categories=list(item.get("related_categories", [])),
                origin="imported",
            )
        )
    return components


def _parse_package_json(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return references
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        entries = payload.get(section, {})
        if not isinstance(entries, dict):
            continue
        for name, version in entries.items():
            references.append(_build_reference(path, name, "npm", "manifest", str(version), 1))
    return references


def _parse_requirements(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = REQUIREMENTS_LINE_RE.match(stripped)
        if not match:
            continue
        references.append(_build_reference(path, match.group(1), "python", "manifest", match.group(2) or "", line_number))
    return references


def _parse_composer_json(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return references
    for section in ("require", "require-dev"):
        entries = payload.get(section, {})
        if not isinstance(entries, dict):
            continue
        for name, version in entries.items():
            if str(name).lower() == "php":
                continue
            references.append(_build_reference(path, str(name), "php", "manifest", str(version), 1))
    return references


def _parse_composer_lock(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return references
    for section in ("packages", "packages-dev"):
        entries = payload.get(section, [])
        if not isinstance(entries, list):
            continue
        for item in entries:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            version = str(item.get("version", "")).strip()
            if name:
                references.append(_build_reference(path, name, "php", "manifest", version, 1))
    return _dedupe_references(references)


def _parse_pom_xml(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return references
    for dependency in root.findall(".//{*}dependency"):
        group_id = dependency.findtext("{*}groupId", default="").strip()
        artifact_id = dependency.findtext("{*}artifactId", default="").strip()
        version = dependency.findtext("{*}version", default="").strip()
        name = ":".join(part for part in (group_id, artifact_id) if part)
        if name:
            references.append(_build_reference(path, name, "maven", "manifest", version, 1))
    return references


def _parse_csproj(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return references
    for package in root.findall(".//{*}PackageReference"):
        name = (package.attrib.get("Include") or package.attrib.get("Update") or "").strip()
        version = (package.attrib.get("Version") or package.findtext("{*}Version", default="")).strip()
        if name:
            references.append(_build_reference(path, name, ".net", "manifest", version, 1))
    return references


def _parse_go_mod(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    in_require_block = False
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_require_block = True
            continue
        if in_require_block and stripped == ")":
            in_require_block = False
            continue
        if stripped.startswith("require ") and not in_require_block:
            stripped = stripped[len("require "):]
            match = GO_MOD_REQUIRE_RE.match(stripped)
            if match:
                references.append(_build_reference(path, match.group(1), "go", "manifest", match.group(2), line_number))
            continue
        if in_require_block:
            match = GO_MOD_REQUIRE_RE.match(stripped)
            if match:
                references.append(_build_reference(path, match.group(1), "go", "manifest", match.group(2), line_number))
    return references


def _parse_build_sbt(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for match in SBT_DEP_RE.finditer(line):
            name = f"{match.group(1)}:{match.group(2)}"
            references.append(_build_reference(path, name, "scala", "manifest", match.group(3), line_number))
    return _dedupe_references(references)


def _parse_gemfile(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        match = RUBY_GEMFILE_RE.match(line)
        if match:
            references.append(_build_reference(path, match.group(1), "ruby", "manifest", match.group(2) or "", line_number))
    return references


def _parse_gemfile_lock(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for match in RUBY_GEMFILE_LOCK_RE.finditer(content):
        line_number = content[:match.start()].count("\n") + 1
        references.append(_build_reference(path, match.group(1), "ruby", "manifest", match.group(2), line_number))
    return _dedupe_references(references)


def _parse_gemspec(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        match = RUBY_GEMSPEC_NAME_RE.match(line)
        if match:
            references.append(_build_reference(path, match.group(1), "ruby", "manifest", "", line_number))
        match = RUBY_GEMSPEC_DEP_RE.match(line)
        if match:
            references.append(_build_reference(path, match.group(1), "ruby", "manifest", match.group(2) or "", line_number))
    return _dedupe_references(references)


def _parse_python_imports(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        match = PYTHON_IMPORT_RE.match(line)
        if match:
            for name in [part.strip().split(".")[0] for part in match.group(1).split(",") if part.strip()]:
                references.append(_build_reference(path, name, "python", "import", "", line_number))
        match = PYTHON_FROM_RE.match(line)
        if match:
            name = match.group(1).split(".")[0]
            references.append(_build_reference(path, name, "python", "import", "", line_number))
    references.extend(_parse_python_source_markers(path, content))
    return _dedupe_references(references)


def _parse_cargo_toml(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    active_section = ""
    allowed_sections = {"dependencies", "dev-dependencies", "build-dependencies", "workspace.dependencies"}
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            active_section = stripped.strip("[]").strip()
            continue
        if active_section not in allowed_sections:
            continue
        match = RUST_CARGO_DEP_RE.match(line)
        if not match:
            continue
        name = match.group(1)
        version = match.group(2) or match.group(3) or ""
        references.append(_build_reference(path, name, "rust", "manifest", version, line_number))
    return references


def _parse_cargo_lock(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for match in RUST_CARGO_LOCK_PACKAGE_RE.finditer(content):
        name = match.group(1)
        version = match.group(2)
        line_number = content[:match.start()].count("\n") + 1
        references.append(_build_reference(path, name, "rust", "manifest", version, line_number))
    return references


def _parse_rust_uses(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for match in RUST_USE_RE.finditer(content):
        clause = match.group(1)
        root_name = clause.split("::", 1)[0].strip().strip("{").strip()
        if not root_name or root_name in {"crate", "self", "super", "std", "core", "alloc"}:
            continue
        line_number = content[:match.start()].count("\n") + 1
        references.append(_build_reference(path, root_name, "rust", "import", "", line_number))
    for match in RUST_EXTERN_CRATE_RE.finditer(content):
        name = match.group(1)
        line_number = content[:match.start()].count("\n") + 1
        references.append(_build_reference(path, name, "rust", "import", "", line_number))
    references.extend(_parse_rust_source_markers(path, content))
    return _dedupe_references(references)


def _parse_rust_source_markers(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        for pattern in (RUST_STRUCT_DECL_RE, RUST_FN_DECL_RE):
            match = pattern.match(line)
            if match and _match_dependency_categories(match.group(1)):
                references.append(_build_reference(path, match.group(1), "rust", "source_marker", "", line_number))
        for route_match in JAVA_ROUTE_LITERAL_RE.finditer(line):
            route = route_match.group(1)
            if _match_dependency_categories(route):
                references.append(_build_reference(path, route, "rust", "route_marker", "", line_number))
        for url_match in SCRIPT_URL_RE.finditer(line):
            host = urlparse(url_match.group(0)).netloc
            if host and _match_dependency_categories(host):
                references.append(_build_reference(path, host, "rust", "url_marker", "", line_number))
    return references


def _parse_ruby_requires(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        match = RUBY_REQUIRE_RE.match(line)
        if match:
            name = match.group(1).split("/")[0]
            if name and name not in {"json", "date", "time", "spec_helper"}:
                references.append(_build_reference(path, name, "ruby", "import", "", line_number))
    references.extend(_parse_ruby_source_markers(path, content))
    return _dedupe_references(references)


def _parse_ruby_source_markers(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "=begin", "=end")):
            continue
        class_match = RUBY_CLASS_DECL_RE.match(line)
        if class_match and _match_dependency_categories(class_match.group(1)):
            references.append(_build_reference(path, class_match.group(1), "ruby", "source_marker", "", line_number))
        for route_match in JAVA_ROUTE_LITERAL_RE.finditer(line):
            route = route_match.group(1)
            if _match_dependency_categories(route):
                references.append(_build_reference(path, route, "ruby", "route_marker", "", line_number))
        for url_match in SCRIPT_URL_RE.finditer(line):
            host = urlparse(url_match.group(0)).netloc
            if host and _match_dependency_categories(host):
                references.append(_build_reference(path, host, "ruby", "url_marker", "", line_number))
    return references


def _parse_php_uses(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for match in PHP_USE_RE.finditer(content):
        name = match.group(1).strip().lstrip("\\")
        if name:
            line_number = content[:match.start()].count("\n") + 1
            references.append(_build_reference(path, name, "php", "import", "", line_number))
    return _dedupe_references(references)



def _parse_php_source_markers(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*", "#")):
            continue
        class_match = PHP_CLASS_DECL_RE.match(line)
        if class_match and _match_dependency_categories(class_match.group(1)):
            references.append(_build_reference(path, class_match.group(1), "php", "source_marker", "", line_number))
        for route_match in JAVA_ROUTE_LITERAL_RE.finditer(line):
            route = route_match.group(1)
            if _match_dependency_categories(route):
                references.append(_build_reference(path, route, "php", "route_marker", "", line_number))
        for url_match in SCRIPT_URL_RE.finditer(line):
            host = urlparse(url_match.group(0)).netloc
            if host and _match_dependency_categories(host):
                references.append(_build_reference(path, host, "php", "url_marker", "", line_number))
    return references


def _parse_js_imports(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for match in JS_REQUIRE_RE.finditer(line):
            references.append(_build_reference(path, match.group(1), "npm", "import", "", line_number))
        for match in JS_IMPORT_RE.finditer(line):
            name = match.group(1) or match.group(2)
            if name:
                references.append(_build_reference(path, name, "npm", "import", "", line_number))
    references.extend(_parse_js_source_markers(path, content))
    return _dedupe_references(references)


def _parse_java_imports(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        match = JAVA_IMPORT_RE.match(line)
        if match:
            references.append(_build_reference(path, match.group(1), "jvm", "import", "", line_number))
    references.extend(_parse_java_source_markers(path, content))
    return _dedupe_references(references)


def _parse_java_source_markers(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        class_match = JAVA_CLASS_DECL_RE.match(line)
        if class_match and _match_dependency_categories(class_match.group(1)):
            references.append(_build_reference(path, class_match.group(1), "jvm", "source_marker", "", line_number))
        for route_match in JAVA_ROUTE_LITERAL_RE.finditer(line):
            route = route_match.group(1)
            if _match_dependency_categories(route):
                references.append(_build_reference(path, route, "jvm", "route_marker", "", line_number))
    return references


def _parse_scala_imports(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for match in SCALA_IMPORT_RE.finditer(content):
        clause = match.group(1).strip()
        line_number = content[:match.start()].count("\n") + 1
        for part in [item.strip() for item in clause.split(",") if item.strip()]:
            if part.startswith("{") or part in {"scala", "java.lang"}:
                continue
            root = part.split("{", 1)[0].strip()
            if root.endswith("._"):
                root = root[:-2]
            if root:
                references.append(_build_reference(path, root, "scala", "import", "", line_number))
    references.extend(_parse_scala_source_markers(path, content))
    return _dedupe_references(references)


def _parse_scala_source_markers(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        class_match = SCALA_CLASS_DECL_RE.match(line)
        if class_match and _match_dependency_categories(class_match.group(1)):
            references.append(_build_reference(path, class_match.group(1), "scala", "source_marker", "", line_number))
        for route_match in JAVA_ROUTE_LITERAL_RE.finditer(line):
            route = route_match.group(1)
            if _match_dependency_categories(route):
                references.append(_build_reference(path, route, "scala", "route_marker", "", line_number))
        for url_match in SCRIPT_URL_RE.finditer(line):
            host = urlparse(url_match.group(0)).netloc
            if host and _match_dependency_categories(host):
                references.append(_build_reference(path, host, "scala", "url_marker", "", line_number))
    return references


def _parse_csharp_usings(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        match = CSHARP_USING_RE.match(line)
        if match:
            references.append(_build_reference(path, match.group(1), ".net", "import", "", line_number))
    references.extend(_parse_csharp_source_markers(path, content))
    return _dedupe_references(references)


def _parse_go_imports(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    block_match = GO_IMPORT_BLOCK_RE.search(content)
    if block_match:
        for import_match in GO_IMPORT_LINE_RE.finditer(block_match.group(1)):
            references.append(_build_reference(path, import_match.group(1), "go", "import", "", 1))
    for import_match in GO_SINGLE_IMPORT_RE.finditer(content):
        references.append(_build_reference(path, import_match.group(1), "go", "import", "", 1))
    return _dedupe_references(references)


def _parse_c_includes(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        match = C_INCLUDE_RE.match(line)
        if match:
            references.append(_build_reference(path, match.group(1), "native", "import", "", line_number))
    references.extend(_parse_c_source_markers(path, content))
    return _dedupe_references(references)


def _parse_js_source_markers(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        for pattern in (JS_FUNCTION_DECL_RE, JS_CLASS_DECL_RE, JS_CONST_FUNC_RE):
            match = pattern.match(line)
            if match and _match_dependency_categories(match.group(1)):
                references.append(_build_reference(path, match.group(1), "npm", "source_marker", "", line_number))
        for route_match in JAVA_ROUTE_LITERAL_RE.finditer(line):
            route = route_match.group(1)
            if _match_dependency_categories(route):
                references.append(_build_reference(path, route, "npm", "route_marker", "", line_number))
    return references


def _parse_python_source_markers(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for pattern in (PYTHON_CLASS_RE, PYTHON_DEF_RE):
            match = pattern.match(line)
            if match and _match_dependency_categories(match.group(1)):
                references.append(_build_reference(path, match.group(1), "python", "source_marker", "", line_number))
        for route_match in JAVA_ROUTE_LITERAL_RE.finditer(line):
            route = route_match.group(1)
            if _match_dependency_categories(route):
                references.append(_build_reference(path, route, "python", "route_marker", "", line_number))
    return references


def _parse_csharp_source_markers(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        class_match = CSHARP_CLASS_DECL_RE.match(line)
        if class_match and _match_dependency_categories(class_match.group(1)):
            references.append(_build_reference(path, class_match.group(1), ".net", "source_marker", "", line_number))
        for route_match in JAVA_ROUTE_LITERAL_RE.finditer(line):
            route = route_match.group(1)
            if _match_dependency_categories(route):
                references.append(_build_reference(path, route, ".net", "route_marker", "", line_number))
    return references


def _parse_c_source_markers(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        function_match = C_FUNCTION_DECL_RE.match(line)
        if function_match and _match_dependency_categories(function_match.group(1)):
            references.append(_build_reference(path, function_match.group(1), "native", "source_marker", "", line_number))
        for route_match in C_ROUTE_LITERAL_RE.finditer(line):
            route = route_match.group(1)
            if _match_dependency_categories(route):
                references.append(_build_reference(path, route, "native", "route_marker", "", line_number))
    return references


def _parse_script_calls(path: Path, content: str) -> List[DependencyReference]:
    references: List[DependencyReference] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "::", "REM ")):
            continue
        if not SCRIPT_HTTP_CALL_RE.search(line):
            continue
        line_without_urls = line
        for url_match in SCRIPT_URL_RE.finditer(line):
            url = url_match.group(0)
            route = urlparse(url).path or ""
            if route and _match_dependency_categories(route):
                references.append(_build_reference(path, route, "ops", "route_marker", "", line_number))
            line_without_urls = line_without_urls.replace(url, " ")
        for route_match in SCRIPT_ROUTE_LITERAL_RE.finditer(line_without_urls):
            route = _normalize_script_route(route_match.group(1))
            if route and _match_dependency_categories(route):
                references.append(_build_reference(path, route, "ops", "route_marker", "", line_number))
    return _dedupe_references(references)


def _normalize_script_route(route: str) -> str:
    normalized = (route or "").strip()
    if normalized.startswith("//"):
        parsed = urlparse(f"https:{normalized}")
        return parsed.path or ""
    return normalized


def _build_reference(
    path: Path,
    name: str,
    ecosystem: str,
    reference_type: str,
    version: str,
    line_number: int,
) -> DependencyReference:
    normalized_name = name.strip()
    related_categories = _match_dependency_categories(normalized_name)
    return DependencyReference(
        name=normalized_name,
        ecosystem=ecosystem,
        reference_type=reference_type,
        source=str(path),
        line_number=line_number,
        version=version.strip(),
        related_categories=related_categories,
    )


def _match_dependency_categories(name: str) -> List[str]:
    matches: List[str] = []
    lowered = name.lower()
    for category, hints in CRYPTO_PACKAGE_HINTS.items():
        for hint in hints:
            if hint.lower() in lowered:
                matches.append(category)
                break
    return matches


def _algorithm_label_for_category(category: str, name: str) -> str:
    mapping = {
        "JWT_OR_TOKEN_SIGNING": "JWT dependency",
        "SSH_USAGE": "SSH dependency",
        "KMS_OR_HSM_ASYMMETRIC": "KMS/HSM dependency",
        "CODE_SIGNING": "Code-signing dependency",
        "CERTIFICATE_USAGE": "Certificate dependency",
    }
    return mapping.get(category, name)


def _migration_class_for_category(category: str) -> str:
    mapping = {
        "JWT_OR_TOKEN_SIGNING": "APPLICATION_SIGNING",
        "SSH_USAGE": "PROTOCOL_STACK",
        "KMS_OR_HSM_ASYMMETRIC": "DEPENDENCY_DRIVEN",
        "CODE_SIGNING": "DEPENDENCY_DRIVEN",
        "CERTIFICATE_USAGE": "PKI_CERTIFICATE_LIFECYCLE",
    }
    return mapping.get(category, "DEPENDENCY_DRIVEN")


def _dedupe_references(references: Iterable[DependencyReference]) -> List[DependencyReference]:
    seen = set()
    ordered: List[DependencyReference] = []
    for reference in references:
        key = (reference.name, reference.ecosystem, reference.reference_type, reference.line_number)
        if key not in seen:
            seen.add(key)
            ordered.append(reference)
    return ordered


def _dedupe_pqc_findings(findings: Iterable[PqcFinding]) -> List[PqcFinding]:
    seen = set()
    ordered: List[PqcFinding] = []
    for finding in findings:
        key = (finding.line_number, finding.category, finding.algorithm, finding.matched_text)
        if key not in seen:
            seen.add(key)
            ordered.append(finding)
    return ordered
