# Dependency Explanations JSON Maintenance

This file explains how to safely maintain the JSON-backed glossary used by the PQC HTML report.

## File Location

The glossary content lives here:

- `E:\codex\work\migration\config\dependency-explanations.json`

The report loader lives here:

- `E:\codex\work\migration\scanner\dependency_explanations.py`

The HTML report renderer that uses the glossary lives here:

- `E:\codex\work\migration\scanner\html_reporting.py`

## What This File Controls

The JSON file provides plain-English explanations for package names, classes, modules, and APIs that appear in PQC dependency and CBOM report sections.

It drives the following report columns:

- `Meaning`
- `Why It Matters`

## JSON Structure

The file currently has three sections:

- `exact_meanings`
- `partial_meanings`
- `category_why`

### `exact_meanings`

Use this for exact package, class, or module matches.

Example:

```json
"io.jsonwebtoken.signaturealgorithm": "Java JJWT type used to select token-signing algorithms such as RSA or HMAC variants."
```

Guidelines:

- use lowercase keys
- be specific and factual
- prefer one sentence
- explain what the item is, not every possible use of it

### `partial_meanings`

Use this for substring-based fallback matching when an exact match is not present.

Example:

```json
{
  "match": "x509",
  "meaning": "Certificate-related API or library for working with X.509 certificates or trust chains."
}
```

Guidelines:

- keep these broad enough to be useful, but not so broad they cause misleading matches
- use these only for stable concepts like `x509`, `jwt`, `tls`, `ssh`, `kms`
- avoid vague matches like `key`, `auth`, `security`, or `client`

### `category_why`

Use this to explain why a category matters from a PQC migration perspective.

Example:

```json
"CERTIFICATE_USAGE": "May indicate certificate lifecycle, trust-chain, keystore, or mTLS work that needs post-quantum planning."
```

Guidelines:

- keep this language business-readable
- focus on migration impact, not implementation detail
- these values are reused across many findings

## Safe Editing Tips

- keep the file valid JSON at all times
- use double quotes for all keys and string values
- do not leave trailing commas
- keep exact-match keys lowercase so lookup remains consistent
- prefer adding exact matches before adding new partial matches
- when in doubt, use wording that is precise and conservative rather than broad marketing language

## Recommended Editing Pattern

1. Find a package or class in the HTML report that needs a clearer explanation.
2. Check whether it already has an exact match in `exact_meanings`.
3. If not, add an exact match first.
4. Only add or change a `partial_meanings` rule if multiple related items need the same fallback wording.
5. Rerun the validation command and inspect the HTML report.

## Good Examples

Good exact entry:

```json
"system.security.cryptography.pkcs": ".NET library for PKCS/CMS message handling and certificate-based signing workflows."
```

Good partial entry:

```json
{
  "match": "jwt",
  "meaning": "JWT-related library or API used for token issuing, validation, or signing."
}
```

Good category explanation:

```json
"SSH_USAGE": "May indicate SSH protocol or SSH key-management usage that should be reviewed for post-quantum readiness."
```

## Examples To Avoid

Too vague:

```json
{
  "match": "key",
  "meaning": "Security-related thing."
}
```

Too broad and misleading:

```json
{
  "match": "client",
  "meaning": "Client used for cryptography."
}
```

Too implementation-heavy for report readers:

```json
"io.jsonwebtoken.signaturealgorithm": "This enum selects the JWS algorithm and is consumed by the builder chain before serialization."
```

## Validation Command

Use this command after editing the JSON file:

```powershell
python app.py E:\codex\work\migration\sample_code --scan pqc --html-out E:\codex\work\migration\reports\phase2_validation_pqc_report.html --quiet
```

Then review:

- `E:\codex\work\migration\reports\phase2_validation_pqc_report.html`

If you want to also compile-check the loader code, run:

```powershell
python -m compileall E:\codex\work\migration\scanner\dependency_explanations.py E:\codex\work\migration\scanner\html_reporting.py
```

## Fallback Behavior

If the JSON file is missing or malformed, the loader currently falls back to built-in defaults in Python.

That means:

- report generation should still work
- your new JSON edits may not appear if the file is invalid
- if the wording does not change after an edit, check the JSON syntax first

## Suggested Review Workflow

For security architects or non-developers:

1. Edit `dependency-explanations.json`
2. Run the validation command
3. Open the HTML report
4. Confirm the wording is accurate and understandable
5. Repeat until the explanation reads well for both technical and non-technical reviewers
