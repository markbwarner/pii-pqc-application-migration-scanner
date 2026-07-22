# PQC Custom Wrapper Examples

This folder contains example PQC-related config fragments for custom wrappers, custom web-service endpoints, and Swagger-derived draft artifacts.

Purpose:

- show what machine-readable config snippets look like before they are merged into the live config files under `E:\codex\work\migration\config`
- keep copy-and-adapt example JSON near the actual PQC config area instead of under general docs

Subfolders:

- `wrapper-example`
  - example config fragments for direct wrapper-class and helper-method detection
- `webservice-example`
  - example config fragments for abstract service endpoints that eventually route into crypto or CRDP behavior
- `swagger-drafts`
  - generated draft artifacts from raw Swagger input

These examples typically feed or illustrate updates to:

- `cbom-vendor-families.json`
- `dependency-explanations.json`
- `dependency-hints.json`
- `pqc-rules.json`

These are example artifacts, not the live scanner config.

For narrative guidance, see:

- `E:\codex\work\migration\docs\pqc\how-to-add-your-own-security-wrapper.md`
- `E:\codex\work\migration\docs\pqc\how-to-make-a-custom-addition-show-up-in-the-report.md`
