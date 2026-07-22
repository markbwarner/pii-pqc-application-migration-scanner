from __future__ import annotations

import json
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

CBOM_VENDOR_FAMILIES_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "cbom-vendor-families.json"
DEFAULT_CBOM_VENDOR_FALLBACK_LABEL = "Other / General"
DEFAULT_CBOM_VENDOR_FAMILY_PATTERNS: Sequence[Tuple[str, Sequence[str]]] = (
    ("Spring", ("spring",)),
    ("Microsoft Platform", ("microsoft.aspnetcore", "microsoft.data.sqlclient", "system.data.sqlclient", "system.net.http", "microsoft.identitymodel")),
    ("Java Persistence / SQL", ("jakarta.persistence", "javax.sql", "java.sql")),
    ("Go Standard Library", ("database/sql",)),
    ("Java Core IO", ("java.io.", "java.util.")),
    ("Thales Luna HSM", ("com.safenetinc.luna", "lunaprovider", "lunaslotmanager")),
    ("Oracle GoldenGate", ("goldengate", "thalesoracleggkeyproviderplugin")),
    ("Thales CM REST", ("com.thales.cm.rest.cmhelper", "ciphertrustmanagerhelper", "cmrestprotect", "cmrestsign", "cmrestmac", "/api/v1/crypto/", "/api/v1/vault/keys2/")),
    ("Thales CT-VL", ("vts/rest/v2.0/tokenize", "vts/rest/v2.0/detokenize", "tokengroup", "tokentemplate", "ff1_tok_group", "ff1_tok_template", "vts_ip_address", "vaultless tokenization", "ct-vl")),
    ("Generic KMIP", ("kmipsession", "kmipcipher", "kmipgcmkeyinformation", "kmipgcmspec", "kmipivspec", "kmipcryptoresult", "kmipkey", "kmipdata", "kmipresponse", "kmip.h", "libkmip", "kmipclient", "register_kmip", "locate_kmip", "get_kmip", "destroy_kmip", "kmip_open", "kmip_close")),
    ("Thales KMIP", ("naeclientcertificate",)),
    ("Thales CADP PKCS11", ("cadp_pkcs11.properties", "cadp/cadp.h", "ciphertrust_pkcs11_client", "ciphertrust_cadp_pkcs11", "thalescadppkcs11", "cadppkcs11", "cadp-pkcs11")),
    ("Thales CADP / CipherTrust", ("thales", "ciphertrust", "cadp", "ingrian", "keysecure", "ciphertrust.cadp.netcore", "cadp.netcore.crypto", "cadp.netcore.keymanagement", "cadp.netcore.sessions", "naesession", "naekeymanagement", "naersakey", "cadp_capi.h", "i_c_initialize", "i_c_opensession", "i_c_createcipherspec", "i_c_crypt_enhanced")),
    ("Vormetric", ("vormetric", "vpkcs11", "vorpkcs11", "pkcs11interop")),
    ("Voltage", ("voltage", "securedata", "dataprotection", "datamasking", "simpleapi")),
    ("Protegrity", ("protegrity", "applicationprotector", "developerjava", "protector", "appython")),
    ("AWS CloudHSM", ("cloudhsm", "cavium", "libcloudhsm", "cloudhsm_pkcs11", "amazon.cloudhsm")),
    ("AWS KMS", ("@aws-sdk/client-kms", "amazon.keymanagementservice", "awskms", "awskmsclientbuilder", "kmsclient")),
    ("AWS S3 Encryption", ("amazons3encryption", "kmsencryptionmaterialsprovider", "encryptionmaterials", "staticencryptionmaterialsprovider", "ssecustomerkey")),
    ("AWS Certificate Manager / PCA", ("awscertificatemanager", "describecertificaterequest", "exportcertificaterequest", "awspca", "issuecertificaterequest", "getcertificaterequest", "listcertificateauthoritiesrequest", "certificateauthorityarn")),
    ("AWS Secrets Manager", ("secretsmanager", "getsecretvaluerequest", "secretbinary", "secretstring")),
    ("AWS Encryption SDK", ("encryptionsdk", "awsencryptionsdk", "awcrypto", "kmsmasterkeyprovider", "materialproviders", "ikeyring", "createawskmskeyringinput", "createawskmsmultikeyringinput")),
    ("Oracle OCI KMS", ("com.oracle.bmc.keymanagement", "kmsmanagementclient", "kmscryptoclient", "oci-java-sdk-keymanagement")),
    ("Oracle Certificates / CA", ("certificatesmanagement", "certificatesclient", "createcertificateauthorityrequest", "createcertificaterequest", "getcertificateauthorityrequest", "getcabundlerequest", "getcertificateauthoritybundlerequest", "createcertificateauthoritydetails", "createcertificatedetails")),
    ("Oracle Secrets / Vault", ("vaultsclient", "createsecretrequest", "getsecretrequest", "createsecretdetails", "com.oracle.bmc.vault.model.secret")),
    ("Oracle PKI / Wallet", ("oraclewallet", "oraclesecretstore", "oraclepki", "osdt_core", "osdt_cert", "cwallet.sso", "ewallet.p12")),
    ("Azure Managed HSM", ("managedhsm", "azure.security.keyvault.administration", "managedhsm.azure.net")),
    ("Azure Key Vault", ("azure.security.keyvault", "com.microsoft.azure.keyvault", "keyvaultclient", "keyvaultconfiguration")),
    ("GCP Cloud HSM", ("com.google.cloud.kms.v1.protectionlevel", "com.google.cloud.kms.v1.cryptokeyversiontemplate", "protectionlevel", "cryptokeyversiontemplate")),
    ("HashiCorp Vault", ("github.com/hashicorp/vault/api", "hashicorp/vault/api", "node-vault", "hvac", "vault.logical", "vault.transit", "/v1/transit/encrypt/", "/v1/transit/decrypt/", "/v1/transit/sign/", "/v1/transit/verify/", "auth/approle/login")),
    ("Akeyless", ("akeyless", "io.akeyless", "io.akeyless.client", "akeyless-java", "akeyless-python", "akeyless-javascript", "akeyless-csharp-netcore", "github.com/akeylesslabs/akeyless-go", "api.akeyless.io", "provision-certificate", "verify-pkcs1", "upload-rsa", "update-ssh-cert-issuer", "create-dynamic-secret", "rotate-key")),
    ("GCP Cloud KMS", ("cloud.google.com/go/kms", "google.cloud.kms", "com.google.cloud.kms.v1.keymanagementserviceclient", "com.google.cloud.kms.v1.cryptokeyname", "keymanagementserviceclient")),
    ("Bouncy Castle", ("bouncycastle", "bcprov", "bcpkix", "bc-fips")),
    ("OpenSSL", ("openssl", "libssl", "libcrypto", "pyopenssl")),
    ("JWT / Identity", ("jsonwebtoken", "jjwt", "jose", "jwt", "oidc", "oauth")),
    ("SSH", ("ssh", "paramiko")),
    ("Certificate / PKI", ("x509", "certificate", "keystore", "truststore", "pkcs12", "pkcs7")),
    ("Language Runtime Crypto", ("system.security.cryptography", "java.security", "javax.crypto", "cryptography", "crypto")),
)

from .dependency_explanations import dependency_meaning, dependency_why_it_matters
from .models import FileReport, ScanReport


RATING_ORDER = {"low": 1, "medium": 2, "high": 3}

