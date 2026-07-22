# How To Make A Custom Addition Show Up In The Report

This guide explains all the steps needed when you add a new customer wrapper, crypto SDK, or vendor-specific pattern and want it to show up clearly in the scanner output.

## The Important Idea

There are three separate report layers:

1. File-level PQC findings
2. Observed dependency and CBOM components
3. Vendor or source-family rollups in the HTML report

A new addition may appear in one layer without appearing in the others.

Example:

- a file can produce PQC findings from regex matches
- but if the scanner does not observe a real import, package, include, or manifest dependency, it may not create a visible CBOM component
- and if there is no observed CBOM component, the vendor-family summary may stay empty or small

## What You Usually Need To Update

For most custom additions, these are the files to review:

- `E:\codex\work\migration\config\dependency-hints.json`
- `E:\codex\work\migration\config\dependency-explanations.json`
- `E:\codex\work\migration\config\pqc-rules.json`
- `E:\codex\work\migration\config\cbom-vendor-families.json`

## What Each File Does

### `dependency-hints.json`

Use this when you want dependency enrichment to recognize a package, import, include, header, namespace, or wrapper name as crypto-relevant.

This affects:

- dependency references
- CBOM component enrichment
- some dependency-derived PQC findings

### `dependency-explanations.json`

Use this when you want the report to explain a package or class in plain English.

This affects:

- `Meaning`
- `Why It Matters`

### `pqc-rules.json`

Use this when you want the file itself to produce PQC findings from code content.

This affects:

- file-level PQC findings
- category counts
- complexity scoring inputs
- likely change-target behavior

### `cbom-vendor-families.json`

Use this when you want observed CBOM components to roll up under a specific label such as:

- `Thales CM REST`
- `Thales CADP / CipherTrust`
- `Oracle GoldenGate`
- `Oracle OCI KMS`
- `Voltage`

This only works if the scanner actually observes a component name that matches the configured patterns.

## Full Step-By-Step Process

### Step 1: Identify what is visible in code

Look for the exact names the scanner can realistically observe.

Good examples:

- Java package names
- Java imports
- .NET `using` namespaces
- Python imports
- JS or TS imports
- Go imports
- C or C++ includes
- Maven, NuGet, npm, Go, or Python manifest dependency names
- distinctive wrapper method names when used in code

Avoid relying only on comments or broad words.

## Step 2: Add dependency hints

Add the relevant names to `dependency-hints.json` under the most appropriate category.

Example uses:

- SDK package names
- wrapper class names
- distinctive REST helper method names
- header names
- provider names

This helps the scanner treat those imports or dependencies as crypto-relevant.

## Step 3: Add file-level PQC rules

If you want files to show PQC findings even when the dependency signal is weak, add or extend patterns in `pqc-rules.json`.

Use this for:

- wrapper method calls
- algorithm strings
- provider APIs
- TLS or certificate handling logic
- KMS or HSM operations

This is what makes a file show up in the PQC findings table.

## Step 4: Add plain-English explanations

Add exact or partial explanation entries in `dependency-explanations.json`.

This helps non-developers understand what the dependency or API means in the report.

## Step 5: Add a vendor-family mapping

Add or extend a family in `cbom-vendor-families.json`.

Example:

```json
{
  "label": "Thales CM REST",
  "patterns": [
    "com.thales.cm.rest.cmhelper",
    "ciphertrustmanagerhelper",
    "cmrestprotect"
  ]
}
```

This does not create a component by itself. It only groups components that were already observed.

## Step 6: Make sure the scanner can observe a real component name

This is the part that causes the most confusion.

If you want a new addition to show up in the CBOM or vendor-family summary, the scanned code must contain something the dependency extractor can observe.

Examples that work well:

- `import com.thales.cm.rest.cmhelper.CipherTrustManagerHelper;`
- `using CipherTrust.CADP.NETCore;`
- `require('@aws-sdk/client-kms')`
- `#include <pkcs11.h>`
- a Maven dependency in `pom.xml`
- a NuGet `PackageReference`
- a Python requirement in `requirements.txt`

If the code only contains generic business logic and never exposes an import, package, include, or manifest dependency, the file may still get PQC findings but may not produce a visible CBOM component.

## Step 7: Add a small sample if needed

If you want stable validation, add a small sample file under `sample_code` that includes the exact import, package, or dependency name you want to surface.

This is often the easiest way to make a custom addition visible in:

- CBOM output
- vendor-family rollups
- report examples

## Step 8: Run the scan and verify all three layers

Use a validation command like this:

```powershell
python E:\codex\work\migration\app.py E:\codex\work\migration\sample_code --scan pqc --html-out E:\codex\work\migration\reports\custom_addition_check.html --json-out E:\codex\work\migration\reports\custom_addition_check.json --quiet
```

Then verify:

1. The file has PQC findings
2. The dependency or component appears in JSON or HTML output
3. The vendor/source family row appears under the expected label

## When You Need To Change Code

You do need to change code or sample code when the scanner has no observable dependency or component name to work with.

That is why `Thales CM REST` needed a real observed component such as:

- `com.thales.cm.rest.cmhelper.CipherTrustManagerHelper`

Without that observable import or package-style name, the vendor-family config had nothing concrete to group.

## Why Some Families Stay Small

A family can be correctly configured but still look small in the summary if the sample corpus only contains one or two distinct observed components for that family.

That is what happened with Oracle GoldenGate:

- classifier support existed
- but the Oracle OCI and Oracle PKI samples had more observed components
- so GoldenGate was less prominent in the rollup

That is not necessarily a bug. It just reflects what the scan actually observed.

## Fast Checklist

Use this checklist for every custom addition:

1. Add dependency hints
2. Add PQC rule coverage if file findings are needed
3. Add plain-English explanations
4. Add vendor-family mapping if summary grouping is needed
5. Confirm the scanned code exposes a real import, include, package, or manifest dependency
6. Add a sample if needed
7. Run the validation scan
8. Check findings, CBOM, and vendor-family output

## Rule Of Thumb

- If you only want file findings, update rules and hints.
- If you want CBOM visibility, the code must expose an observable component name.
- If you want a named vendor bucket, you also need a matching family rule.
- If you want a repeatable demo, add a small sample file.

## Recommended Validation Command

```powershell
python E:\codex\work\migration\app.py E:\codex\work\migration\sample_code --scan pqc --html-out E:\codex\work\migration\reports\custom_addition_check.html --json-out E:\codex\work\migration\reports\custom_addition_check.json --quiet
```
