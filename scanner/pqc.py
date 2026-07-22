from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from .models import ComplexityAssessment, PqcFinding


IMPORT_RE = re.compile(r"^\s*(import |from |using |const .*require\(|require\(|<dependency|implementation\s)")
COMMENT_RE = re.compile(r"^\s*(//|/\*|\*|#|--|<!--)")


@dataclass(frozen=True)
class PqcRule:
    category: str
    algorithm: str
    migration_class: str
    severity: str
    confidence: float
    pattern: re.Pattern[str]


PQC_RULES_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "pqc-rules.json"
DEFAULT_PQC_RULE_DEFINITIONS = [
    {
        "category": "ASYMMETRIC_ALGORITHM",
        "algorithm": "RSA",
        "migration_class": "CUSTOM_REFACTOR",
        "severity": "high",
        "confidence": 0.95,
        "pattern": r"\bRSA\b|RSAPrivateKey|RSAPublicKey|SHA(?:1|224|256|384|512)withRSA|KeyPairGenerator\.getInstance\(\"RSA\"\)|SignatureAlgorithm\.RS\d+|algorithm:\s*RSA\b|RSA\.Create\(|rsa\.GenerateKey\(|rsaEncryption",
    },
    {
        "category": "ASYMMETRIC_ALGORITHM",
        "algorithm": "ECC",
        "migration_class": "APPLICATION_SIGNING",
        "severity": "high",
        "confidence": 0.93,
        "pattern": r"\bECDSA\b|\bECDH\b|\bEC\b|ES(?:256|384|512)\b|SHA(?:224|256|384|512)withECDSA|KeyAgreement\.getInstance\(\"ECDH\"\)|ECDsa\.Create\(|elliptic\.P(?:256|384|521)\(|ecdh\.",
    },
    {
        "category": "CERTIFICATE_USAGE",
        "algorithm": "X.509/Keystore",
        "migration_class": "PKI_CERTIFICATE_LIFECYCLE",
        "severity": "medium",
        "confidence": 0.9,
        "pattern": r"X509Certificate|X509Certificate2|CertificateFactory|KeyStore|getCertificate\(|getKey\(|getEntry\(|load_cert_chain|KeyStore\.load\(|KeyStore\.getInstance\(\"(?:PKCS12|JKS|JCEKS)\"\)|TrustManagerFactory|\.p12\b|\.pfx\b|\.jks\b|\.jceks\b|\.pem\b|\.crt\b|\.cer\b|\.csr\b|pkcs12|truststore|keystore|cert-manager|certificate[A-Za-z0-9_]*|x509\.ParseCertificate|tls\.LoadX509KeyPair|BouncyCastleProvider|Security\.addProvider\(new\s+BouncyCastleProvider|org\.bouncycastle",
    },
    {
        "category": "TLS_CONFIGURATION",
        "algorithm": "TLS/mTLS",
        "migration_class": "PROTOCOL_STACK",
        "severity": "medium",
        "confidence": 0.9,
        "pattern": r"SSLContext|TrustManager|KeyManager|TLSv1(?:_2|_3)?|create_default_context|client-auth|ingress.*tls|kind:\s*Ingress\b|\bmtls\b|secretName:.*tls|ca-chain|minimum_version|tls\.Config|HttpClientHandler|ServerCertificateCustomValidationCallback|SslStream|tls\.LoadX509KeyPair",
    },
    {
        "category": "JWT_OR_TOKEN_SIGNING",
        "algorithm": "JWT asymmetric signing",
        "migration_class": "APPLICATION_SIGNING",
        "severity": "high",
        "confidence": 0.9,
        "pattern": r"Jwts\.builder|jsonwebtoken|jwt\.sign|JWT|JWS|RS256|ES256|PS256|SignatureAlgorithm\.(?:RS|ES|PS)\d+|JwtSecurityTokenHandler|RsaSecurityKey|TokenValidationParameters|golang-jwt|jwt\.NewWithClaims",
    },
    {
        "category": "SSH_USAGE",
        "algorithm": "SSH",
        "migration_class": "PROTOCOL_STACK",
        "severity": "medium",
        "confidence": 0.87,
        "pattern": r"ssh-rsa|known_hosts|authorized_keys|StrictHostKeyChecking|paramiko|JSch|SSHClient|SshClient|Renci\.SshNet|golang\.org/x/crypto/ssh|ssh\.ClientConfig|ssh\.ParsePrivateKey",
    },
    {
        "category": "KMS_OR_HSM_ASYMMETRIC",
        "algorithm": "KMS/HSM",
        "migration_class": "DEPENDENCY_DRIVEN",
        "severity": "high",
        "confidence": 0.85,
        "pattern": r"\bKmsClient\b|\bAWSKMS\b|AmazonKeyManagementServiceClient|AsymmetricSign|CloudKMS|KeyVault|ManagedHsm|KeyClient|CryptographyClient|Google\.Cloud\.Kms|cloud\.google\.com/go/kms|PKCS11|HSM|boto3\.client\([\'\"]kms|CipherTrust\.CADP|CADP_for_JAVA|IngrianProvider|NAESession|NAEKey|NAEPrivateKey|NAEPublicKey|SignVerifySpec|Azure\.Security\.KeyVault\.(?:Keys|Cryptography|Administration)|Amazon\.CloudHSM|CloudHSM|cloudhsm|cloudhsmv2|libcloudhsm_pkcs11|Cavium|CertList|CentralManagementProvider|RegisterClientParameters|CryptoDataUtility|com\.ingrian|com\.gemalto\.ps\.keysecure\.crypto|C_(?:Initialize|OpenSession|Login|SignInit|Sign|VerifyInit|Verify|GenerateKeyPair|FindObjectsInit|FindObjects)\b|CKM_(?:RSA_PKCS|ECDSA)|CKO_PRIVATE_KEY|managedhsm\.azure\.net",
    },
    {
        "category": "CODE_SIGNING",
        "algorithm": "Artifact/code signing",
        "migration_class": "DEPENDENCY_DRIVEN",
        "severity": "high",
        "confidence": 0.85,
        "pattern": r"jarsigner|signtool|codesign|cosign|SignedCms|SignerInfo|SignedXml|XmlDsig|notarytool|gpg\s+--detach-sign",
    },
    {
        "category": "LEGACY_CRYPTO_HYGIENE",
        "algorithm": "SHA-1/MD5/weak key size",
        "migration_class": "DEPENDENCY_DRIVEN",
        "severity": "medium",
        "confidence": 0.84,
        "pattern": r"\bSHA-1\b|\bMD5\b|SHA1withRSA|md5WithRSAEncryption|size:\s*1024\b|rsa\.GenerateKey\([^\n]*1024",
    },
]