PQC_CATEGORY_DEFINITIONS: dict[str, tuple[str, str]] = {
    "PQC_CAPABLE_ALGORITHM": (
        "The file contains explicit post-quantum or hybrid algorithm names such as ML-KEM, ML-DSA, Kyber, Dilithium, Falcon, SLH-DSA, XMSS, or LMS.",
        "Treat this as a positive implementation signal. It means the file appears to reference PQC-capable primitives directly, but it does not prove the full vendor family or deployment path is already PQC-ready.",
    ),
    "ASYMMETRIC_ALGORITHM": (
        "Use of asymmetric algorithms such as RSA or ECC that often drive PQC migration planning.",
        "These algorithms may need replacement, hybrid support, or compatibility review as quantum-safe options are introduced.",
    ),
    "CERTIFICATE_USAGE": (
        "Certificate, keystore, truststore, or X.509 related handling.",
        "Certificates and PKI material often require lifecycle, issuance, trust-chain, and deployment planning during PQC migration.",
    ),
    "CODE_SIGNING": (
        "Code-signing or artifact-signing related usage.",
        "Signing workflows may need updated algorithms, signing services, verification tooling, and rollout coordination.",
    ),
    "JWT_OR_TOKEN_SIGNING": (
        "JWT, token-signing, or application-signing related logic.",
        "These findings usually point to application-level signing behavior that may require code changes and regression testing.",
    ),
    "KMS_OR_HSM_ASYMMETRIC": (
        "KMS, HSM, PKCS#11, or vendor crypto SDK usage tied to managed keys or asymmetric operations.",
        "These findings often indicate dependency-driven migration work with external key managers, HSMs, or crypto platforms.",
    ),
    "SSH_USAGE": (
        "SSH-related crypto or key-exchange usage.",
        "SSH stacks can require protocol and key algorithm review as PQC-capable options mature.",
    ),
    "TLS_CONFIGURATION": (
        "TLS, mTLS, SSL, trust, or protocol-stack configuration.",
        "Transport security settings may need coordinated protocol, certificate, and platform rollout planning.",
    ),
}

PQC_MIGRATION_CLASS_DEFINITIONS: dict[str, tuple[str, str]] = {
    "APPLICATION_KEY_EXCHANGE": (
        "Application-level key exchange logic is present.",
        "Usually indicates protocol or handshake logic that may need explicit PQC-aware redesign or hybrid support.",
    ),
    "APPLICATION_SIGNING": (
        "Application-controlled signing or token-signing behavior is present.",
        "Often requires direct code updates, algorithm replacement decisions, and compatibility testing.",
    ),
    "CUSTOM_REFACTOR": (
        "Custom cryptographic implementation or wrapper behavior is present.",
        "Custom crypto usually needs deeper review because migration is less likely to be solved by a simple library upgrade.",
    ),
    "DEPENDENCY_DRIVEN": (
        "Migration impact is strongly tied to libraries, SDKs, KMS, HSM, or platform dependencies.",
        "Often starts with inventory, vendor roadmap review, and dependency upgrade planning.",
    ),
    "LOW_RELEVANCE_REFERENCE": (
        "Reference-only mention with limited direct implementation ownership.",
        "Useful for awareness, but usually not a primary migration work item by itself.",
    ),
    "PKI_CERTIFICATE_LIFECYCLE": (
        "Certificate lifecycle or PKI management work is likely involved.",
        "May require changes to issuance, renewal, trust distribution, validation, or certificate operations.",
    ),
    "PROTOCOL_STACK": (
        "Protocol-stack or transport-layer migration work is indicated.",
        "Usually points to TLS, mTLS, SSH, or other coordinated edge and platform changes rather than only local code edits.",
    ),
}

PQC_RECOMMENDED_ACTION_DEFINITIONS: dict[str, tuple[str, str]] = {
    "reference_only_frontend": (
        "Front-end reference-only mention with low direct migration ownership.",
        "Treat as a pointer to likely backend, platform, or API owners rather than as the primary implementation target.",
    ),
    "reference_only_or_low_priority": (
        "Reference-only or low-priority item.",
        "Useful for context and inventory, but usually not a first-wave remediation target.",
    ),
    "review_pqc_application_signing": (
        "Review application signing or token-signing logic.",
        "Focus on JWTs, signatures, verification code paths, and compatibility testing.",
    ),
    "review_pqc_certificate_lifecycle": (
        "Review certificate lifecycle and PKI operations.",
        "Focus on issuance, truststores, certificate validation, and deployment coordination.",
    ),
    "review_pqc_code_signing": (
        "Review code-signing and artifact-signing workflows.",
        "Focus on build signing, release verification, and downstream trust consumers.",
    ),
    "review_pqc_custom_crypto": (
        "Review custom cryptographic wrappers or implementations.",
        "Focus on bespoke crypto logic that may need refactoring beyond simple dependency upgrades.",
    ),
    "review_pqc_dependency_and_kms": (
        "Review dependency, SDK, KMS, or HSM migration impact.",
        "Focus on vendor libraries, managed key services, hardware-backed crypto, and roadmap dependencies.",
    ),
    "review_pqc_manual_assessment": (
        "Manual architecture review is recommended.",
        "Use when the scanner sees impact signals but cannot confidently narrow the right remediation lane.",
    ),
    "review_pqc_protocol_stack": (
        "Review transport protocol stack and related edge configuration.",
        "Focus on TLS, mTLS, SSH, ingress, service-mesh, and certificate distribution concerns.",
    ),
}

PQC_FILE_CONTEXT_DEFINITIONS: dict[str, tuple[str, str]] = {
    "backend": (
        "Back-end implementation code or service logic.",
        "Usually the strongest signal for direct migration ownership and application change work.",
    ),
    "docs": (
        "Documentation or readme-style reference material.",
        "Useful for awareness and inventory, but often not the primary implementation target.",
    ),
    "frontend": (
        "Front-end or UI-oriented code.",
        "Often contains certificate or API references, but many PQC changes still land in backend or platform services.",
    ),
    "infrastructure_config": (
        "Infrastructure, deployment, or configuration material.",
        "Often important for TLS, mTLS, certificate rollout, or platform coordination work.",
    ),
    "test": (
        "Test, example, or validation code.",
        "Helpful for understanding usage patterns, though not always a direct production remediation owner.",
    ),
}


PQC_SIGNAL_STATUS_DEFINITIONS: dict[str, tuple[str, str, str]] = {
    "nist_current": (
        "NIST current / selected PQC signal",
        "File contains current or selected NIST-aligned PQC names such as ML-KEM, ML-DSA, SLH-DSA, FN-DSA, or HQC.",
        "Treat as the strongest positive PQC-capable signal in this report. It still does not prove the full product, deployment, or certificate path is end-to-end PQC-ready.",
    ),
    "approved_specialized": (
        "Approved specialized PQC signal",
        "File contains specialized approved hash-based signature names such as XMSS, XMSSMT, LMS, or HSS.",
        "These are meaningful PQC signals, but they usually indicate narrower or more specialized deployment patterns than the mainstream NIST migration set.",
    ),
    "alias_or_legacy_name": (
        "Alias / legacy PQC name",
        "File contains older or alias naming such as Kyber, Dilithium, Falcon, or SPHINCS+ that often maps to standardized NIST families.",
        "Useful as a positive PQC clue, but teams should confirm the exact standardized algorithm family and parameter set actually in use.",
    ),
    "experimental_or_watchlist": (
        "Experimental / watch-list PQC signal",
        "File contains PQC-related names such as FrodoKEM, Classic McEliece, BIKE, NTRU, or SABER.",
        "Treat as PQC-relevant and worth review, but not as the same maturity signal as the current NIST migration set.",
    ),
}

PQC_SIGNAL_STATUS_ORDER = {
    "nist_current": 4,
    "approved_specialized": 3,
    "alias_or_legacy_name": 2,
    "experimental_or_watchlist": 1,
}

PQC_SIGNAL_STATUS_PATTERNS: Sequence[tuple[str, tuple[str, ...]]] = (
    ("nist_current", ("ML-KEM", "MLKEM", "ML-DSA", "MLDSA", "SLH-DSA", "SLHDSA", "FN-DSA", "FNDSA", "HQC", "X25519MLKEM768", "SECP256R1MLKEM768")),
    ("approved_specialized", ("XMSSMT", "XMSS", "LMS", "HSS")),
    ("alias_or_legacy_name", ("KYBER", "DILITHIUM", "FALCON", "SPHINCS", "X25519KYBER768DRAFT00")),
    ("experimental_or_watchlist", ("FRODOKEM", "FRODO", "CLASSIC MCELIECE", "MCELIECE", "BIKE", "NTRU", "SABER")),
)

FRONTEND_PQC_IMPLEMENTATION_MARKERS = (
    "window.crypto",
    "crypto.subtle",
    "browsercrypto.subtle",
    "subtle.generatekey",
    "subtle.importkey",
    "subtle.derivebits",
    "subtle.derivekey",
    "subtle.encrypt",
    "subtle.decrypt",
    "subtle.sign",
    "subtle.verify",
    "subtle.wrapkey",
    "subtle.unwrapkey",
)


