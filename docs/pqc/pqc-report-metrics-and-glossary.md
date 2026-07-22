# PQC Report Metrics And Glossary

This document explains the plain-English meaning of the HTML PQC report metrics and summary sections.

## How To Read These Metrics

The scanner report mixes both raw counts and unique counts. They answer different questions.

- `Files scanned`: Total files included in the scan scope.
- `Files with findings`: Files where at least one scanner finding was detected for the active scan domain.
- `Dependency refs`: Total dependency-reference observations collected across source files and manifests. This is a raw reference count, not a unique count, so the same package can contribute more than once if it appears in multiple files or forms.
- `CBOM components`: Total distinct observed software components included in the component inventory enrichment. This is a unique-component count.
- `Observed Unique CBOM By Ecosystem`: A deduplicated grouping of the observed CBOM component inventory by ecosystem such as JVM, .NET, npm, Go, Python, or native.
- `Observed CBOM By Vendor / Source Family`: A heuristic grouping of raw dependency-reference observations into product, vendor, framework, or crypto-source families defined in the vendor-family config catalog. This is a raw reference count, not a unique-component count. Families that start with `Custom` represent company-built wrappers, internal endpoints, or abstraction layers that sit on top of vendor APIs rather than the vendor's core SDK names themselves.
- `Files with PQC`: Files with one or more PQC indicators.
- `Total PQC findings`: Total number of PQC findings across all scanned files, including repeated findings by category inside the same file.
- `PQC change targets`: Files that look like likely implementation or migration owners rather than reference-only mentions. These are the files with actionable recommended changes.

## What Dependency Enrichment Means

Dependency enrichment is the scanner step that turns raw imports, package references, manifest entries, SDK names, and selected source markers such as wrapper class names or crypto-facing route literals into more useful migration signals.

Instead of only saying that a file contains text that looks cryptographic, dependency enrichment also records which libraries, namespaces, modules, or headers were observed and links them to likely crypto categories such as:

- certificates and PKI
- JWT or token signing
- TLS or mTLS
- SSH
- KMS or HSM usage
- vendor crypto SDK dependencies

In practice, dependency enrichment helps answer questions like:

- which crypto-related dependencies were seen
- how often they were observed
- which files referenced them
- whether they point more toward vendor SDK work, PKI work, protocol-stack work, or application-signing work

The `Dependency refs` metric is the raw observation count produced by this enrichment step.

## Key Distinctions

- `Dependency refs` counts all observed references.
- `CBOM components` counts distinct observed components.
- `Observed Unique CBOM By Ecosystem` stays unique.
- `Observed CBOM By Vendor / Source Family` now reflects actual observed reference volume.

## PQC Summary

The PQC summary groups findings four ways:

- `Categories`: What kind of crypto thing was found.
- `Migration Classes`: What kind of migration work the finding suggests.
- `Recommended Actions`: Which remediation lane the file was mapped to.
- `File Contexts`: What kind of file the finding appeared in.

In the HTML report:

- category counts are counts of PQC findings in each technical category
- migration class counts are counts of PQC findings in each migration-work type
- recommended action counts are counts of PQC-positive files mapped to each action
- file context counts are counts of PQC-positive files mapped to each context

## Related Guide

For step-by-step maintenance instructions on adding new PQC algorithms and mapping them into report status buckets, see `E:\codex\work\migration\docs\pqc\how-to-add-a-new-pqc-algorithm.md`.

## PQC-capable Status Tags

The HTML report can also show a file-level `PQC-capable` status tag when the scanner sees explicit PQC or hybrid algorithm names in the file itself.

These tags do not replace the main PQC categories. They are a secondary interpretation layer that helps distinguish the maturity of explicit PQC algorithm references.

- `PQC-current`: Current or selected NIST-aligned names such as `ML-KEM`, `ML-DSA`, `SLH-DSA`, `FN-DSA`, or `HQC`.
- `PQC-specialized`: Specialized approved hash-based signature names such as `XMSS`, `XMSSMT`, `LMS`, or `HSS`.
- `PQC-alias`: Older or alias names such as `Kyber`, `Dilithium`, `Falcon`, or `SPHINCS+` that often map to NIST-standardized families.
- `PQC-watch-list`: Experimental or watch-list names such as `FrodoKEM`, `Classic McEliece`, `BIKE`, `NTRU`, or `SABER`.

Color intent in the report:

- green: strongest current NIST-aligned signal
- amber: specialized or alias naming that still suggests meaningful PQC usage
- blue: experimental or watch-list signal that is relevant but lower-maturity

## PQC Categories

### `KMS_OR_HSM_ASYMMETRIC`

Meaning: KMS, HSM, PKCS#11, or vendor crypto SDK usage tied to managed keys or asymmetric operations.

Why it matters: These findings often indicate dependency-driven migration work with external key managers, HSMs, or crypto platforms.

### `CERTIFICATE_USAGE`

Meaning: Certificate, keystore, truststore, or X.509 related handling.

Why it matters: Certificates and PKI material often require lifecycle, issuance, trust-chain, and deployment planning during PQC migration.

### `TLS_CONFIGURATION`

Meaning: TLS, mTLS, SSL, trust, or protocol-stack configuration.