def _build_pqc_rules(rule_definitions: Sequence[dict]) -> List[PqcRule]:
    rules: List[PqcRule] = []
    for item in rule_definitions:
        if not isinstance(item, dict):
            continue
        try:
            category = str(item["category"]).strip()
            algorithm = str(item["algorithm"]).strip()
            migration_class = str(item["migration_class"]).strip()
            severity = str(item["severity"]).strip()
            confidence = float(item["confidence"])
            pattern_text = str(item["pattern"])
        except (KeyError, TypeError, ValueError):
            continue
        if not all([category, algorithm, migration_class, severity, pattern_text]):
            continue
        try:
            pattern = re.compile(pattern_text, re.IGNORECASE)
        except re.error:
            continue
        rules.append(
            PqcRule(
                category=category,
                algorithm=algorithm,
                migration_class=migration_class,
                severity=severity,
                confidence=confidence,
                pattern=pattern,
            )
        )
    return rules


def _load_pqc_rule_definitions() -> Sequence[dict]:
    try:
        raw = json.loads(PQC_RULES_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_PQC_RULE_DEFINITIONS

    if not isinstance(raw, dict):
        return DEFAULT_PQC_RULE_DEFINITIONS

    rules = raw.get("pqc_rules", [])
    if not isinstance(rules, list):
        return DEFAULT_PQC_RULE_DEFINITIONS

    return rules or DEFAULT_PQC_RULE_DEFINITIONS


PQC_RULES: Sequence[PqcRule] = tuple(
    _build_pqc_rules(_load_pqc_rule_definitions()) or _build_pqc_rules(DEFAULT_PQC_RULE_DEFINITIONS)
)


def detect_pqc_findings(path: Path, content: str, file_context: str) -> List[PqcFinding]:
    findings: List[PqcFinding] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for rule in PQC_RULES:
            if not rule.pattern.search(line):
                continue
            finding_kind = classify_pqc_finding_kind(file_context, line)
            migration_class = (
                "LOW_RELEVANCE_REFERENCE"
                if finding_kind in {"documentation", "reference_only", "test_example"}
                else rule.migration_class
            )
            findings.append(
                PqcFinding(
                    line_number=line_number,
                    category=rule.category,
                    algorithm=rule.algorithm,
                    matched_text=line.strip()[:200],
                    finding_kind=finding_kind,
                    migration_class=migration_class,
                    confidence=rule.confidence,
                    severity=rule.severity,
                )
            )
    return _dedupe_findings(findings)


def classify_pqc_finding_kind(file_context: str, line: str) -> str:
    if file_context == "docs":
        return "documentation"
    if file_context == "test":
        return "test_example"
    if file_context == "frontend":
        return "reference_only"
    if file_context == "infrastructure_config":
        return "configuration"
    stripped = line.strip()
    if not stripped:
        return "reference_only"
    if COMMENT_RE.match(stripped):
        return "reference_only"
    if IMPORT_RE.match(stripped):
        return "dependency"
    return "implementation"


def summarize_pqc_findings(findings: Sequence[PqcFinding]) -> tuple[dict[str, int], dict[str, int], list[str], int, int]:
    categories = Counter(finding.category for finding in findings)
    migration_classes = Counter(finding.migration_class for finding in findings)
    algorithms = sorted({finding.algorithm for finding in findings})
    implementation_findings = sum(
        1
        for finding in findings
        if finding.finding_kind in {"implementation", "configuration", "dependency"}
    )
    reference_findings = sum(
        1
        for finding in findings
        if finding.finding_kind in {"documentation", "reference_only", "test_example"}
    )
    return (
        dict(categories),
        dict(migration_classes),
        algorithms,
        implementation_findings,
        reference_findings,
    )


def assess_pqc_posture(
    file_context: str,
    findings: Sequence[PqcFinding],
) -> tuple[ComplexityAssessment, bool, str]:
    categories, migration_classes, algorithms, implementation_findings, reference_findings = summarize_pqc_findings(findings)
    score = 0.0
    rationale: List[str] = []

    score += implementation_findings * 3.0
    score += len(algorithms) * 2.0
    score += migration_classes.get("CUSTOM_REFACTOR", 0) * 4.0
    score += migration_classes.get("APPLICATION_SIGNING", 0) * 3.0
    score += migration_classes.get("APPLICATION_KEY_EXCHANGE", 0) * 3.0
    score += migration_classes.get("PKI_CERTIFICATE_LIFECYCLE", 0) * 2.0
    score += migration_classes.get("PROTOCOL_STACK", 0) * 2.0
    score += migration_classes.get("DEPENDENCY_DRIVEN", 0) * 1.5

    if file_context in {"backend", "batch_integration", "shared_library"}:
        score += 2.0
        rationale.append("Back-end or shared implementation paths usually drive more direct PQC remediation work.")
    if file_context == "infrastructure_config":
        score += 1.0
        rationale.append("Platform TLS and certificate configuration still requires migration planning even without code changes.")
    if file_context in {"docs", "test", "frontend"}:
        score -= 2.0
        rationale.append("Reference-only, test, and front-end mentions usually have lower direct migration ownership.")
    if reference_findings > implementation_findings:
        score -= 2.0
        rationale.append("Most findings look reference-oriented rather than true implementation ownership.")
    if categories.get("KMS_OR_HSM_ASYMMETRIC", 0):
        rationale.append("KMS/HSM asymmetric usage can shift remediation toward dependency, platform, and key-management work.")
    if categories.get("JWT_OR_TOKEN_SIGNING", 0):
        rationale.append("JWT or token-signing paths often require application-level signing changes and regression testing.")
    if categories.get("TLS_CONFIGURATION", 0) or categories.get("CERTIFICATE_USAGE", 0):
        rationale.append("TLS, certificate, and keystore usage usually affects PKI lifecycle and deployment coordination.")
    if categories.get("SSH_USAGE", 0):
        rationale.append("SSH usage may require protocol and key-management review for post-quantum readiness.")
    if categories.get("CODE_SIGNING", 0):
        rationale.append("Code-signing paths can affect release tooling, build systems, and trust chains during migration.")

    score = max(1.0, round(score, 1))
    if score >= 12:
        rating = "high"
    elif score >= 6:
        rating = "medium"
    else:
        rating = "low"

    likely_change_target = (
        rating in {"medium", "high"}
        and implementation_findings > 0
        and file_context in {"backend", "batch_integration", "shared_library", "infrastructure_config"}
    )
    recommended_change_action = determine_pqc_action(categories, migration_classes, likely_change_target, file_context)
    return ComplexityAssessment(score=score, rating=rating, rationale=rationale), likely_change_target, recommended_change_action


def determine_pqc_action(
    categories: dict[str, int],
    migration_classes: dict[str, int],
    likely_change_target: bool,
    file_context: str,
) -> str:
    if not likely_change_target:
        if file_context == "frontend":
            return "reference_only_frontend"
        return "reference_only_or_low_priority"

    if categories.get("JWT_OR_TOKEN_SIGNING", 0) or migration_classes.get("APPLICATION_SIGNING", 0):
        return "review_pqc_application_signing"
    if categories.get("TLS_CONFIGURATION", 0) or categories.get("SSH_USAGE", 0) or migration_classes.get("PROTOCOL_STACK", 0):
        return "review_pqc_protocol_stack"
    if categories.get("KMS_OR_HSM_ASYMMETRIC", 0) or migration_classes.get("DEPENDENCY_DRIVEN", 0):
        return "review_pqc_dependency_and_kms"
    if categories.get("CODE_SIGNING", 0):
        return "review_pqc_code_signing"
    if migration_classes.get("CUSTOM_REFACTOR", 0):
        return "review_pqc_custom_crypto"
    if migration_classes.get("PKI_CERTIFICATE_LIFECYCLE", 0):
        return "review_pqc_certificate_lifecycle"
    return "review_pqc_manual_assessment"


def _dedupe_findings(findings: Iterable[PqcFinding]) -> List[PqcFinding]:
    seen = set()
    ordered: List[PqcFinding] = []
    for finding in findings:
        key = (
            finding.line_number,
            finding.category,
            finding.algorithm,
            finding.finding_kind,
            finding.matched_text.lower(),
        )
        if key not in seen:
            seen.add(key)
            ordered.append(finding)
    return ordered