def write_html_report(report: ScanReport, output_path: Path) -> None:
    builder = _build_pii_html_report if set(report.scan_domains) == {"pii"} else _build_html_report
    output_path.write_text(builder(report), encoding="utf-8")


def _build_pii_html_report(report: ScanReport) -> str:
    title = "PII Migration Scanner Report"
    pii_file_reports = [file_report for file_report in report.file_reports if file_report.pii_matches]
    sections: List[str] = [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        f"<title>{escape(title)}</title>",
        "<style>",
        _css(),
        "</style>",
        "</head>",
        "<body>",
        "<main class=\"page\">",
        f"<h1>{escape(title)}</h1>",
        f"<p class=\"lede\">Root path: <code>{escape(report.root_path)}</code></p>",
        '<div class="panel markdown-panel"><p>This standalone PII report focuses on application-change planning for sensitive data handling. It intentionally omits PQC-only summary sections so the output stays centered on PII discovery, likely change ownership, JDBC substitution candidates, and migration work targeting.</p></div>',
        _render_pii_top_stats(report, pii_file_reports),
        _render_pii_metric_legend(report, pii_file_reports),
        _render_pii_planning_summary(report, pii_file_reports),
        _render_pii_tables_summary(report),
        _render_pii_file_report_table(pii_file_reports),
        "</main>",
        "</body>",
        "</html>",
    ]
    return "\n".join(sections) + "\n"


def _build_html_report(report: ScanReport) -> str:
    title = f"Migration Scanner Report - {', '.join(report.scan_domains).upper()}"
    glossary_path = (Path(__file__).resolve().parent.parent / "docs" / "pqc" / "pqc-report-metrics-and-glossary.md").resolve()
    sections: List[str] = [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        f"<title>{escape(title)}</title>",
        "<style>",
        _css(),
        "</style>",
        "</head>",
        "<body>",
        "<main class=\"page\">",
        f"<h1>{escape(title)}</h1>",
        f"<p class=\"lede\">Root path: <code>{escape(report.root_path)}</code></p>",
        f'<p class="lede">Reference glossary: <a href="{escape(glossary_path.as_posix())}">{escape(str(glossary_path))}</a></p>',
        _render_top_stats(report),
        _render_metric_legend(report),
        _render_dependency_summary(report),
    ]
    if report.ai_summary:
        sections.append(_render_ai_summary(report))
    if report.ai_recommendations:
        sections.append(_render_ai_recommendations(report))
    if "pii" in report.scan_domains:
        sections.append(_render_pii_summary(report))
    if "pqc" in report.scan_domains:
        sections.append(_render_pqc_summary(report))
    sections.append(_render_file_report_table(report.file_reports))
    sections.extend(["</main>", "</body>", "</html>"])
    return "\n".join(sections) + "\n"


def _render_top_stats(report: ScanReport) -> str:
    cards = [
        _stat_card("Scan domains", ", ".join(report.scan_domains)),
        _stat_card("Files scanned", str(report.files_scanned)),
        _stat_card("Files with findings", str(report.files_with_findings)),
        _stat_card("Dependency refs", str(report.dependency_reference_total)),
        _stat_card("CBOM components", str(len(report.cbom_components))),
    ]
    if report.imported_cbom_component_total:
        cards.append(_stat_card("Imported CBOM", str(report.imported_cbom_component_total)))
    if report.ai_summary:
        cards.append(_stat_card("AI summary", report.ai_summary.model))
    if report.ai_recommendations:
        cards.append(_stat_card("AI recommendations", report.ai_recommendations.model))
    if "pii" in report.scan_domains:
        cards.extend([
            _stat_card("Files with PII", str(report.files_with_pii)),
            _stat_card("Total PII matches", str(report.total_pii_matches)),
        ])
    if "pqc" in report.scan_domains:
        cards.extend([
            _stat_card("Files with PQC", str(report.files_with_pqc)),
            _stat_card("Total PQC findings", str(report.total_pqc_findings)),
            _stat_card("PQC change targets", str(report.pqc_likely_change_target_total)),
        ])
    return "<section><div class=\"stats\">" + "".join(cards) + "</div></section>"


def _render_metric_legend(report: ScanReport) -> str:
    actionable_actions = [
        file_report.pqc_recommended_change_action
        for file_report in report.file_reports
        if file_report.pqc_likely_change_target and file_report.pqc_recommended_change_action
    ]
    actionable_breakdown = _count_values(actionable_actions)
    reference_only_count = len([
        file_report for file_report in report.file_reports
        if file_report.pqc_findings and not file_report.pqc_likely_change_target
    ])
    cbom_ecosystems = _count_ecosystems(report)
    vendor_source_reference_counts = _count_vendor_source_reference_counts(report)
    cbom_rollup = " + ".join(f"{ecosystem} {count}" for ecosystem, count in cbom_ecosystems.items()) or "0"
    vendor_source_rollup = " + ".join(f"{family} {count}" for family, count in vendor_source_reference_counts.items()) or "0"
    dependency_ref_rollup = sum(len(file_report.dependency_references) for file_report in report.file_reports)
    actionable_rollup = ", ".join(f"<code>{escape(action)}</code> = {count}" for action, count in actionable_breakdown) or "no actionable PQC files"
    rows = [
        "<tr><td><code>Files scanned</code></td><td>Total files included in the scan scope.</td><td>This report scanned <strong>{}</strong> files under <code>{}</code>.</td></tr>".format(report.files_scanned, escape(report.root_path)),
        "<tr><td><code>Files with findings</code></td><td>Files where at least one PQC-related finding was detected.</td><td><strong>{}</strong> files had one or more PQC findings.</td></tr>".format(report.files_with_findings),
        "<tr><td><code>Dependency refs</code></td><td>Total dependency-reference observations collected across source files and manifests. This is a raw reference count, not a unique-component count, so the same package can contribute more than once if it appears in multiple files or forms.</td><td>The value <strong>{}</strong> comes from the report's dependency enrichment total (<code>dependency_reference_total</code>). It also matches the sum of the <code>Deps</code> column in the file findings table: <strong>{}</strong>.</td></tr>".format(report.dependency_reference_total, dependency_ref_rollup),
        "<tr><td><code>CBOM components</code></td><td>Total distinct observed software components included in the component inventory enrichment across ecosystems such as JVM, .NET, npm, Go, and Python.</td><td>The value <strong>{}</strong> is a unique-component count. The unique ecosystem tables below roll it up as <code>{}</code>.</td></tr>".format(len(report.cbom_components), escape(cbom_rollup)),
        "<tr><td><code>Observed Unique CBOM By Ecosystem</code></td><td>A deduplicated grouping of the observed CBOM component inventory by ecosystem.</td><td>Each component is counted once. The current report rolls the same <strong>{}</strong> unique CBOM components up as <code>{}</code>.</td></tr>".format(len(report.cbom_components), escape(cbom_rollup)),
        "<tr><td><code>Observed CBOM By Vendor / Source Family</code></td><td>A heuristic grouping of raw dependency-reference observations into product, vendor, framework, or crypto-source families defined in the vendor-family config catalog.</td><td>This is a raw reference count, not a unique-component count. The same dependency can contribute more than once if it appears in multiple files or forms. The current report rolls up to <code>{}</code> using configured families such as <code>{}</code>.</td></tr>".format(escape(vendor_source_rollup), escape(_vendor_family_example_rollup())),
        "<tr><td><code>Files with PQC</code></td><td>Files with one or more PQC indicators. In this report this is effectively the same as files with findings.</td><td>The value is <strong>{}</strong>, matching the files that appear with PQC findings in the file table below.</td></tr>".format(report.files_with_pqc),
        "<tr><td><code>Total PQC findings</code></td><td>Total number of PQC findings across all scanned files, including repeated findings by category inside the same file.</td><td>The value <strong>{}</strong> is the aggregate of all category-level PQC detections across the PQC-positive files.</td></tr>".format(report.total_pqc_findings),
        "<tr><td><code>PQC change targets</code></td><td>Files that look like likely implementation or migration owners rather than reference-only mentions. These are the files with actionable recommended changes.</td><td>The value <strong>{}</strong> comes from the actionable PQC files whose recommended actions are {}. The remaining <strong>{}</strong> PQC-positive files are reference-only.</td></tr>".format(report.pqc_likely_change_target_total, actionable_rollup, reference_only_count),
        "<tr><td><code>Dependency refs</code> vs <code>CBOM components</code></td><td>These metrics answer different questions. Dependency refs count all observed references. CBOM components count distinct observed components.</td><td>That is why <strong>Dependency refs = {}</strong> is larger than <strong>CBOM components = {}</strong> in this report.</td></tr>".format(report.dependency_reference_total, len(report.cbom_components)),
    ]
    return "\n".join([
        "<section>",
        "<h2>How To Read These Metrics</h2>",
        "<div class=\"panel markdown-panel\">",
        "<p>This legend explains what the top summary cards count, whether each number is unique or raw, and how the totals roll up from the tables below.</p>",
        "<table><thead><tr><th>Metric</th><th>Definition</th><th>How this report's value is derived</th></tr></thead><tbody>",
        *rows,
        "</tbody></table>",
        "</div>",
        "</section>",
    ])


