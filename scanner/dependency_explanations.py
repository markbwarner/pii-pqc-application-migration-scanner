from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable


DEFAULT_EXACT_MEANINGS: dict[str, str] = {
    "system.security.cryptography.pkcs": ".NET library for PKCS/CMS message handling and certificate-based signing workflows.",
    "system.security.cryptography.x509certificates": ".NET certificate API for working with X.509 certificates, stores, and trust material.",
    "microsoft.identitymodel.tokens": ".NET token-security library commonly used for JWT validation and signing configuration.",
    "system.identitymodel.tokens.jwt": ".NET JWT library used for issuing, parsing, or validating JSON Web Tokens.",
    "azure.security.keyvault.keys": "Azure Key Vault client library for key-management operations, including asymmetric key usage.",
    "amazon.keymanagementservice": "AWS KMS client library for managed key operations, including asymmetric key usage.",
    "@aws-sdk/client-kms": "AWS SDK client for KMS operations, often used for encryption, signing, or asymmetric key management.",
    "boto3": "Python AWS SDK that can be used to call KMS and other managed security services.",
    "cloud.google.com/go/kms/apiv1": "Google Cloud KMS client library for managed key operations.",
    "google.cloud.kms": "Google Cloud KMS client library for managed key operations.",
    "golang.org/x/crypto": "Go cryptography extension module that includes SSH and other security-related packages.",
    "io.jsonwebtoken.jwts": "Java JJWT API entry point used to build or parse JWT tokens.",
    "io.jsonwebtoken.signaturealgorithm": "Java JJWT type used to select token-signing algorithms such as RSA or HMAC variants.",
    "jsonwebtoken": "JavaScript JWT library used to sign, verify, or decode tokens.",
    "jose": "JavaScript JOSE library used for JWT, JWS, or JWE operations.",
    "github.com/golang-jwt/jwt/v5": "Go JWT library used for token creation, signing, or validation.",
    "pyjwt": "Python JWT library used for token creation or validation.",
    "golang.org/x/crypto/ssh": "Go SSH library used for SSH client, server, or key-handling operations.",
    "paramiko": "Python SSH library used for remote access, automation, and SSH key handling.",
    "ssh2": "Node.js SSH library used for SSH connections and key-based remote operations.",
    "java.io.fileinputstream": "Java file input stream often used here to load keystores, certificates, or key material from disk.",
    "java.security.keystore": "Java keystore API used to load or manage certificate and key material.",
    "java.security.privatekey": "Java private-key interface used for signing or key-handling operations.",
    "java.security.signature": "Java signature engine API used to create or verify digital signatures.",
    "java.security.interfaces.rsaprivatekey": "Java RSA private-key interface that indicates explicit RSA key usage.",
    "java.security.interfaces.rsapublickey": "Java RSA public-key interface that indicates explicit RSA key usage.",
    "java.security.cert.x509certificate": "Java X.509 certificate API used to inspect or validate certificates.",
    "ssl": "Python standard TLS and SSL module used to configure secure connections, certificate validation, or mTLS behavior.",
    "cryptography": "Python cryptography library commonly used for certificates, keys, and cryptographic primitives.",
    "pyopenssl": "Python OpenSSL wrapper used for certificate and TLS operations.",
    "openssl": "Widely used cryptographic and TLS toolkit often associated with certificate and protocol handling.",
    "signedcms": ".NET API for CMS/PKCS signed-message handling, often tied to code-signing or signed payload workflows.",
}
DEFAULT_PARTIAL_MEANINGS: list[tuple[str, str]] = [
    ("x509", "Certificate-related API or library for working with X.509 certificates or trust chains."),
    ("rsa", "RSA-related API or key type that may indicate quantum-vulnerable asymmetric cryptography."),
    ("privatekey", "Private-key API used for signing or asymmetric key handling."),
    ("tls", "TLS-related API or library used for secure transport or mTLS configuration."),
    ("keystore", "Keystore-related API for loading or managing certificate and private-key material."),
    ("jwt", "JWT-related library or API used for token issuing, validation, or signing."),
    ("kms", "Key-management service client or dependency used for managed key operations."),
    ("ssh", "SSH-related library used for remote access, protocol handling, or SSH key operations."),
    ("pkcs", "PKCS or CMS-related API often associated with certificate-based signing or message protection."),
    ("cryptography", "Cryptography library that may support keys, certificates, or encryption primitives."),
    ("signature", "Signature-related API used to select, produce, or validate digital signatures."),
    ("keyvault", "Managed key-vault client used to access or operate on cryptographic keys."),
]
DEFAULT_CATEGORY_WHY: dict[str, str] = {
    "JWT_OR_TOKEN_SIGNING": "May indicate token-signing or token-validation logic that will need algorithm and key-strategy review for PQC migration.",
    "CERTIFICATE_USAGE": "May indicate certificate lifecycle, trust-chain, keystore, or mTLS work that needs post-quantum planning.",
    "TLS_CONFIGURATION": "May indicate TLS or mTLS configuration that could require coordinated protocol and certificate changes.",
    "SSH_USAGE": "May indicate SSH protocol or SSH key-management usage that should be reviewed for post-quantum readiness.",
    "KMS_OR_HSM_ASYMMETRIC": "May indicate managed key, KMS, or HSM usage that needs review for asymmetric key strategy and provider support.",
    "CODE_SIGNING": "May indicate code-signing or signed-artifact workflows that could require certificate and signing-process updates.",
    "ASYMMETRIC_ALGORITHM": "May indicate explicit asymmetric algorithm usage that should be reviewed for quantum-vulnerable key types or signing choices.",
}
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "dependency-explanations.json"