Why it matters: Transport security settings may need coordinated protocol, certificate, and platform rollout planning.

### `ASYMMETRIC_ALGORITHM`

Meaning: Use of asymmetric algorithms such as RSA or ECC that often drive PQC migration planning.

Why it matters: These algorithms may need replacement, hybrid support, or compatibility review as quantum-safe options are introduced.

### `JWT_OR_TOKEN_SIGNING`

Meaning: JWT, token-signing, or application-signing related logic.

Why it matters: These findings usually point to application-level signing behavior that may require code changes and regression testing.

### `CODE_SIGNING`

Meaning: Code-signing or artifact-signing related usage.

Why it matters: Signing workflows may need updated algorithms, signing services, verification tooling, and rollout coordination.

### `SSH_USAGE`

Meaning: SSH-related crypto or key-exchange usage.

Why it matters: SSH stacks can require protocol and key algorithm review as PQC-capable options mature.

## PQC Migration Classes

### `DEPENDENCY_DRIVEN`

Meaning: Migration impact is strongly tied to libraries, SDKs, KMS, HSM, or platform dependencies.

Why it matters: Often starts with inventory, vendor roadmap review, and dependency upgrade planning.

### `PKI_CERTIFICATE_LIFECYCLE`

Meaning: Certificate lifecycle or PKI management work is likely involved.

Why it matters: May require changes to issuance, renewal, trust distribution, validation, or certificate operations.

### `LOW_RELEVANCE_REFERENCE`

Meaning: Reference-only mention with limited direct implementation ownership.

Why it matters: Useful for awareness, but usually not a primary migration work item by itself.

### `PROTOCOL_STACK`

Meaning: Protocol-stack or transport-layer migration work is indicated.

Why it matters: Usually points to TLS, mTLS, SSH, or other coordinated edge and platform changes rather than only local code edits.

### `CUSTOM_REFACTOR`

Meaning: Custom cryptographic implementation or wrapper behavior is present.

Why it matters: Custom crypto usually needs deeper review because migration is less likely to be solved by a simple library upgrade.

### `APPLICATION_SIGNING`

Meaning: Application-controlled signing or token-signing behavior is present.

Why it matters: Often requires direct code updates, algorithm replacement decisions, and compatibility testing.

### `APPLICATION_KEY_EXCHANGE`

Meaning: Application-level key exchange logic is present.

Why it matters: Usually indicates protocol or handshake logic that may need explicit PQC-aware redesign or hybrid support.

## PQC Recommended Actions

### `review_pqc_dependency_and_kms`

Meaning: Review dependency, SDK, KMS, or HSM migration impact.

Why it matters: Focus on vendor libraries, managed key services, hardware-backed crypto, and roadmap dependencies.

### `review_pqc_application_signing`

Meaning: Review application signing or token-signing logic.

Why it matters: Focus on JWTs, signatures, verification code paths, and compatibility testing.

### `review_pqc_protocol_stack`

Meaning: Review transport protocol stack and related edge configuration.

Why it matters: Focus on TLS, mTLS, SSH, ingress, service-mesh, and certificate distribution concerns.

### `review_pqc_certificate_lifecycle`

Meaning: Review certificate lifecycle and PKI operations.

Why it matters: Focus on issuance, truststores, certificate validation, and deployment coordination.

### `review_pqc_code_signing`

Meaning: Review code-signing and artifact-signing workflows.

Why it matters: Focus on build signing, release verification, and downstream trust consumers.

### `review_pqc_custom_crypto`

Meaning: Review custom cryptographic wrappers or implementations.

Why it matters: Focus on bespoke crypto logic that may need refactoring beyond simple dependency upgrades.

### `review_pqc_manual_assessment`

Meaning: Manual architecture review is recommended.

Why it matters: Use when the scanner sees impact signals but cannot confidently narrow the right remediation lane.

### `reference_only_or_low_priority`

Meaning: Reference-only or low-priority item.

Why it matters: Useful for context and inventory, but usually not a first-wave remediation target.

### `reference_only_frontend`

Meaning: Front-end reference-only mention with low direct migration ownership.

Why it matters: Treat as a pointer to likely backend, platform, or API owners rather than as the primary implementation target.

## PQC File Contexts

### `backend`

Meaning: Back-end implementation code or service logic.

Why it matters: Usually the strongest signal for direct migration ownership and application change work.

### `infrastructure_config`

Meaning: Infrastructure, deployment, or configuration material.

Why it matters: Often important for TLS, mTLS, certificate rollout, or platform coordination work.

### `frontend`

Meaning: Front-end or UI-oriented code.

Why it matters: Often contains certificate or API references, but many PQC changes still land in backend or platform services.

### `docs`

Meaning: Documentation or readme-style reference material.

Why it matters: Useful for awareness and inventory, but often not the primary implementation target.

### `test`

Meaning: Test, example, or validation code.

Why it matters: Helpful for understanding usage patterns, though not always a direct production remediation owner.

## Quick Interpretation

- Categories answer: what crypto-related thing did we find?
- Migration classes answer: what kind of migration work does it imply?
- Recommended actions answer: where should a team start remediation triage?
- File contexts answer: where in the application landscape was this signal found?