def _render_dependency_summary(report: ScanReport) -> str:
    package_rows = [
        "<tr>"
        f"<td><code>{escape(name)}</code></td>"
        f"<td>{count}</td>"
        f"<td>{escape(dependency_meaning(name))}</td>"
        f"<td>{escape(_why_for_package(report, name))}</td>"
        "</tr>"
        for name, count in list(report.dependency_package_summary.items())[:15]
    ] or ["<tr><td colspan=\"4\">No dependency references found</td></tr>"]

    ecosystem_sections = _render_cbom_ecosystem_sections(report)

    return "\n".join([
        "<section>",
        "<h2>Dependency And CBOM Summary</h2>",
        "<div class=\"grid\">",
        _render_simple_table("Top Dependency References", ["Package", "Count", "Meaning", "Why It Matters"], package_rows),
        _render_stacked_key_value_tables(
            ("Observed Unique CBOM By Ecosystem", _dict_rows(_count_ecosystems(report).items())),
            ("Observed CBOM By Vendor / Source Family", _dict_rows(_count_vendor_source_reference_counts(report).items())),
            ("Top Remaining Other / General References", _remaining_general_reference_rows(report)),
        ),
        "</div>",
        *ecosystem_sections,
        "</section>",
    ])


def _render_ai_summary(report: ScanReport) -> str:
    metadata_rows = [
        ("Provider", report.ai_summary.provider),
        ("Model", report.ai_summary.model),
        ("Prompt version", report.ai_summary.prompt_version),
        ("Generated at (UTC)", report.ai_summary.generated_at_utc),
        ("Advisory only", str(report.ai_summary.advisory_only).lower()),
    ]
    markdown_html = "<br>".join(escape(line) for line in report.ai_summary.summary_markdown.splitlines())
    return "\n".join([
        "<section>",
        "<h2>AI Advisory Summary</h2>",
        "<div class=\"grid\">",
        _render_key_value_table("AI Summary Metadata", metadata_rows),
        '<section class="panel">',
        "<h3>Generated Summary</h3>",
        f"<div class=\"markdown-panel\">{markdown_html}</div>",
        "</section>",
        "</div>",
        "</section>",
    ])


def _render_ai_recommendations(report: ScanReport) -> str:
    metadata_rows = [
        ("Provider", report.ai_recommendations.provider),
        ("Model", report.ai_recommendations.model),
        ("Prompt version", report.ai_recommendations.prompt_version),
        ("Generated at (UTC)", report.ai_recommendations.generated_at_utc),
        ("Advisory only", str(report.ai_recommendations.advisory_only).lower()),
        ("File recommendations", str(len(report.ai_recommendations.file_recommendations))),
        ("Work packages", str(len(report.ai_recommendations.work_packages))),
    ]
    markdown_html = "<br>".join(escape(line) for line in report.ai_recommendations.summary_markdown.splitlines())
    file_rows = [
        "<tr>"
        f"<td><code>{escape(item.path)}</code></td>"
        f"<td>{escape(item.priority)}</td>"
        f"<td>{escape(item.recommendation)}</td>"
        f"<td>{escape(item.rationale)}</td>"
        "</tr>"
        for item in report.ai_recommendations.file_recommendations
    ] or ["<tr><td colspan=\"4\">No AI file recommendations</td></tr>"]
    package_rows = [
        "<tr>"
        f"<td>{escape(item.name)}</td>"
        f"<td>{escape(', '.join(item.related_categories))}</td>"
        f"<td>{escape(item.rationale)}</td>"
        f"<td>{escape(str(len(item.target_paths)))}</td>"
        "</tr>"
        for item in report.ai_recommendations.work_packages
    ] or ["<tr><td colspan=\"4\">No AI work packages</td></tr>"]
    dependency_rows = [
        "<tr>"
        f"<td><code>{escape(item.name)}</code></td>"
        f"<td>{escape(item.meaning)}</td>"
        f"<td>{escape(item.why_it_matters)}</td>"
        "</tr>"
        for item in report.ai_recommendations.dependency_guidance
    ] or ["<tr><td colspan=\"3\">No AI dependency guidance</td></tr>"]
    return "\n".join([
        "<section>",
        "<h2>AI Recommendation Advisory</h2>",
        "<div class=\"grid\">",
        _render_key_value_table("AI Recommendation Metadata", metadata_rows),
        '<section class="panel">',
        "<h3>Recommendation Overview</h3>",
        f"<div class=\"markdown-panel\">{markdown_html}</div>",
        "</section>",
        "</div>",
        _render_simple_table("AI File Recommendations", ["Path", "Priority", "Recommendation", "Rationale"], file_rows),
        _render_simple_table("AI Work Packages", ["Package", "Categories", "Rationale", "Target Files"], package_rows),
        _render_simple_table("AI Dependency Guidance", ["Dependency", "Meaning", "Why It Matters"], dependency_rows),
        "</section>",
    ])


def _render_cbom_ecosystem_sections(report: ScanReport) -> List[str]:
    grouped = defaultdict(list)
    for component in report.cbom_components:
        grouped[component.ecosystem or "unknown"].append(component)

    sections: List[str] = []
    for ecosystem in sorted(grouped.keys(), key=lambda item: item.lower()):
        rows = [
            "<tr>"
            f"<td><code>{escape(component.name)}</code></td>"
            f"<td>{escape(component.version)}</td>"
            f"<td>{escape(', '.join(component.related_categories))}</td>"
            f"<td>{escape(dependency_meaning(component.name, component.ecosystem, component.related_categories))}</td>"
            f"<td>{escape(dependency_why_it_matters(component.related_categories))}</td>"
            f"<td>{escape(component.origin)}</td>"
            f"<td>{escape(str(len(component.source_files)))}</td>"
            "</tr>"
            for component in sorted(grouped[ecosystem], key=lambda item: (item.name.lower(), item.version, item.origin))
        ] or ["<tr><td colspan=\"7\">No components</td></tr>"]
        sections.append(
            _render_simple_table(
                f"Observed CBOM Components: {ecosystem} ({len(grouped[ecosystem])})",
                ["Component", "Version", "Categories", "Meaning", "Why It Matters", "Origin", "Source Files"],
                rows,
            )
        )
    return sections


def _count_ecosystems(report: ScanReport) -> dict[str, int]:
    counts: dict[str, int] = {}
    for component in report.cbom_components:
        ecosystem = component.ecosystem or "unknown"
        counts[ecosystem] = counts.get(ecosystem, 0) + 1
    return counts


def _count_vendor_source_reference_counts(report: ScanReport) -> dict[str, int]:
    counts: dict[str, int] = {}
    for file_report in report.file_reports:
        for reference in file_report.dependency_references:
            family = _classify_cbom_vendor_source(reference.name)
            counts[family] = counts.get(family, 0) + 1
    return counts


