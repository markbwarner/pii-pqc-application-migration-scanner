# How To Add Your Own Security Wrapper

Many organizations do not call a vendor SDK directly from business code. Instead, they create a local helper or wrapper such as `CipherTrustManagerHelper` and expose a smaller set of application-facing methods like:

- `cmRESTProtect(..., "encrypt")`
- `cmRESTProtect(..., "decrypt")`
- `cmRESTSign(..., "sign")`
- `cmRESTSign(..., "signv")`
- `cmRESTMac(..., "mac")`
- `cmRESTMac(..., "macv")`

That pattern is important for this scanner because the application code may never import the underlying crypto SDK directly. The scanner therefore needs to recognize the wrapper layer itself.

This guide shows how to add that support safely using the existing JSON-backed config in this project.

## Files You Will Edit

For wrapper detection, these are the main files:

- `E:\codex\work\migration\config\dependency-hints.json`
- `E:\codex\work\migration\config\dependency-explanations.json`
- `E:\codex\work\migration\config\pqc-rules.json`

These maintenance guides are also useful:

- `E:\codex\work\migration\docs\pqc\dependency-hints-maintenance.md`
- `E:\codex\work\migration\docs\pqc\dependency-explanations-maintenance.md`
- `E:\codex\work\migration\docs\pqc\pqc-rules-maintenance.md`

## What To Capture From A Customer Wrapper

Before editing config, collect the narrow identifiers that are unique to the customer wrapper.

From your example, good identifiers are:

- package: `com.thales.cm.rest.cmhelper`
- wrapper class: `CipherTrustManagerHelper`
- wrapper methods: `cmRESTProtect`, `cmRESTSign`, `cmRESTMac`
- service routes: `/api/v1/crypto/encrypt`, `/api/v1/crypto/decrypt`, `/api/v1/crypto/sign`, `/api/v1/crypto/signv`, `/api/v1/crypto/mac`, `/api/v1/crypto/macv`
- key metadata route: `/api/v1/vault/keys2/`
- keystore usage: `java.security.KeyStore`

Avoid broad terms such as:

- `protect`
- `sign`
- `verify`
- `client`
- `security`

Those are too generic and will create false positives.

## Step 1: Add Wrapper Hints

Edit `dependency-hints.json` first.

Where to add them:

- add wrapper APIs and REST routes under `KMS_OR_HSM_ASYMMETRIC`
- add keystore or certificate loader types under `CERTIFICATE_USAGE` when the wrapper manages truststores, wallets, or certificates

Example pattern from your wrapper:

```json
{
  "crypto_package_hints": {
    "KMS_OR_HSM_ASYMMETRIC": [
      "com.thales.cm.rest.cmhelper",
      "CipherTrustManagerHelper",
      "cmRESTProtect",
      "cmRESTSign",
      "cmRESTMac",
      "/api/v1/crypto/encrypt",
      "/api/v1/crypto/decrypt",
      "/api/v1/crypto/sign",
      "/api/v1/crypto/signv",
      "/api/v1/crypto/mac",
      "/api/v1/crypto/macv",
      "/api/v1/vault/keys2/"
    ],
    "CERTIFICATE_USAGE": [
      "java.security.KeyStore"
    ]
  }
}
```

Why this matters:

- `KMS_OR_HSM_ASYMMETRIC` is the best existing home for managed-service wrapper calls because the app is delegating crypto to an external service
- `CERTIFICATE_USAGE` should be used when the helper also loads truststores, keystores, wallets, or certificate chains

## Step 2: Add Plain-English Explanations

Edit `dependency-explanations.json` so security teams can understand what the wrapper identifiers mean in the HTML report.

Use `exact_meanings` for specific class or method names.

Example:

```json
{
  "exact_meanings": {
    "com.thales.cm.rest.cmhelper": "Java package for a customer-facing Thales CipherTrust REST helper that wraps encryption, signing, MAC, and token calls behind simpler application APIs.",
    "ciphertrustmanagerhelper": "Customer-style Thales CipherTrust REST wrapper class that centralizes key selection, token handling, and crypto API calls behind helper methods.",
    "cmrestprotect": "Wrapper method that hides Thales CipherTrust encrypt or decrypt REST calls behind a single application-facing API.",
    "cmrestsign": "Wrapper method that hides Thales CipherTrust sign or verify REST calls behind a simplified application-facing API.",
    "cmrestmac": "Wrapper method that hides Thales CipherTrust MAC or MAC-verify REST calls behind a simplified application-facing API."
  }
}
```

You can also add exact explanations for route fragments when they appear in dependency or CBOM sections.

## Step 3: Extend PQC Detection Rules

Edit `pqc-rules.json` so file-level findings are created when wrapper-owned methods appear in application code.

For this style of helper, the existing `KMS_OR_HSM_ASYMMETRIC` rule is the right place.

Example addition to the regex pattern:

