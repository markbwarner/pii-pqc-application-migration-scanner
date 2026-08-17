# PQC Scanner Positioning Matrix

This matrix is intended to explain where the migration scanner fits relative to CBOM-style tooling, static-analysis frameworks, network monitoring, simple scanners, and broader crypto discovery scanners.

## Vendor / Tool Family Matrix

| Capability | CBOM / CycloneDX tools | Static analysis frameworks and queries | Network crypto monitoring | Simple code scanners | Enterprise crypto discovery scanners | Your proposed scanner |
| --- | --- | --- | --- | --- | --- | --- |
| Primary purpose | Produce crypto/component inventory and BOM artifacts | Find crypto API usage and coding patterns in source | Observe protocols, cipher suites, certificates, and crypto behavior in traffic | Fast first-pass keyword search for crypto terms | Find cryptographic assets, keys, certs, algorithms, libraries, and exposure | Explain migration impact in application code |
| Typical examples | CycloneDX CBOM, CBOMkit output | CodeQL, SonarQube plugins, custom static rules | Zeek and similar telemetry tooling | grep-style scans, simple scripts | Commercial inventory and discovery products | Application PQC readiness scanner |
| Output style | CBOM / CycloneDX, machine-readable inventory | Findings, query results, sometimes CBOM export | Logs, protocol inventories, dashboards | Match lists, quick hit reports | Inventory dashboards, findings, risk lists | File/line findings plus migration worklist |
| Source line attribution | Sometimes partial, often limited | Often strong | None | Sometimes line-based but shallow | Varies | Core feature |
| Dependency visibility | Strong | Medium | Weak | Weak | Medium to strong | Strong enough for planning and enriched by CBOM evidence |
| Runtime / network visibility | Weak | Weak | Strong | None | Sometimes strong | Weak unless you add integrations |
| Certificate / keystore discovery | Good | Medium | Medium to strong for observed certs | Weak | Strong | Good |
| Frontend vs backend classification | Usually no | Rarely | No | No | Usually limited | Core feature |
| Distinguish reference vs implementation | Limited | Limited to medium | No | No | Limited to medium | Core feature |
| Likely change-owner identification | No | Rarely | No | No | Rarely | Core feature |
| Work package / recommended action output | No | Rarely | No | No | Rarely | Core feature |
| PQC migration advice | Usually generic | Generic to medium | Generic | None | Medium | Deep, app-specific |
| Estimate level of effort | No | No | No | No | Rarely | Core feature |
| Import or ingest CBOM | Sometimes native | Sometimes via extension | No | No | Varies | Supported |
| Swagger / OpenAPI wrapper onboarding | Rarely | Rarely | No | No | Rarely | Supported |
| JSON / CSV / HTML reporting | Varies | Varies | Varies | Usually minimal | Usually product-specific | Core feature |
| Best use | Build inventory baseline | Find crypto usage patterns and API calls | Validate deployed network crypto posture | Quick low-cost first pass | Enterprise-wide posture discovery | Application modernization planning |

## Why A Team Would Pick This Scanner First

The scanner is strongest when the customer's real question is not just "where does cryptography exist?" but:

- which files are likely true migration owners
- which findings are only references versus implementation-heavy
- which back-end services are more important than front-end references
- which recommended action should happen first
- how large the migration and testing effort is likely to be

That is the gap between inventory and planning.

## How To Read It

- CBOM-style tools are strongest for portable, machine-readable component and crypto inventories.
- Static analysis frameworks are strong when teams want customizable detection logic inside existing code-scanning platforms.
- Network monitoring is strongest when runtime TLS, certificate, or cipher-suite observation matters.
- Simple scanners are useful for a fast, inexpensive first pass.
- Enterprise crypto discovery scanners are strongest for broad posture visibility across keys, certificates, services, and deployed assets.
- The migration scanner is strongest when teams need file-level attribution, implementation context, estimated effort, ownership hints, and an application modernization worklist.

## Recommended Positioning

Use the tools together when possible:

- use CBOM or CycloneDX-style output to establish inventory and dependency baselines
- use static analysis frameworks when customers already operate CodeQL, SonarQube, or similar engines and want additional crypto rules
- use network monitoring where runtime, certificates, or deployed services matter
- use broader crypto discovery to improve enterprise visibility across assets and environments
- use the migration scanner to translate those signals into concrete application work packages, likely owners, recommended actions, and code-level review priorities