def _load_cbom_vendor_families() -> tuple[Sequence[Tuple[str, Sequence[str]]], str]:
    try:
        raw = json.loads(CBOM_VENDOR_FAMILIES_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CBOM_VENDOR_FAMILY_PATTERNS, DEFAULT_CBOM_VENDOR_FALLBACK_LABEL

    if not isinstance(raw, dict):
        return DEFAULT_CBOM_VENDOR_FAMILY_PATTERNS, DEFAULT_CBOM_VENDOR_FALLBACK_LABEL

    families_raw = raw.get("vendor_families", [])
    fallback_label = str(raw.get("fallback_label", DEFAULT_CBOM_VENDOR_FALLBACK_LABEL) or DEFAULT_CBOM_VENDOR_FALLBACK_LABEL).strip() or DEFAULT_CBOM_VENDOR_FALLBACK_LABEL
    if not isinstance(families_raw, list):
        return DEFAULT_CBOM_VENDOR_FAMILY_PATTERNS, fallback_label

    parsed: List[Tuple[str, Sequence[str]]] = []
    for item in families_raw:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label", "") or "").strip()
        patterns_raw = item.get("patterns", [])
        if not label or not isinstance(patterns_raw, list):
            continue
        patterns = [str(pattern).strip().lower() for pattern in patterns_raw if str(pattern).strip()]
        if patterns:
            parsed.append((label, tuple(patterns)))

    return (tuple(parsed) or DEFAULT_CBOM_VENDOR_FAMILY_PATTERNS), fallback_label


CBOM_VENDOR_FAMILY_PATTERNS, CBOM_VENDOR_FALLBACK_LABEL = _load_cbom_vendor_families()


def _vendor_family_example_rollup(limit: int = 8) -> str:
    labels = [label for label, _patterns in CBOM_VENDOR_FAMILY_PATTERNS[:limit]]
    if not labels:
        return CBOM_VENDOR_FALLBACK_LABEL
    return ", ".join(labels)


def _classify_cbom_vendor_source(component_name: str) -> str:
    normalized = (component_name or "").lower()
    for label, patterns in CBOM_VENDOR_FAMILY_PATTERNS:
        if any(pattern in normalized for pattern in patterns):
            return label
    return CBOM_VENDOR_FALLBACK_LABEL


def _remaining_general_reference_rows(report: ScanReport) -> List[Tuple[str, str]]:
    counts: dict[str, int] = {}
    for file_report in report.file_reports:
        for reference in file_report.dependency_references:
            if _classify_cbom_vendor_source(reference.name) != CBOM_VENDOR_FALLBACK_LABEL:
                continue
            counts[reference.name] = counts.get(reference.name, 0) + 1
    rows = [(name, str(count)) for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:8]]
    return rows or [("None", "0")]




def _render_pii_top_stats(report: ScanReport, pii_file_reports: Sequence[FileReport]) -> str:
    likely_change_target_total = sum(1 for file_report in pii_file_reports if file_report.ownership and file_report.ownership.likely_change_target)
    custom_category_total = sum(1 for category in report.totals_by_category if str(category).startswith("CUSTOM_"))
    cards = [
        _stat_card("Scan domains", ", ".join(report.scan_domains)),
        _stat_card("Files scanned", str(report.files_scanned)),
        _stat_card("Files with PII", str(report.files_with_pii)),
        _stat_card("Total PII matches", str(report.total_pii_matches)),
        _stat_card("Likely change targets", str(likely_change_target_total)),
        _stat_card("JDBC candidates", str(report.jdbc_candidate_total)),
        _stat_card("Code change candidates", str(report.code_change_candidate_total)),
    ]
    if custom_category_total:
        cards.append(_stat_card("Custom categories", str(custom_category_total)))
    return "<section><div class=\"stats\">" + "".join(cards) + "</div></section>"


def _render_pii_metric_legend(report: ScanReport, pii_file_reports: Sequence[FileReport]) -> str:
    likely_change_target_total = sum(1 for file_report in pii_file_reports if file_report.ownership and file_report.ownership.likely_change_target)
    reference_only_total = len(pii_file_reports) - likely_change_target_total
    custom_categories = [category for category in report.totals_by_category if str(category).startswith("CUSTOM_")]
    action_rollup = ", ".join(
        f"<code>{escape(action)}</code> = {count}"
        for action, count in _count_values(
            file_report.ownership.recommended_change_action
            for file_report in pii_file_reports
            if file_report.ownership and file_report.ownership.recommended_change_action
        )
    ) or "no recommended actions"
    rows = [
        "<tr><td><code>Files scanned</code></td><td>Total files included in the scan scope.</td><td>This report scanned <strong>{}</strong> files under <code>{}</code>.</td></tr>".format(report.files_scanned, escape(report.root_path)),
        "<tr><td><code>Files with PII</code></td><td>Files with one or more PII detections from built-in or custom keyword / regex patterns.</td><td>The value is <strong>{}</strong>, matching the PII-positive files shown in the file findings table below.</td></tr>".format(report.files_with_pii),
        "<tr><td><code>Total PII matches</code></td><td>Raw detection count across all files and categories. This is not a unique-field count.</td><td>The value <strong>{}</strong> includes repeated matches when the same field or category appears multiple times in a file or across files.</td></tr>".format(report.total_pii_matches),
        "<tr><td><code>Likely change targets</code></td><td>PII-positive files that the ownership heuristics marked as likely implementation or migration owners instead of reference-only files.</td><td>The value <strong>{}</strong> comes from actionable files with recommended changes {}. The remaining <strong>{}</strong> PII-positive files are reference-only or supporting-model oriented.</td></tr>".format(likely_change_target_total, action_rollup, reference_only_total),
        "<tr><td><code>JDBC candidates</code></td><td>Raw count of JDBC-oriented planning signals observed in the scan.</td><td>The value <strong>{}</strong> is an observation count, so a single file can contribute more than once if it contains multiple JDBC migration hints.</td></tr>".format(report.jdbc_candidate_total),
        "<tr><td><code>Code change candidates</code></td><td>Raw count of code-level change indicators that suggest application updates may be needed.</td><td>The value <strong>{}</strong> is also a raw signal count rather than a unique-file count.</td></tr>".format(report.code_change_candidate_total),
    ]
    if custom_categories:
        rows.append(
            "<tr><td><code>Custom categories</code></td><td>Scanner categories added through customer-maintained custom keyword or regex patterns.</td><td>This report observed <strong>{}</strong> custom categories: {}</td></tr>".format(
                len(custom_categories),
                ", ".join(f"<code>{escape(category)}</code>" for category in sorted(custom_categories)),
            )
        )
    return "\n".join([
        "<section>",
        "<h2>How To Read These Metrics</h2>",
        "<div class=\"panel markdown-panel\">",
        "<p>This legend explains the PII summary cards, what each number counts, and whether the value is a unique file count or a raw observation count.</p>",
        "<table><thead><tr><th>Metric</th><th>Definition</th><th>How this report's value is derived</th></tr></thead><tbody>",
        *rows,
        "</tbody></table>",
        "</div>",
        "</section>",
    ])


def _render_pii_planning_summary(report: ScanReport, pii_file_reports: Sequence[FileReport]) -> str:
    context_counts = _dict_rows(_count_values(file_report.classification.context for file_report in pii_file_reports))
    owner_counts = _dict_rows(_count_values(
        file_report.ownership.likely_change_owner
        for file_report in pii_file_reports
        if file_report.ownership
    ))
    action_counts = _dict_rows(_count_values(
        file_report.ownership.recommended_change_action
        for file_report in pii_file_reports
        if file_report.ownership
    ))
    role_counts = _dict_rows(_count_values(
        file_report.ownership.role_in_flow
        for file_report in pii_file_reports
        if file_report.ownership
    ))
    complexity_counts = _dict_rows(_count_values(
        file_report.complexity.rating
        for file_report in pii_file_reports
        if file_report.complexity
    ))
    return "\n".join([
        "<section>",
        "<h2>PII Planning Summary</h2>",
        '<div class="panel markdown-panel"><p>This section groups PII-positive files by detection category, likely change ownership, remediation lane, role in flow, and complexity so implementation teams can quickly separate primary change targets from reference-only files.</p></div>',
        '<div class="grid summary-grid-equal">',
        _render_key_value_table("PII Categories", _dict_rows(report.totals_by_category.items())),
        _render_key_value_table("File Contexts", context_counts),
        "</div>",
        '<div class="grid summary-grid-equal">',
        _render_key_value_table("Likely Change Owners", owner_counts),
        _render_key_value_table("Recommended Actions", action_counts),
        "</div>",
        '<div class="grid summary-grid-equal">',
        _render_key_value_table("Role In Flow", role_counts),
        _render_key_value_table("Complexity Distribution", complexity_counts),
        "</div>",
        "</section>",
    ])


