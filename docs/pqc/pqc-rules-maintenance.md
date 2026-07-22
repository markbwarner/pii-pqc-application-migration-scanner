# PQC Rule Catalog Maintenance

This file explains how to safely maintain the JSON-backed PQC rule catalog used by the scanner.

## File Location

The PQC rule catalog lives here:

- `E:\codex\work\migration\config\pqc-rules.json`

The loader and scan engine live here:

- `E:\codex\work\migration\scanner\pqc.py`

## What This File Controls

This JSON file controls the static PQC detection rule catalog used during per-line scanning.

Each rule defines:

- `category`
- `algorithm`
- `migration_class`
- `severity`
- `confidence`
- `pattern`

It affects:

- PQC file findings
- category summaries
- per-file complexity scoring inputs
- recommended change target identification

## JSON Structure

The file currently has one top-level section:

- `pqc_rules`

Each entry is a rule object.

Example:

```json
{
  "category": "KMS_OR_HSM_ASYMMETRIC",
  "algorithm": "KMS/HSM",
  "migration_class": "DEPENDENCY_DRIVEN",
  "severity": "high",
  "confidence": 0.85,
  "pattern": "CloudHSM|ManagedHsm|PKCS11"
}
```

## Safe Editing Tips

- keep the file valid JSON
- use double quotes for all keys and string values
- do not leave trailing commas
- keep regex patterns specific enough to avoid noisy matches
- prefer extending an existing category before inventing a new one unless the scanner engine is also being updated
- be careful with escaping backslashes inside regex strings

## Recommended Editing Pattern

1. Identify the code, config, or dependency pattern you want to detect.
2. Decide whether it belongs in an existing rule or a new rule.
3. Add or update the JSON entry in `pqc-rules.json`.
4. Run the validation command.
5. Check that findings land in the right category and do not create obvious false positives.

## Validation Command

Use this command after editing the PQC rule catalog:

```powershell
python app.py E:\codex\work\migration\sample_code --scan pqc --json-summary-out E:\codex\work\migration\reports\pqc_vendor_validation_summary.json --quiet
```

If you also want a compile check for the loader, run:

```powershell
python -m compileall E:\codex\work\migration\scanner\pqc.py
```

## Fallback Behavior

If `pqc-rules.json` is missing or malformed, the scanner falls back to built-in defaults in `pqc.py`.

That means:

- scans should still run
- new JSON edits may not show up if the file is invalid
- if detection behavior does not change after an edit, validate the JSON syntax first

## What Stays In Code

The following still remain in Python by design:

- finding kind classification
- complexity scoring
- likely change target logic
- recommended action mapping

This keeps the catalog data-driven without turning business logic into configuration.
