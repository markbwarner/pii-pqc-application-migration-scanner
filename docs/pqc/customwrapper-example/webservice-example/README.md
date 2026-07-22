# Custom Web Service Example

This example shows how to model a CRDP-backed web service where the public route names are more abstract than the lower-level protect or reveal APIs.

Example style:

- front-end or caller-facing routes such as `/protectInput`, `/revealInput`, and `/protectInputAndCallLLM`
- a backend Java service class such as `ThalesGCPProtectServerOpenAI`
- authentication and gateway logic in a Spark Java service
- a backend implementation that still routes into Thales CRDP behavior

Use these examples as snippets to merge into the main config files:

- [cbom-example.json](E:/codex/work/migration/config/pqc/examples/customwrapper-example/webservice-example/cbom-example.json)
- [dependency-explanations-example.json](E:/codex/work/migration/config/pqc/examples/customwrapper-example/webservice-example/dependency-explanations-example.json)
- [dependency-hints-example.json](E:/codex/work/migration/config/pqc/examples/customwrapper-example/webservice-example/dependency-hints-example.json)
- [pqc-rules-example.json](E:/codex/work/migration/config/pqc/examples/customwrapper-example/webservice-example/pqc-rules-example.json)

Recommended use:

1. Put route literals and abstract endpoint names into `pqc-rules.json` if you want them to create PQC findings.
2. Put helper classes, provider classes, service classes, and package names into `dependency-hints.json` if you want dependency enrichment to connect them to `KMS_OR_HSM_ASYMMETRIC`.
3. Put the same stronger implementation identifiers into `cbom-vendor-families.json` if you want them to contribute to `Custom Thales CRDP` or a similar vendor/source family.

Important caveat:

- route strings are good for PQC detection
- imports, helper classes, provider classes, and stable implementation identifiers are better for vendor/source rollups and CBOM-style grouping

That means a route like `/protectInput` is useful, but identifiers like `ThalesGCPProtectServerOpenAI`, `CentralManagementProvider`, `CryptoManager`, or a custom CRDP gateway helper are stronger evidence of real backend CRDP integration.
