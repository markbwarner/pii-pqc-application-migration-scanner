# PQC Scanner Positioning Matrix

This matrix is intended to explain where the migration scanner fits relative to CBOM-style tooling and broader crypto discovery scanners.

| Capability | cdxgen / CBOM-style tools | Crypto discovery scanners | Your proposed scanner |
| --- | --- | --- | --- |
| Primary purpose | Produce crypto/component inventory and BOM artifacts | Find cryptographic assets, keys, certs, algorithms, libraries | Explain migration impact in application code |
| Output style | CBOM / CycloneDX, machine-readable inventory | Inventory dashboards, findings, risk lists | File/line findings plus migration worklist |
| Source line attribution | Sometimes partial, often limited | Varies | Core feature |
| Dependency visibility | Strong | Medium to strong | Medium |
| Certificate / keystore discovery | Good | Strong | Good |
| Runtime / network visibility | Weak | Sometimes strong | Weak unless you add integrations |
| Frontend vs backend classification | Usually no | Usually limited | Core feature |
| Distinguish reference vs implementation | Limited | Limited to medium | Core feature |
| PQC migration advice | Usually generic | Medium | Deep, app-specific |
| Estimate level of effort | No | Rarely | Core feature |
| Team ownership / work package grouping | No | Limited | Core feature |
| Thales-specific recommendation logic | No | No | Core feature |
| Best use | Build inventory baseline | Enterprise crypto posture discovery | Application modernization planning |

## How To Read It

- CBOM-style tools are strongest for creating machine-readable component and crypto inventories.
- Enterprise crypto discovery scanners are strongest for broad posture visibility across keys, certificates, services, and cryptographic assets.
- The migration scanner is strongest when teams need file-level attribution, implementation context, estimated effort, and an application modernization worklist.

## Recommended Positioning

Use the tools together when possible:

- use CBOM or CycloneDX-style output to establish inventory and dependency baselines
- use broader crypto discovery to improve enterprise visibility where runtime, certificates, or deployed services matter
- use the migration scanner to translate those signals into concrete application work packages, likely owners, and code-level review priorities