def _render_pii_tables_summary(report: ScanReport) -> str:
    rows = []
    for table_name, details in sorted(report.tables_summary.items(), key=lambda item: (-int(item[1].get("match_count", 0)), item[0])):
        columns = ", ".join(str(column) for column in details.get("columns", [])) or "None"
        file_count = int(details.get("file_count", 0))
        match_count = int(details.get("match_count", 0))
        rows.append(
            "<tr>"
            f"<td><code>{escape(table_name)}</code></td>"
            f"<td>{match_count}</td>"
            f"<td>{file_count}</td>"
            f"<td>{escape(columns)}</td>"
            "</tr>"
        )
    if not rows:
        rows = ['<tr><td colspan="4">No inferred PII data stores or table groupings</td></tr>']
    return "\n".join([
        "<section>",
        "<h2>Inferred Data Store Summary</h2>",
        '<div class="panel markdown-panel"><p>The scanner also rolls repeated field detections into likely data-store or table groupings when source files suggest a shared persistence target. These are planning hints, not authoritative schema definitions.</p></div>',
        _render_simple_table("Inferred Tables / Collections", ["Store or Table", "Matches", "Files", "Observed Sensitive Fields"], rows),
        "</section>",
    ])


def _render_pii_file_report_table(file_reports: Sequence[FileReport]) -> str:
    rows = []
    ordered = sorted(file_reports, key=lambda item: (-RATING_ORDER.get(_overall_change_likelihood(item), 0), -len(item.pii_matches), item.path.lower()))
    for file_report in ordered:
        owner = file_report.ownership.likely_change_owner if file_report.ownership else ""
        action = file_report.ownership.recommended_change_action if file_report.ownership else ""
        complexity = file_report.complexity.rating if file_report.complexity else "low"
        categories = ", ".join(
            f"{key}={value}" for key, value in sorted(file_report.summary_by_category.items(), key=lambda item: (-item[1], item[0]))[:4]
        ) or "None"
        rows.append(
            "<tr>"
            f"<td><code>{escape(file_report.path)}</code></td>"
            f"<td>{escape(file_report.classification.layer)}</td>"
            f"<td>{escape(file_report.classification.context)}</td>"
            f"<td>{len(file_report.pii_matches)}</td>"
            f"<td>{escape(categories)}</td>"
            f"<td>{escape(owner)}</td>"
            f"<td>{escape(action)}</td>"
            f"<td><span class=\"badge badge-{escape(complexity)}\">{escape(complexity)}</span></td>"
            f"<td>{_pii_file_notes_html(file_report)}</td>"
            "</tr>"
        )
    if not rows:
        rows = ['<tr><td colspan="9">No PII-positive files found</td></tr>']
    return "\n".join([
        "<section>",
        "<h2>PII File Findings</h2>",
        '<div class="table-wrap pii-file-findings-wrap">',
        '<table class="pii-file-findings-table"><thead><tr><th>Path</th><th>Layer</th><th>Context</th><th>PII Matches</th><th>Top Categories</th><th>Likely Owner</th><th>Recommended Action</th><th>Complexity</th><th>Notes</th></tr></thead><tbody>',
        *rows,
        "</tbody></table>",
        "</div>",
        "</section>",
    ])


def _pii_file_notes_html(file_report: FileReport) -> str:
    parts: List[str] = []
    if file_report.ownership and file_report.ownership.role_in_flow:
        parts.append(escape(f"Role: {file_report.ownership.role_in_flow}"))
    if file_report.ownership and file_report.ownership.matched_payload_fields:
        parts.append(escape("Payload fields: " + ", ".join(file_report.ownership.matched_payload_fields[:6])))
    if file_report.ownership and file_report.ownership.matched_endpoints:
        parts.append(escape("Endpoints: " + ", ".join(file_report.ownership.matched_endpoints[:4])))
    if file_report.ownership and file_report.ownership.rationale:
        parts.append(escape(file_report.ownership.rationale[0]))
    elif file_report.notes:
        parts.append(escape(file_report.notes[0]))
    return " | ".join(parts)

def _render_pii_summary(report: ScanReport) -> str:
    return "\n".join([
        "<section>",
        "<h2>PII Summary</h2>",
        "<div class=\"grid\">",
        _render_key_value_table("Categories", _dict_rows(report.totals_by_category.items())),
        _render_key_value_table("Likely Change Owners", _dict_rows(_count_values(
            file_report.ownership.likely_change_owner for file_report in report.file_reports if file_report.ownership
        ))),
        _render_key_value_table("Recommended Actions", _dict_rows(_count_values(
            file_report.ownership.recommended_change_action for file_report in report.file_reports if file_report.ownership
        ))),
        _render_key_value_table("Complexity Distribution", _dict_rows(_count_values(
            file_report.complexity.rating for file_report in report.file_reports if file_report.complexity
        ))),
        "</div>",
        "</section>",
    ])


def _render_pqc_summary(report: ScanReport) -> str:
    action_counts = dict(_count_values(
        file_report.pqc_recommended_change_action for file_report in report.file_reports if file_report.pqc_findings
    ))
    context_counts = dict(_count_values(
        file_report.classification.context for file_report in report.file_reports if file_report.pqc_findings
    ))
    return "\n".join([
        "<section>",
        "<h2>PQC Summary</h2>",
        '<div class="panel markdown-panel">',
        "<p>This section groups PQC findings four ways: by technical category, by migration class, by recommended remediation lane, and by file context. The value in each summary table is the count of PQC findings or PQC-positive files that landed in that bucket, as described below.</p>",
        "<p><strong>Note: PQC-capable status tags</strong><br>Some files will show a color-coded PQC-capable status tag in the file findings table. Those tags are file-level only. They mean the scanner saw explicit PQC or hybrid algorithm names in that file. They do not mean the entire vendor family, platform, or product line is universally PQC-ready.</p>",
        "<p><strong>Note: Dependency Enrichment</strong><br>Dependency enrichment is the scanner step that turns raw imports, package references, manifest entries, and SDK names into more useful migration signals. Instead of only saying a file contains text that looks cryptographic, it also records which libraries, namespaces, modules, or headers were observed and links them to likely crypto categories such as certificates, JWT signing, TLS, SSH, KMS, or HSM usage.</p>",
        "<p>In practice, dependency enrichment helps answer questions like: which crypto-related dependencies were seen, how often they were observed, which files referenced them, and whether they point to vendor SDK, PKI, protocol-stack, or application-signing migration work. The <code>Dependency refs</code> metric is the raw observation count produced by this enrichment step.</p>",
        "<p><strong>Note: PQC complexity ratings</strong><br>The report also assigns each file a PQC migration-complexity rating of <code>low</code>, <code>medium</code>, or <code>high</code>. This is a migration-effort signal, not a vulnerability severity score. In general, files trend higher when they appear to own real signing, certificate, key-exchange, TLS, SSH, KMS, HSM, or vendor-SDK integration behavior. Files trend lower when they are mostly tests, documentation, UI-only references, or secondary mentions. The current thresholds are <code>low &lt; 6</code>, <code>medium = 6 to less than 12</code>, and <code>high &gt;= 12</code>.</p>",
        "</div>",
        '<div class="grid">',
        _render_pqc_definition_table(
            "PQC Category Definitions",
            report.pqc_totals_by_category,
            PQC_CATEGORY_DEFINITIONS,
            "Count",
        ),
        _render_pqc_signal_status_table(report),
        _render_pqc_definition_table(
            "PQC Migration Class Definitions",
            report.pqc_migration_class_totals,
            PQC_MIGRATION_CLASS_DEFINITIONS,
            "Count",
        ),
        _render_pqc_definition_table(
            "PQC Recommended Action Definitions",
            action_counts,
            PQC_RECOMMENDED_ACTION_DEFINITIONS,
            "Files",
        ),
        _render_pqc_definition_table(
            "PQC File Context Definitions",
            context_counts,
            PQC_FILE_CONTEXT_DEFINITIONS,
            "Files",
        ),
        "</div>",
        "</section>",
    ])


