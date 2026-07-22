# External Test Corpus Recommendations

## Purpose

This guide lists external public repositories and source collections that are useful for testing the migration scanner against a broader and more realistic set of code patterns than the local `sample_code` folder alone.

The goal is not to treat every repository as production truth. The goal is to build a curated validation corpus that helps test:

- PII detection behavior
- PQC and legacy-crypto detection behavior
- dependency enrichment
- vendor and source-family grouping
- frontend vs backend vs config vs docs classification
- implementation vs reference-only separation
- false-positive reduction

## Recommended Strategy

Use a **small curated set** of high-signal repositories rather than cloning random security repos.

A good validation corpus should include:

- mainstream crypto libraries
- PQC-focused repos
- cloud KMS and signing samples
- KMIP and HSM examples
- secret-management examples
- docs-heavy or reference-heavy repos to test reference-only handling
- multiple languages including `C`, `.NET`, `Java`, `Go`, `Python`, JavaScript, and shell scripts

## Recommended Repositories

### 1. Open Quantum Safe `liboqs`

- Repository: [https://github.com/open-quantum-safe/liboqs](https://github.com/open-quantum-safe/liboqs)
- Best for: `C`
- Scanner focus: `pqc`
- Useful for testing:
  - explicit PQC algorithm detection
  - KEM and signature naming coverage
  - positive PQC-capable implementation signals
  - native-code crypto coverage

Why it is valuable:

- It gives a strong positive-control corpus for post-quantum algorithm names and implementation patterns.
- It is one of the best public sources for validating that the scanner can find real PQC-related code rather than only legacy RSA or ECC code.

### 2. OpenSSL

- Repository: [https://github.com/openssl/openssl](https://github.com/openssl/openssl)
- Best for: `C`
- Scanner focus: `pqc`, `combined`
- Useful for testing:
  - TLS and SSL detection
  - X.509 and certificate handling
  - signing and verification flows
  - trust, key, and protocol-stack patterns

Why it is valuable:

- It is one of the highest-signal public repositories for mainstream TLS and certificate-related code.
- It is especially useful for validating native `C` coverage and reducing false negatives around OpenSSL-related families.

### 3. OpenKMIP `PyKMIP`

- Repository: [https://github.com/OpenKMIP/PyKMIP](https://github.com/OpenKMIP/PyKMIP)
- Best for: `Python`
- Scanner focus: `pqc`
- Useful for testing:
  - KMIP detection
  - key-lifecycle and managed-key APIs
  - KMS/HSM-like dependency enrichment
  - reference vs implementation behavior in a standards-oriented project

Why it is valuable:

- It provides standards-community-style code rather than only vendor samples.
- It helps validate that KMIP-related findings are not overly vendor-specific.

### 4. OpenKMIP `libkmip`

- Repository: [https://github.com/OpenKMIP/libkmip](https://github.com/OpenKMIP/libkmip)
- Best for: `C`
- Scanner focus: `pqc`
- Useful for testing:
  - native KMIP detection
  - key-management protocol coverage in `C`
  - dependency and category mapping for standards-based key-management code

Why it is valuable:

- It complements vendor-specific HSM and KMS examples with standards-oriented native code.

### 5. PQC ScratchPad

- Repository: [https://github.com/salrashid123/pqc_scratchpad](https://github.com/salrashid123/pqc_scratchpad)
- Best for: `Java`, `.NET`, `Node.js`, `Python`, `Go`
- Scanner focus: `pqc`, `combined`
- Useful for testing:
  - multi-language signing coverage
  - auth and request-signing patterns
  - cloud-service integration examples across several ecosystems

Why it is valuable:

- It is one of the best compact multi-cloud repositories for quickly testing PQC security concept across multiple platforms.

### 6. Thales Luna Samples

- Repository: [https://github.com/ThalesGroup/luna-samples/tree/main](https://github.com/ThalesGroup/luna-samples/tree/main)
- Best for: `HSM Examples`
- Scanner focus: `pqc`
- Useful for testing:
  - HSM 
  - asymmetric sign and decrypt patterns
  - key-management family classification

Why it is valuable:

- It gives real client-library usage for HSM services and is a good example of PQC coverage.

### 7. Google Go Tink

- Repository collection: [https://github.com/tink-crypto/tink-go](https://github.com/tink-crypto/tink-go)
- Best for:  Go
- Scanner focus: `pqc`
- Useful for testing:
  - Key Vault and identity-adjacent APIs
  - service-to-service security patterns
  - mixed application and infrastructure sample code

Why it is valuable:

- It gives many PQC coverage, especially for `go`centric organizations.


### 8. OWASP WrongSecrets

- Repository: [https://github.com/OWASP/wrongsecrets](https://github.com/OWASP/wrongsecrets)
- Best for: mixed application code and examples
- Scanner focus: `pii`, `combined`
- Useful for testing:
  - reference-only vs implementation separation
  - secret-handling anti-patterns
  - mixed language and framework coverage
  - docs and example-heavy project behavior

Why it is valuable:

- It is useful for testing how the scanner behaves in intentionally security-themed repositories that include both real implementation code and educational reference material.

### 9. OWASP Cheat Sheet Series

- Repository: [https://github.com/OWASP/CheatSheetSeries](https://github.com/OWASP/CheatSheetSeries)
- Best for: documentation and reference material
- Scanner focus: `pqc`, `combined`
- Useful for testing:
  - reference-only findings
  - docs classification
  - false-positive control in markdown-heavy content

Why it is valuable:

- It is a good negative-control or reference-heavy corpus.
- It helps validate that documentation does not get treated too aggressively as implementation ownership.

### 10. HashiCorp Vault

- Repository: [https://github.com/hashicorp/vault](https://github.com/hashicorp/vault)
- Best for: `Go`
- Scanner focus: `pqc`, `combined`
- Useful for testing:
  - secrets and transit encryption concepts
  - PKI and certificate handling references
  - infrastructure and operational security patterns
  - large repo behavior and docs-heavy sections

Why it is valuable:

- It is a strong test corpus for key-management and operational security concepts, especially in a large mixed codebase.

## Standards And Community Sources To Favor

The most useful standards-oriented or community-oriented sources are usually:

- Open Quantum Safe projects
- OpenKMIP projects
- OWASP projects
- official cloud-provider sample repositories
- OpenSSL and related mainstream crypto projects

These are often better validation sources than random app repos because they contain stable, inspectable, high-signal cryptographic content.

## Good Language Coverage Mix

If you want a balanced validation corpus, this is a strong mix:

- `C`
  - `liboqs`
  - `OpenSSL`
  - `libkmip`
- `.NET`
  - AWS signing examples
  - Azure samples
- `Java`
  - AWS signing examples
  - Google KMS samples
  - Azure samples
- `Go`
  - AWS signing examples
  - Vault
  - KMIP Go projects if needed later
- `Python`
  - PyKMIP
  - AWS samples
  - Azure samples
- `Shell / scripts`
  - Vault examples
  - operational repos
  - OWASP or infra-related examples where appropriate

## Suggested Validation Use By Scanner Domain

### Best for PII-oriented testing

- OWASP WrongSecrets
- mixed application repos with DTOs, APIs, models, frontend forms, and SQL access patterns
- your own customer-like sample apps

### Best for PQC-oriented testing

- Open Quantum Safe `liboqs`
- OpenSSL
- OpenKMIP `PyKMIP`
- OpenKMIP `libkmip`
- cloud KMS and signing samples
- vendor SDK and HSM sample repos

### Best for combined-mode testing

- mixed cloud samples
- security-heavy applications with both payload handling and crypto APIs
- repos containing service code, frontend code, config, scripts, and docs together

## Practical Cautions

- Do not treat a single repo as a ground-truth benchmark.
- Many repos are documentation-heavy or test-heavy, which can inflate reference findings.
- Large upstream libraries may contain implementation internals that are useful for detection validation but not representative of ordinary customer application architecture.
- For true scanner tuning, pair external repos with your own curated `sample_code` corpus.

## Recommended Starter Set

If you want a compact but high-value first external corpus, start with:

1. [liboqs](https://github.com/open-quantum-safe/liboqs)
2. [OpenSSL](https://github.com/openssl/openssl)
3. [PyKMIP](https://github.com/OpenKMIP/PyKMIP)
4. [libkmip](https://github.com/OpenKMIP/libkmip)
5. [AWS SigV4 Signing Examples](https://github.com/aws-samples/sigv4-signing-examples)
6. [OWASP WrongSecrets](https://github.com/OWASP/wrongsecrets)
7. [HashiCorp Vault](https://github.com/hashicorp/vault)

That set gives you strong coverage across:

- `C`
- `Java`
- `.NET`
- `Go`
- `Python`
- scripts and mixed operational content
- PQC, TLS, certs, KMS, signing, and docs/reference behavior
