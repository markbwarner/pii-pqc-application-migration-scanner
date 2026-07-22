# Dependency Hint Catalog Maintenance

This file explains how to safely maintain the JSON-backed dependency and vendor hint catalog used by the PQC scanner.

## File Location

The dependency hint catalog lives here:

- `E:\codex\work\migration\config\dependency-hints.json`

The loader lives here:

- `E:\codex\work\migration\scanner\dependency.py`

## What This File Controls

This JSON file controls substring-based dependency and import matching for crypto-relevant categories such as:

- `JWT_OR_TOKEN_SIGNING`
- `SSH_USAGE`
- `KMS_OR_HSM_ASYMMETRIC`
- `CODE_SIGNING`
- `CERTIFICATE_USAGE`

It affects:

- dependency reference categorization
- dependency-derived PQC findings
- CBOM category tagging
- HTML dependency summary tables

## JSON Structure

The file currently has one top-level section:

- `crypto_package_hints`

Each entry maps a category name to a list of case-insensitive substring matches.

Example:

```json
{
  "crypto_package_hints": {
    "KMS_OR_HSM_ASYMMETRIC": [
      "CipherTrust.CADP.NETCore",
      "cloudhsm",
      "Azure.Security.KeyVault.Cryptography"
    ]
  }
}
```

## Safe Editing Tips

- keep the file valid JSON
- use double quotes for all keys and values
- do not leave trailing commas
- prefer specific package or namespace fragments over vague terms
- avoid overly broad terms like `key`, `security`, `crypto`, or `client` by themselves
- add vendor-specific terms only when they are likely to indicate relevant crypto ownership or migration work

## Good Patterns

Good examples:

- `CipherTrust.CADP.NETCore`
- `Azure.Security.KeyVault.Cryptography`
- `cloudhsm_pkcs11`
- `io.github.thalescpl-io.cadp`
- `golang.org/x/crypto/ssh`

Risky examples to avoid:

- `key`
- `client`
- `security`
- `provider`

## Recommended Editing Pattern

1. Identify the package, module, namespace, or header you want the scanner to recognize.
2. Add it to the most appropriate category list in `dependency-hints.json`.
3. Prefer the narrowest useful string that will still match the real package or import.
4. Run the validation command.
5. Confirm the dependency appears in the JSON summary or HTML report under the expected category.

## Validation Command

Use this command after editing the dependency hint catalog:

```powershell
python app.py E:\codex\work\migration\sample_code --scan pqc --json-summary-out E:\codex\work\migration\reports\pqc_vendor_validation_summary.json --quiet
```

If you also want a compile check for the loader, run:

```powershell
python -m compileall E:\codex\work\migration\scanner\dependency.py
```

## Fallback Behavior

If `dependency-hints.json` is missing or malformed, the scanner falls back to built-in defaults in `dependency.py`.

That means:

- scans should still run
- new JSON edits may not show up if the file is invalid
- if behavior does not change after an edit, validate the JSON syntax first

## Suggested Review Workflow

For maintainers adding new vendor SDKs or crypto libraries:

1. Edit `dependency-hints.json`
2. Run the validation command
3. Inspect the report output
4. If needed, add a matching plain-English glossary entry in `dependency-explanations.json`
5. Repeat until the new dependency is categorized correctly
