# Application PQC Readiness Scanner Assessment Tool

## Page 1: Find The Real PQC Migration Touchpoints Faster

The Application PQC Readiness Scanner Assessment Tool helps customers find quantum-vulnerable cryptography touchpoints in source code and configuration, determine which files are likely true change owners, and estimate where post-quantum migration work is likely to concentrate.

This is not just a BOM or inventory generator. It is a source-code and dependency assessment tool built for practical migration planning.

It helps answer questions such as:

- Where do RSA, ECC, certificate, TLS, JWT, SSH, KMS, and code-signing patterns appear in code and configuration?
- Are those references only in frontend or documentation files, or in backend services, infrastructure config, and key-management paths that are more likely to require change?
- Which files look like implementation-heavy migration targets versus reference-only or passive dependency evidence?
- How large is the likely delivery and testing effort?

### Top Benefits

- **Migration clarity**
  - Shows where quantum-vulnerable crypto patterns actually sit in application code, dependencies, and config.
- **Better prioritization**
  - Separates frontend awareness, backend implementation, infrastructure configuration, and reference-only artifacts.
- **Actionable planning**
  - Produces per-file findings, likely change targets, complexity ratings, CBOM enrichment, and migration work packages.

### Why This Matters

Many organizations can produce a crypto inventory, but that still leaves the harder question unanswered: which files, services, certificates, and integration points are most likely to drive post-quantum migration effort?

PQC transitions cut across certificate lifecycles, JWT and token signing, mTLS configuration, SSH operations, KMS dependencies, and code-signing workflows. Teams need evidence that maps these concerns back to real files and likely owners.

## Page 2: Executive Summary And How The Scanner Works

The scanner uses source patterns, dependency evidence, and file classification heuristics to find likely post-quantum migration touchpoints.

### What The Scanner Detects

- RSA and ECC algorithm usage
- certificate and keystore handling
- TLS and mTLS configuration
- JWT and token-signing logic
- SSH usage and key-management dependencies
- KMS or HSM asymmetric dependencies
- code-signing workflows
- dependency references and CBOM component evidence across JVM, .NET, npm, Go, and Python ecosystems

### What The Scanner Produces

- per-file PQC findings by category
- per-file PQC migration classes
- likely implementation versus reference-only separation
- recommended change actions such as:
  - `review_pqc_application_signing`
  - `review_pqc_protocol_stack`
  - `review_pqc_dependency_and_kms`
  - `reference_only_frontend`
  - `reference_only_or_low_priority`
- low, medium, and high PQC migration complexity scores
- JSON, CSV, and HTML reporting
- CBOM import and export support

The migration project can now scan:

- `--scan pii`
- `--scan pqc`
- `--scan pii,pqc`

PQC findings retain their own domain, category totals, complexity distribution, and recommended-action summary so they are not hidden inside PII results.

### Executive Summary Snapshot

Current sample PQC results:

```text
Root path: E:\codex\work\migration\sample_code
Scan domains: pqc
Files scanned: 55
Files with findings: 12
Dependency references: 119
Files with PQC indicators: 12
Total PQC findings: 115
PQC likely change targets: 9

Executive summary:
  Dependency enrichment summary:
    - dependency_reference_total: 119
    - cbom_component_total: 82
    - imported_cbom_component_total: 0
  PQC recommended change action summary:
    - reference_only_frontend: 1
    - reference_only_or_low_priority: 2
    - review_pqc_application_signing: 5
    - review_pqc_dependency_and_kms: 1
    - review_pqc_protocol_stack: 3
  PQC category summary:
    - ASYMMETRIC_ALGORITHM: 13
    - CERTIFICATE_USAGE: 49
    - CODE_SIGNING: 6
    - JWT_OR_TOKEN_SIGNING: 23
    - KMS_OR_HSM_ASYMMETRIC: 6
    - SSH_USAGE: 10
    - TLS_CONFIGURATION: 8
  PQC complexity distribution:
    - high: 10
    - medium: 1
    - low: 1
```

This summary helps teams answer not just where crypto appears, but whether the issue is more likely certificate lifecycle work, protocol-stack work, signing modernization, or dependency and KMS/HSM review.

## Page 3: Positioning, Metrics, And Customer Outcome

### Important Output Attributes

- `pqc_summary_by_category`
- `pqc_migration_classes`
- `pqc_likely_change_target`
- `pqc_recommended_change_action`
- `pqc_complexity_rating`
- `pqc_complexity_score`
- `dependency_references`
- `cbom_components`

These fields help teams filter for protocol work, signing work, certificate lifecycle work, and dependency-driven remediation.

### Typical Work Packages

- JWT and application-signing review
- TLS and certificate lifecycle modernization
- KMS or HSM dependency review
- SSH protocol and key-management review
- code-signing workflow review
- reference-only triage for docs and frontend artifacts

### Why Use This Scanner Versus Other Tool Families

Most crypto inventory tools are good at telling you what cryptography exists.

This scanner is designed to help answer the harder delivery question:

- what is most likely to change
- who likely owns the change
- which findings are implementation-heavy versus reference-only
- how to turn the results into a migration worklist

### Expanded Positioning Matrix

| Capability | CBOM / CycloneDX tools | Static analysis frameworks | Network monitoring | Enterprise crypto discovery scanners | This scanner |
| --- | --- | --- | --- | --- | --- |
| Primary purpose | Produce crypto/component inventory and BOM artifacts | Find crypto API usage and coding patterns in source | Observe protocols, cipher suites, and certificates in traffic | Find cryptographic assets, keys, certs, algorithms, libraries | Explain migration impact in application code |
| Best at | Portable inventory and governance | Custom code rules in existing pipelines | Runtime crypto posture | Broad estate visibility | Application migration planning |
| Source line attribution | Sometimes partial, often limited | Often strong | None | Varies | Core feature |
| Distinguish reference vs implementation | Limited | Limited to medium | No | Limited | Core feature |
| Frontend vs backend classification | Usually no | Rarely | No | Usually limited | Core feature |
| Recommended migration actions | No | Rarely | No | Rarely | Core feature |
| Output options | Varies | Varies | Varies | Usually product-specific | JSON, CSV, HTML, and CBOM-aligned workflows |
| Swagger / OpenAPI wrapper onboarding | Rarely | Rarely | No | Rarely | Supported |
| Best use | Build inventory baseline | Add crypto rules to existing developer tooling | Validate deployed protocol posture | Enterprise crypto posture discovery | Application modernization planning |

### Buyer-Friendly Differentiators

- easier to move from findings to planning output
- better file-level prioritization than inventory-first tools
- stronger support for likely change targets and recommended actions
- more useful for multi-tier application analysis
- better fit for Excel, Power Query, BI, and architecture-review workflows
- better support for custom wrappers and OpenAPI-generated clients

### Customer Outcome

Instead of stopping at "we found RSA, certs, and JWT libraries," customers can review concrete evidence showing which files are likely to require implementation change, which items are mostly reference-only, how crypto dependencies map to source files, and where remediation should begin.

The result is faster scoping, clearer ownership conversations, better sequencing of certificate and protocol work, and more practical PQC migration planning across application and infrastructure teams.

