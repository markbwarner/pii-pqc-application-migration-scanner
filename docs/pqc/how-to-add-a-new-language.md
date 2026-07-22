# How To Add A New Language

This scanner adds language support in layers. If you want to add a new language such as Ruby, PHP, Scala, or another ecosystem later, use the steps below.

## 1. Make The Scanner Read The Files

Update [scanner/config.py](E:\codex\work\migration\scanner\config.py).

Add:
- source-file extensions to `SUPPORTED_EXTENSIONS`
- manifest filenames to `SPECIAL_FILENAMES`

Examples:
- Ruby: `.rb`, `.gemspec`, `Gemfile`, `Gemfile.lock`
- Rust: `.rs`, `Cargo.toml`, `Cargo.lock`
- PHP: `.php`, `composer.json`, `composer.lock`
- Scala: `.scala`, `build.sbt`

If this step is skipped, the scanner may never open the files.

## 2. Teach File Classification

Update [scanner/classifiers.py](E:\codex\work\migration\scanner\classifiers.py).

Decide how the new language should be classified:
- backend
- frontend
- infrastructure_config
- docs
- test
- batch_integration
- shared_library

Also decide whether its manifests should behave like infrastructure/config inputs.

Examples:
- Ruby source normally behaves like backend or shared-library code.
- `Gemfile` and `Gemfile.lock` behave like infrastructure/config manifests.
- Scala source usually behaves like backend or shared-library code.
- `build.sbt` behaves like infrastructure/config metadata.

This is what controls the `Layer` and `Context` columns in the report.

## 3. Teach Dependency Extraction

Update [scanner/dependency.py](E:\codex\work\migration\scanner\dependency.py).

This is the most important step for PQC and CBOM support.

Usually you add:
- regexes for imports, requires, `use`, `extern crate`, `using`, and similar syntax
- manifest parsers
- optional source-marker parsing for class names, struct names, wrapper names, route literals, or endpoint hosts

Examples:
- Ruby: `require`, `Gemfile`, `Gemfile.lock`, `.gemspec`, class/module markers
- Rust: `use`, `extern crate`, `Cargo.toml`, `Cargo.lock`, struct/function markers
- PHP: `use`, Composer manifests, class markers
- Scala: `import`, `build.sbt`, object/class markers

If this step is skipped, the language may still trigger raw PQC regex findings, but it will not enrich CBOM or vendor-family output correctly.

## 4. Map Dependencies To Crypto Categories

Update [config/dependency-hints.json](E:\codex\work\migration\config\dependency-hints.json).

This file maps names to crypto-relevant categories such as:
- `JWT_OR_TOKEN_SIGNING`
- `CERTIFICATE_USAGE`
- `TLS_CONFIGURATION`
- `SSH_USAGE`
- `KMS_OR_HSM_ASYMMETRIC`
- `CODE_SIGNING`

If a package, namespace, helper class, route, or endpoint marker should count as crypto-relevant, it needs to be listed here.

If this step is skipped, a dependency may appear in CBOM output but not count as crypto-relevant for PQC analysis.

## 5. Map Dependencies To Vendor / Source Families

Update [config/cbom-vendor-families.json](E:\codex\work\migration\config\cbom-vendor-families.json).

This controls the rollups used in the HTML report, such as:
- `HashiCorp Vault`
- `Akeyless`
- `Thales CADP / CipherTrust`
- `OpenSSL`
- `Bouncy Castle`

Use only real signals for that ecosystem:
- real package names
- real namespaces
- real manifest coordinates
- real product-specific route markers
- real customer wrapper names if the family is intentionally meant to capture them

Important:
A language can support vendor REST usage even if no first-party SDK exists. That does not automatically mean we should model it as a native SDK family signal.

Example:
Rust can call Thales-related REST endpoints, but there is no first-party Thales Rust SDK in this project. Rust REST wrapper samples should remain generic wrapper or REST-usage examples unless a real Rust package exists.

## 6. Add Human-Readable Explanations

Update:
- [config/dependency-explanations.json](E:\codex\work\migration\config\dependency-explanations.json)
- sometimes [scanner/dependency_explanations.py](E:\codex\work\migration\scanner\dependency_explanations.py)

This is what makes the report understandable for non-developers.

You may need to add:
- exact meanings for known package or class names
- partial meanings for useful prefixes
- fallback wording for the new ecosystem

Examples:
- what `vault` means
- what `vaultrs` means
- what `Vault::Client` means
- what a wrapper class implies
- why the dependency matters for PQC migration

## 7. Add Sample Code

Add representative examples under [sample_code](E:\codex\work\migration\sample_code).

A good sample set usually includes:
- one manifest file
- one or more source files
- at least one generic crypto example
- at least one vendor-family example
- at least one app-owned wrapper or endpoint-driven example if that pattern is common in customer code

Examples:
- Ruby: `Gemfile`, Vault example, Akeyless example, CipherTrust REST-wrapper example
- Rust: `Cargo.toml`, Vault crate example, Akeyless crate example, generic managed-crypto REST-wrapper example

The sample set is the quickest way to prove the support actually works.

## 8. Update Sample Documentation

Update [sample_code/README.md](E:\codex\work\migration\sample_code\README.md).

Document:
- what you added
- what the report should show
- which sample files should surface
- whether the language has real SDK coverage or only REST-wrapper coverage for a given vendor

This helps future validation and prevents confusion.

## 9. Run Validation

Run a PQC scan and inspect the output.

Example command:

```powershell
python E:\codex\work\migrationpp.py E:\codex\work\migration\sample_code --scan pqc --html-out E:\codex\work\migrationeports\language_validation.html --quiet
```

Then confirm:
- the new ecosystem appears in `Observed Unique CBOM By Ecosystem`
- sample files appear in `File Findings`
- vendor-family totals move in expected ways
- generic REST wrappers are not being mislabeled as first-party SDK usage
- explanations in the report still read clearly for security and architecture audiences

## Practical Checklist

Use this checklist each time:

1. Update [scanner/config.py](E:\codex\work\migration\scanner\config.py).
2. Update [scanner/classifiers.py](E:\codex\work\migration\scanner\classifiers.py).
3. Update [scanner/dependency.py](E:\codex\work\migration\scanner\dependency.py).
4. Update [config/dependency-hints.json](E:\codex\work\migration\config\dependency-hints.json).
5. Update [config/cbom-vendor-families.json](E:\codex\work\migration\config\cbom-vendor-families.json).
6. Update [config/dependency-explanations.json](E:\codex\work\migration\config\dependency-explanations.json).
7. Add or update samples under [sample_code](E:\codex\work\migration\sample_code).
8. Update [sample_code/README.md](E:\codex\work\migration\sample_code\README.md).
9. Run a validation scan and inspect the HTML output.

## Design Rule To Keep In Mind

Keep these three things separate:
- language support
- vendor-family support
- generic REST endpoint detection

A language may legitimately call a vendor service through REST without having a native vendor SDK. That should be represented honestly in the scanner so the report stays trustworthy.