def _render_pqc_definition_table(
    title: str,
    counts: dict[str, int],
    definitions: dict[str, tuple[str, str]],
    count_header: str,
) -> str:
    rows = []
    for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        meaning, why = definitions.get(
            key,
            (
                "PQC-related classification produced by the scanner.",
                "Review the underlying files to confirm exact migration scope and ownership.",
            ),
        )
        rows.append(
            "<tr>"
            f"<td><code>{escape(str(key))}</code></td>"
            f"<td>{count}</td>"
            f"<td>{escape(meaning)}</td>"
            f"<td>{escape(why)}</td>"
            "</tr>"
        )
    if not rows:
        rows = ['<tr><td colspan="4">No PQC data</td></tr>']
    return _render_simple_table(title, ["Item", count_header, "Meaning", "Why It Matters"], rows)


def _render_pqc_signal_status_table(report: ScanReport) -> str:
    counts = _count_pqc_signal_statuses(report)
    rows = []
    for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        label, meaning, why = PQC_SIGNAL_STATUS_DEFINITIONS.get(
            key,
            (
                "PQC-capable status",
                "PQC-capable file status produced by the scanner.",
                "Review the file to confirm exact algorithm maturity and deployment scope.",
            ),
        )
        rows.append(
            "<tr>"
            f"<td>{_render_pqc_status_badge(key, label)}</td>"
            f"<td>{count}</td>"
            f"<td>{escape(meaning)}</td>"
            f"<td>{escape(why)}</td>"
            "</tr>"
        )
    if not rows:
        rows = ['<tr><td colspan="4">No explicit PQC-capable algorithm signals</td></tr>']
    return _render_simple_table("PQC-capable Status", ["Item", "Files", "Meaning", "Why It Matters"], rows)


def _render_file_report_table(file_reports: Sequence[FileReport]) -> str:
    rows = []
    ordered = sorted(file_reports, key=lambda item: (-RATING_ORDER.get(_overall_change_likelihood(item), 0), item.path.lower()))
    for file_report in ordered:
        row_class = _pqc_row_class(file_report)
        rows.append(
            f"<tr{row_class}>"
            f"<td>{_render_file_path_cell(file_report)}</td>"
            f"<td>{escape(', '.join(_finding_domains(file_report)))}</td>"
            f"<td>{escape(file_report.classification.layer)}</td>"
            f"<td>{escape(file_report.classification.context)}</td>"
            f"<td><span class=\"badge badge-{escape(_overall_change_likelihood(file_report))}\">{escape(_overall_change_likelihood(file_report))}</span></td>"
            f"<td>{len(file_report.pii_matches)}</td>"
            f"<td>{len(file_report.pqc_findings)}</td>"
            f"<td>{len(file_report.dependency_references)}</td>"
            f"<td>{escape(_combined_action(file_report))}</td>"
            f"<td>{_file_notes_html(file_report)}</td>"
            "</tr>"
        )
    return "\n".join([
        "<section>",
        "<h2>File Findings</h2>",
        '<div class="table-wrap file-findings-wrap">',
        '<table class="file-findings-table"><thead><tr><th>Path</th><th>Domains</th><th>Layer</th><th>Context</th><th>Overall</th><th>PII</th><th>PQC</th><th>Deps</th><th>Recommended Action</th><th>Notes</th></tr></thead><tbody>',
        *rows,
        "</tbody></table>",
        "</div>",
        "</section>",
    ])


def _render_key_value_table(title: str, rows: Sequence[Tuple[str, str]]) -> str:
    body = [f"<tr><td>{escape(label)}</td><td>{escape(value)}</td></tr>" for label, value in rows] or ["<tr><td colspan=\"2\">No data</td></tr>"]
    return "\n".join([
        '<section class="panel">',
        f"<h3>{escape(title)}</h3>",
        '<div class="table-wrap">',
        "<table><thead><tr><th>Item</th><th>Value</th></tr></thead><tbody>",
        *body,
        "</tbody></table>",
        "</div>",
        "</section>",
    ])


def _render_simple_table(title: str, headers: Sequence[str], rows: Sequence[str]) -> str:
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    return "\n".join([
        '<section class="panel">',
        f"<h3>{escape(title)}</h3>",
        '<div class="table-wrap">',
        f"<table><thead><tr>{header_html}</tr></thead><tbody>",
        *rows,
        "</tbody></table>",
        "</div>",
        "</section>",
    ])


def _render_stacked_key_value_tables(*sections: Tuple[str, Sequence[Tuple[str, str]]]) -> str:
    blocks: List[str] = []
    for index, (title, rows) in enumerate(sections):
        body = [
            f"<tr><td>{_render_key_value_label(title, label)}</td><td>{escape(value)}</td></tr>"
            for label, value in rows
        ] or ['<tr><td colspan="2">No data</td></tr>']
        section_class = "stacked-section" if index == 0 else "stacked-section stacked-section-divider"
        blocks.extend([
            f'<div class="{section_class}">',
            f"<h3>{escape(title)}</h3>",
            _stacked_section_note(title),
            '<div class="table-wrap">',
            "<table><thead><tr><th>Item</th><th>Value</th></tr></thead><tbody>",
            *body,
            "</tbody></table>",
            "</div>",
            "</div>",
        ])
    return "\n".join([
        '<section class="panel stacked-panel">',
        *blocks,
        "</section>",
    ])


def _dict_rows(items: Iterable[Tuple[str, int]]) -> List[Tuple[str, str]]:
    return [(str(key), str(value)) for key, value in sorted(items, key=lambda item: (-item[1], item[0]))]


def _render_key_value_label(title: str, label: str) -> str:
    if title == "Observed CBOM By Vendor / Source Family" and label.startswith("Custom "):
        return f'<span class="custom-family-tag">{escape(label)}</span>'
    return escape(label)


def _stacked_section_note(title: str) -> str:
    if title == "Observed CBOM By Vendor / Source Family":
        return "<p class=\"table-note\"><strong>Note:</strong> Families that start with <code>Custom</code> represent company-built wrappers, internal service endpoints, or abstraction layers layered on top of vendor APIs rather than the vendor's core SDK or platform package names.</p>"
    return ""


def _count_values(values: Iterable[str]) -> List[Tuple[str, int]]:
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return list(counts.items())


def _finding_domains(file_report: FileReport) -> List[str]:
    domains: List[str] = []
    if file_report.pii_matches:
        domains.append("pii")
    if file_report.pqc_findings:
        domains.append("pqc")
    return domains


def _render_file_path_cell(file_report: FileReport) -> str:
    path_html = f"<code>{escape(file_report.path)}</code>"
    status = _pqc_signal_status(file_report)
    if status:
        return path_html + "<br>" + _render_pqc_status_badge(status, _pqc_status_short_label(status))
    return path_html


def _combined_action(file_report: FileReport) -> str:
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


def _has_pqc_capable_signal(file_report: FileReport) -> bool:
    return _pqc_signal_status(file_report) is not None


def _pqc_signal_status(file_report: FileReport) -> str | None:
    if file_report.classification.context in {"docs", "test"}:
        return None
    matched_statuses = []
    for finding in file_report.pqc_findings:
        status = _classify_pqc_signal_text(finding.matched_text)
        if status:
            matched_statuses.append(status)
    if "PQC_CAPABLE_ALGORITHM" in file_report.pqc_summary_by_category and not matched_statuses:
        matched_statuses.append("alias_or_legacy_name")
    if not matched_statuses:
        return None
    if file_report.classification.context == "frontend" and not _has_frontend_pqc_implementation_signal(file_report):
        return None
    return max(matched_statuses, key=lambda item: PQC_SIGNAL_STATUS_ORDER.get(item, 0))


def _classify_pqc_signal_text(text: str) -> str | None:
    upper_text = text.upper()
    for status, terms in PQC_SIGNAL_STATUS_PATTERNS:
        if any(term in upper_text for term in terms):
            return status
    return None


def _has_frontend_pqc_implementation_signal(file_report: FileReport) -> bool:
    for finding in file_report.pqc_findings:
        lowered = finding.matched_text.lower()
        if any(marker in lowered for marker in FRONTEND_PQC_IMPLEMENTATION_MARKERS):
            return True
    return False


def _pqc_status_short_label(status: str) -> str:
    labels = {
        "nist_current": "PQC-current",
        "approved_specialized": "PQC-specialized",
        "alias_or_legacy_name": "PQC-alias",
        "experimental_or_watchlist": "PQC-watch-list",
    }
    return labels.get(status, "PQC-capable")


def _render_pqc_status_badge(status: str, label: str) -> str:
    return f'<span class="pqc-capable-tag pqc-capable-tag-{escape(status)}">{escape(label)}</span>'


