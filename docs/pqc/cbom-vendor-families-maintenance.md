# CBOM Vendor Family Maintenance

This file explains how to safely maintain the JSON-backed vendor or source-family grouping used by the PQC HTML report.

## File Location

The vendor-family catalog lives here:

- `E:\codex\work\migration\config\cbom-vendor-families.json`

The report loader and classifier live here:

- `E:\codex\work\migration\scanner\html_reporting.py`

## What This File Controls

This JSON file controls the `Observed CBOM By Vendor / Source Family` rollup in the HTML report.

It affects:

- vendor/source-family summary counts
- the `Top Remaining Other / General Components` table
- the plain-English metric legend text for vendor/source-family grouping

It does not change:

- raw dependency detection
- PQC finding generation
- CBOM component totals
- scan scoring

## JSON Structure

The file has two top-level sections:

- `vendor_families`
- `fallback_label`

Each `vendor_families` item contains:

- `label`
- `patterns`

Example:

```json
{
  "vendor_families": [
    {
      "label": "Thales CM REST",
      "patterns": [
        "com.thales.cm.rest.cmhelper",
        "ciphertrustmanagerhelper",
        "cmrestprotect"
      ]
    }
  ],
  "fallback_label": "Other / General"
}
```

## How Matching Works

Matching is case-insensitive substring matching against the observed CBOM component name.

The first matching family wins.

That means ordering matters.

Example:

- put `Thales CM REST` before broader `Thales CADP / CipherTrust`
- put `Oracle GoldenGate` before broad Oracle or Thales-related catch-alls
- put narrow product families before generic technology families like `Certificate / PKI` or `Language Runtime Crypto`

## Safe Editing Tips

- keep the file valid JSON
- use double quotes for all keys and values
- do not leave trailing commas
- prefer narrow product or SDK markers over broad words
- order more specific families before more general families
- avoid generic patterns like `security`, `provider`, `helper`, or `client` by themselves

## Good Patterns

Good examples:

- `com.thales.cm.rest.cmhelper`
- `managedhsm.azure.net`
- `kmsmanagementclient`
- `com.google.cloud.kms.v1.keymanagementserviceclient`
- `cloudhsm_pkcs11`

Risky examples to avoid:

- `helper`
- `client`
- `key`
- `security`
- `crypto`

## Recommended Editing Pattern

1. Identify the exact observed CBOM component names you want to regroup.
2. Add a new family or extend an existing family in `cbom-vendor-families.json`.
3. Place narrow product-specific rules before broad catch-all rules.
4. Run the validation command.
5. Confirm the family appears in the HTML report as expected.
6. Check that unrelated components did not move into the new family by accident.

## Validation Command

Use this command after editing the vendor-family catalog:

```powershell
python app.py E:\codex\work\migration\sample_code --scan pqc --html-out E:\codex\work\migration\reports\sample_code_vendor_family_check.html --quiet
```

## Fallback Behavior

If `cbom-vendor-families.json` is missing or malformed, the report falls back to the built-in default catalog in Python.

That means:

- report generation should still work
- your new JSON edits may not appear if the file is invalid
- if a family does not move as expected, validate the JSON syntax first

## Suggested Review Workflow

For maintainers adding or refining families:

1. Edit `cbom-vendor-families.json`
2. Run the validation command
3. Review `Observed CBOM By Vendor / Source Family`
4. Review `Top Remaining Other / General Components`
5. Repeat until the grouping reads clearly for security and architecture stakeholders