@lru_cache(maxsize=1)
def _load_glossary() -> tuple[dict[str, str], list[tuple[str, str]], dict[str, str]]:
    exact = dict(DEFAULT_EXACT_MEANINGS)
    partial = list(DEFAULT_PARTIAL_MEANINGS)
    category_why = dict(DEFAULT_CATEGORY_WHY)

    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return exact, partial, category_why

    if not isinstance(raw, dict):
        return exact, partial, category_why

    exact_raw = raw.get("exact_meanings", {})
    if isinstance(exact_raw, dict):
        exact = {
            str(key).strip().lower(): str(value).strip()
            for key, value in exact_raw.items()
            if str(key).strip() and str(value).strip()
        } or exact

    partial_raw = raw.get("partial_meanings", [])
    if isinstance(partial_raw, list):
        parsed_partial: list[tuple[str, str]] = []
        for item in partial_raw:
            if not isinstance(item, dict):
                continue
            match = str(item.get("match", "")).strip().lower()
            meaning = str(item.get("meaning", "")).strip()
            if match and meaning:
                parsed_partial.append((match, meaning))
        if parsed_partial:
            partial = parsed_partial

    category_raw = raw.get("category_why", {})
    if isinstance(category_raw, dict):
        parsed_category = {
            str(key).strip(): str(value).strip()
            for key, value in category_raw.items()
            if str(key).strip() and str(value).strip()
        }
        if parsed_category:
            category_why = parsed_category

    return exact, partial, category_why



def dependency_meaning(name: str, ecosystem: str = "", categories: Iterable[str] = ()) -> str:
    normalized = _normalize(name)
    exact_meanings, partial_meanings, _ = _load_glossary()
    if normalized in exact_meanings:
        return exact_meanings[normalized]

    for prefix, meaning in partial_meanings:
        if prefix in normalized:
            return meaning

    if ecosystem == ".net":
        return ".NET package or namespace observed in code or manifests."
    if ecosystem in {"jvm", "maven"}:
        return "Java or JVM package, class, or dependency observed in code or manifests."
    if ecosystem == "npm":
        return "Node.js or frontend package observed in code or manifests."
    if ecosystem == "python":
        return "Python package or module observed in code or manifests."
    if ecosystem == "php":
        return "PHP package, namespace, or Composer dependency observed in source files or manifests."
    if ecosystem == "ruby":
        return "Ruby gem, module, or package observed in code or manifests."
    if ecosystem == "scala":
        return "Scala package, import, or SBT dependency observed in source files or manifests."
    if ecosystem == "rust":
        return "Rust crate, module, or Cargo dependency observed in source files or manifests."
    if ecosystem == "go":
        return "Go package or module observed in code or manifests."
    if ecosystem == "native":
        return "Native C/C++ header or library reference observed in source code."
    if categories:
        return "Dependency or API associated with one or more crypto-relevant categories in this scan."
    return "Observed package, module, or API reference."



def dependency_why_it_matters(categories: Iterable[str]) -> str:
    _, _, category_why = _load_glossary()
    ordered = [category for category in categories if category in category_why]
    if not ordered:
        return "Included for traceability because it was observed in the scanned codebase or imported CBOM data."
    unique: list[str] = []
    for category in ordered:
        if category not in unique:
            unique.append(category)
    return " ".join(category_why[category] for category in unique[:2])



def _normalize(value: str) -> str:
    return value.strip().lower()