def _pqc_row_class(file_report: FileReport) -> str:
    status = _pqc_signal_status(file_report)
    if not status:
        return ""
    return f' class="pqc-capable-row pqc-capable-row-{escape(status)}"'


def _count_pqc_signal_statuses(report: ScanReport) -> Counter[str]:
    counts: Counter[str] = Counter()
    for file_report in report.file_reports:
        status = _pqc_signal_status(file_report)
        if status:
            counts[status] += 1
    return counts


def _file_notes_html(file_report: FileReport) -> str:
    note_parts: List[str] = []
    status = _pqc_signal_status(file_report)
    if status:
        _, meaning, _ = PQC_SIGNAL_STATUS_DEFINITIONS.get(
            status,
            (
                "PQC-capable status",
                "Explicit PQC or hybrid algorithm markers observed in this file.",
                "Review the file to confirm exact algorithm maturity and deployment scope.",
            ),
        )
        note_parts.append(_render_pqc_status_badge(status, _pqc_status_short_label(status)))
        note_parts.append(escape(meaning))
    if file_report.pqc_summary_by_category:
        note_parts.append(escape("PQC: " + ", ".join(f"{key}={value}" for key, value in sorted(file_report.pqc_summary_by_category.items()))))
    if file_report.dependency_references:
        note_parts.append(escape("Deps: " + ", ".join(sorted({item.name for item in file_report.dependency_references})[:4])))
    if file_report.notes:
        note_parts.append(escape(file_report.notes[0]))
    return " | ".join(note_parts)


def _stat_card(label: str, value: str) -> str:
    return '<section class="stat-card">' + f'<div class="stat-label">{escape(label)}</div>' + f'<div class="stat-value">{escape(value)}</div>' + "</section>"


def _why_for_package(report: ScanReport, package_name: str) -> str:
    categories: List[str] = []
    for component in report.cbom_components:
        if component.name == package_name:
            for category in component.related_categories:
                if category not in categories:
                    categories.append(category)
    if not categories:
        for file_report in report.file_reports:
            for reference in file_report.dependency_references:
                if reference.name == package_name:
                    for category in reference.related_categories:
                        if category not in categories:
                            categories.append(category)
    return dependency_why_it_matters(categories)


def _css() -> str:
    return """
body {
  margin: 0;
  background: #f4f1ea;
  color: #1f2430;
  font-family: 'Segoe UI', Tahoma, sans-serif;
}
.page {
  max-width: 1500px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}
h1, h2, h3 {
  color: #11233b;
}
.lede {
  margin-bottom: 24px;
}
.stats, .grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.grid {
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 0.95fr);
  align-items: start;
}
.grid > * {
  min-width: 0;
}
.stat-card, .panel {
  background: #fffdf8;
  border: 1px solid #d9cdb8;
  border-radius: 14px;
  padding: 16px 18px;
  box-shadow: 0 8px 22px rgba(17, 35, 59, 0.06);
}
.panel {
  overflow: hidden;
}
.markdown-panel {
  white-space: normal;
  line-height: 1.55;
}
.table-wrap {
  width: 100%;
  overflow-x: auto;
}
.stacked-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.stacked-section-divider {
  border-top: 1px solid #e5d9c7;
  padding-top: 12px;
}
.stacked-section h3 {
  margin: 0 0 10px;
}
.stat-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #7b6f60;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-top: 8px;
}
section {
  margin-top: 24px;
}
table {
  width: 100%;
  border-collapse: collapse;
  background: #fffdf8;
  border: 1px solid #d9cdb8;
  border-radius: 14px;
  overflow: hidden;
  table-layout: fixed;
}
th, td {
  text-align: left;
  vertical-align: top;
  padding: 12px 14px;
  border-bottom: 1px solid #eadfcd;
  overflow-wrap: anywhere;
  word-break: break-word;
}
th {
  background: #efe6d6;
  color: #31445c;
  font-size: 13px;
}
tr:nth-child(even) td {
  background: #fcf8f1;
}
code {
  font-family: Consolas, 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
}
.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}
.badge-low { background: #d6f0d8; color: #22543d; }
.badge-medium { background: #fef0c7; color: #92400e; }
.badge-high { background: #ffd5d5; color: #9b1c1c; }
.table-note {
  margin: 0 0 12px;
  color: #5e5a52;
  font-size: 13px;
  line-height: 1.5;
}
.custom-family-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  background: #d9eef9;
  border: 1px solid #8fbfd4;
  color: #174a63;
  font-weight: 700;
}
.pqc-capable-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-weight: 700;
}
.pqc-capable-tag-nist_current {
  background: #d7f4df;
  border: 1px solid #84c49a;
  color: #1f5f36;
}
.pqc-capable-tag-approved_specialized,
.pqc-capable-tag-alias_or_legacy_name {
  background: #fef0c7;
  border: 1px solid #d9a441;
  color: #8a5a00;
}
.pqc-capable-tag-experimental_or_watchlist {
  background: #dde6f7;
  border: 1px solid #98acd6;
  color: #29456f;
}
.pqc-capable-row-nist_current td:first-child {
  border-left: 4px solid #84c49a;
}
.pqc-capable-row-approved_specialized td:first-child,
.pqc-capable-row-alias_or_legacy_name td:first-child {
  border-left: 4px solid #d9a441;
}
.pqc-capable-row-experimental_or_watchlist td:first-child {
  border-left: 4px solid #98acd6;
}
.file-findings-wrap table {
  table-layout: fixed;
}
.file-findings-table th:nth-child(1),
.file-findings-table td:nth-child(1) {
  width: 16%;
}
.file-findings-table th:nth-child(2),
.file-findings-table td:nth-child(2) {
  width: 6%;
}
.file-findings-table th:nth-child(3),
.file-findings-table td:nth-child(3) {
  width: 9%;
}
.file-findings-table th:nth-child(4),
.file-findings-table td:nth-child(4) {
  width: 9%;
}
.file-findings-table th:nth-child(5),
.file-findings-table td:nth-child(5) {
  width: 8%;
}
.file-findings-table th:nth-child(6),
.file-findings-table td:nth-child(6),
.file-findings-table th:nth-child(7),
.file-findings-table td:nth-child(7),
.file-findings-table th:nth-child(8),
.file-findings-table td:nth-child(8) {
  width: 4%;
  text-align: center;
}
.file-findings-table th:nth-child(9),
.file-findings-table td:nth-child(9) {
  width: 10%;
}
.file-findings-table th:nth-child(10),
.file-findings-table td:nth-child(10) {
  width: 30%;
}
.file-findings-table td:nth-child(1),
.file-findings-table td:nth-child(9),
.file-findings-table td:nth-child(10) {
  overflow-wrap: anywhere;
  word-break: break-word;
}
.file-findings-table td:nth-child(10) {
  line-height: 1.45;
}
.summary-grid-equal {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}
.pii-file-findings-wrap table {
  table-layout: fixed;
}
.pii-file-findings-table th:nth-child(1),
.pii-file-findings-table td:nth-child(1) {
  width: 22%;
}
.pii-file-findings-table th:nth-child(2),
.pii-file-findings-table td:nth-child(2),
.pii-file-findings-table th:nth-child(3),
.pii-file-findings-table td:nth-child(3) {
  width: 7%;
}
.pii-file-findings-table th:nth-child(4),
.pii-file-findings-table td:nth-child(4) {
  width: 5%;
  text-align: center;
}
.pii-file-findings-table th:nth-child(5),
.pii-file-findings-table td:nth-child(5) {
  width: 13%;
}
.pii-file-findings-table th:nth-child(6),
.pii-file-findings-table td:nth-child(6) {
  width: 11%;
}
.pii-file-findings-table th:nth-child(7),
.pii-file-findings-table td:nth-child(7) {
  width: 12%;
}
.pii-file-findings-table th:nth-child(8),
.pii-file-findings-table td:nth-child(8) {
  width: 6%;
  text-align: center;
}
.pii-file-findings-table th:nth-child(9),
.pii-file-findings-table td:nth-child(9) {
  width: 17%;
  line-height: 1.45;
}
@media (max-width: 720px) {
  .page { padding: 20px 12px 40px; }
  .grid { grid-template-columns: 1fr; }
  th, td { padding: 10px; }
}
"""