```json
{
  "category": "KMS_OR_HSM_ASYMMETRIC",
  "pattern": "...|CipherTrustManagerHelper|cmRESTProtect|cmRESTSign|cmRESTMac|/api/v1/crypto/(?:encrypt|decrypt|sign|signv|mac|macv)|/api/v1/vault/keys2/"
}
```

Why this works:

- application code that only calls `cmRESTSign(...)` can still be flagged as PQC-relevant even if the low-level SDK call is hidden inside the helper
- the scanner can now treat the wrapper as a likely implementation ownership point instead of missing it entirely

## Step 4: Decide Whether The Wrapper Implies Other Categories

Some wrappers only do symmetric encryption. Others also do:

- RSA signing
- certificate or truststore loading
- TLS client authentication
- JWT signing
- HSM or KMS key lookups

Use the wrapper internals to decide whether you also need to extend other categories.

For your `CipherTrustManagerHelper`, these internals matter:

- `cmRESTSign(..., "sign")` and `cmRESTSign(..., "signv")` indicate managed signing and signature verification
- `getKeySize()` and `/api/v1/vault/keys2/` indicate managed key metadata lookup
- `KeyStore`, `TrustManagerFactory`, and `SSLContext` indicate keystore and TLS certificate handling
- comments and examples referring to `rsa` indicate asymmetric algorithm ownership

Usually the rule of thumb is:

- if the wrapper exposes or selects signing algorithms, add wrapper indicators to PQC findings
- if the wrapper loads keystores or certs, make sure those classes are covered under `CERTIFICATE_USAGE`
- if the wrapper configures TLS or mTLS, confirm the existing `TLS_CONFIGURATION` patterns already catch the implementation

## Step 5: Validate On Realistic Code

Run the scanner against code that uses the wrapper.

Example command:

```powershell
python E:\codex\work\migration\app.py E:\codex\work\migration\sample_code --scan pqc --html-out E:\codex\work\migration\reports\wrapper_validation_report.html --json-out E:\codex\work\migration\reports\wrapper_validation_report.json --quiet
```

If you also want a quick syntax check of the scanner modules:

```powershell
python -m compileall E:\codex\work\migration\scanner
```

Then review the output for:

- new PQC findings in files that call the wrapper
- CBOM or dependency references for the wrapper class or package
- correct category placement under managed crypto, certificates, or TLS
- no obvious false positives in unrelated files

## Step 6: Tune To Reduce False Positives

If the scanner becomes noisy, tighten the config.

Good tuning actions:

- keep wrapper identifiers fully qualified when possible
- prefer `CipherTrustManagerHelper` over `Helper`
- prefer `cmRESTSign` over `sign`
- prefer exact REST route fragments over generic words like `crypto`
- only add a partial glossary match if multiple customer wrappers share the same stable naming pattern

Bad tuning actions:

- adding `protect` by itself
- adding `verify` by itself
- adding `token` by itself
- adding `ssl` everywhere without checking context

## Recommended Customer Onboarding Workflow

When onboarding a new customer wrapper, use this checklist:

1. Read one application file that calls the wrapper and one helper file that implements it.
2. List the narrow wrapper identifiers.
3. Add those identifiers to `dependency-hints.json`.
4. Add plain-English explanations to `dependency-explanations.json`.
5. Extend the most appropriate regex in `pqc-rules.json`.
6. Run the PQC scan.
7. Review the HTML report for findings, CBOM entries, and dependency references.
8. Tighten the patterns if unrelated files start matching.

## How This Maps To Your Example

From `E:\eclipse-workspace\com.thales.cm.rest.helper\src\main\java\com\thales\cm\rest\cmhelper\App.java`, the main application-facing calls are:

```java
results = awsresrest.cmRESTProtect("gcm", sensitive, "encrypt");
results = awsresrest.cmRESTProtect("gcm", results, "decrypt");
results = awsresrest.cmRESTSign("SHA1", "na", sensitive, "sign");
results = awsresrest.cmRESTSign("SHA1", results, sensitive, "signv");
```

That means the scanner should treat this wrapper as:

- managed crypto ownership
- possible asymmetric signing ownership
- possible certificate or TLS ownership if the helper also loads keystores or trust material

And from `CipherTrustManagerHelper.java`, the underlying implementation confirms:

- managed REST crypto endpoints are being called
- key metadata is retrieved from a managed service
- Java keystore and TLS trust manager APIs are involved

## What Has Already Been Added In This Repo

The current migration config has already been updated to recognize this wrapper style with:

- `com.thales.cm.rest.cmhelper`
- `CipherTrustManagerHelper`
- `cmRESTProtect`
- `cmRESTSign`
- `cmRESTMac`
- `/api/v1/crypto/encrypt`
- `/api/v1/crypto/decrypt`
- `/api/v1/crypto/sign`
- `/api/v1/crypto/signv`
- `/api/v1/crypto/mac`
- `/api/v1/crypto/macv`
- `/api/v1/vault/keys2/`
- `java.security.KeyStore`

That gives you a good starter pattern for adding similar customer-owned wrapper layers going forward.
