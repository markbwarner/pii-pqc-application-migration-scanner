# Sample Code Corpus

This folder contains synthetic sample applications to exercise the scanner.

## Included patterns

- Front end React component referencing PII and calling REST endpoints
- Front end React WebCrypto sample showing browser-side end-to-end PQC-style envelope handling with `window.crypto.subtle`, `ML-KEM-768`, and `ML-DSA-65` markers
- Front end Angular component referencing payment PII and posting to a back end
- Node.js UI gateway making REST calls with PII payloads
- Java Spring Boot service using REST plus JDBC/SQL
- .NET API using `HttpClient` plus `SqlConnection`
- Node.js service using Kafka and PostgreSQL
- Python FastAPI service using REST and SQL updates
- Go HTTP handler using SQL statements
- Java Kafka consumer using REST plus `PreparedStatement`
- Vector-search style code in Python and Node.js
- JDBC-only repository code that is a strong JDBC-driver candidate
- Customer-specific alias examples such as `acctNbr`, `accntNbr`, `householdNbr`, and `hhId`
- Spring controller to service to repository flow for ownership correlation
- DTO/supporting-model samples that should be labeled `supporting_model`
- React and Node.js proxy samples with routes that correlate to likely backend owners
- Additional route-aligned React, Node.js, and .NET claim-review samples for easier endpoint correlation demos
- JPA/ORM-style repository sample that should land as `review_data_access_change`
- Java PQC candidate using `RS256`, `SHA256withRSA`, `KeyStore`, and `X509Certificate`
- Java Bouncy Castle keystore sample using `org.bouncycastle` and `PKCS12` certificate loading
- Java truststore-oriented TLS sample using `TrustManagerFactory`, `KeyStore`, and `JKS`
- Java Thales Luna PQC-style samples using `LunaProvider` together with explicit `ML-KEM`, `ML-DSA`, `HQC`, and hybrid TLS named-group markers such as `X25519MLKEM768`
- Java PQC specialized and watch-list samples using `XMSS`, `HSS`, `FrodoKEM`, `Classic McEliece`, and `BIKE` so the HTML report can demonstrate green, amber, and blue PQC-capable status tags
- Node.js PQC candidate using `jsonwebtoken` with `RS256`
- Python mTLS client using certificate and private key files
- Kubernetes ingress and cert-manager sample with RSA TLS and PKCS12 keystore settings
- React certificate status component that should look like a frontend reference rather than the true backend owner
- .NET package manifest with IdentityModel, Key Vault, and PKCS dependencies
- Go module manifest with JWT, SSH, and Cloud KMS dependencies
- Rust Cargo and source sample using `openssl`, `jsonwebtoken`, and `ssh2` so Rust crates show up in dependency enrichment, CBOM summaries, and PQC categories
- PHP Composer and source sample using `firebase/php-jwt`, `phpseclib/phpseclib`, and OpenSSL calls so PHP dependencies show up in dependency enrichment, CBOM summaries, and PQC categories
- Scala SBT and source sample using `io.jsonwebtoken`, `java.security.KeyStore`, and `org.bouncycastle` so Scala dependencies show up in dependency enrichment, CBOM summaries, and PQC categories
- PHP Vault, Akeyless, and Thales/CipherTrust samples using namespace imports plus managed-service paths so existing vendor families appear in CBOM rollups for PHP
- Scala Vault, Akeyless, and Thales CADP samples using JVM imports plus managed-service paths so existing vendor families appear in CBOM rollups for Scala
- Ruby Gem and source samples using `vault`, managed Akeyless endpoint markers, and CipherTrust REST paths so existing vendor families appear in CBOM rollups for Ruby
- Rust Vault and Akeyless samples using crates, plus a generic managed-crypto REST wrapper sample that shows how Rust code can still expose vendor REST endpoints without implying a native Thales Rust SDK
- Generic managed-crypto REST wrapper sample in Rust using `/api/v1/crypto/...` and `/api/v1/vault/keys2/...` paths to demonstrate vendor REST usage without implying a first-party Rust SDK
- Java Google Cloud KMS sample using KeyManagementServiceClient for managed key operations
- Java Google Cloud HSM-style sample using CryptoKeyVersionTemplate and ProtectionLevel.HSM for HSM-backed key templates
- Node.js package manifest with JWT, KMS, JOSE, and SSH dependencies
- Python requirements manifest with JWT, certificate, KMS, and SSH packages
- HashiCorp Vault transit samples across Go, Python, and Node.js using `github.com/hashicorp/vault/api`, `hvac`, `node-vault`, `transit/encrypt`, `transit/decrypt`, `transit/sign`, and `auth/approle/login`
- Akeyless secret and certificate samples across Java, Go, Python, Node.js, and .NET using SDK markers such as `io.akeyless`, `github.com/akeylesslabs/akeyless-go`, `akeyless-python`, `akeyless-javascript`, `akeyless-csharp-netcore`, and managed operations such as `create-dynamic-secret`, `provision-certificate`, `rotate-key`, `verify-pkcs1`, and `upload-rsa`
- Go SSH client sample using `golang.org/x/crypto/ssh`
- .NET code-signing sample using `SignedCms`
- .NET Thales CADP package manifest and service reference using `CipherTrust.CADP.NETCore`
- Native C CADP CAPI sample using `cadp_capi.h`, `I_C_Initialize`, `I_C_OpenSession`, and `I_C_CreateCipherSpec` plus a richer .NET CADP RSA sample using `CADP.NetCore.Crypto`, `CADP.NetCore.KeyManagement`, `CADP.NetCore.Sessions`, `NaeSession`, `NaeKeyManagement`, and `NaeRsaKey`
- Java and native C Thales CADP PKCS#11 samples using `CADP_PKCS11.properties`, `SunPKCS11`, `CKM_RSA_PKCS`, `cadp/cadp.h`, `C_SignInit`, and `C_Sign`
- Java Thales CADP signing sample using `NAESession`, `NAEKey`, and `IngrianProvider`
- Java and native C Thales KMIP samples using `KMIPSession`, `KMIPCipher`, `KMIPGCMSpec`, `KMIPGCMKeyInformation`, `NAEClientCertificate`, and native `kmip.h` / `libkmip` client markers
- Java, Python, and cURL-style Thales CT-VL tokenization samples using `/vts/rest/v2.0/tokenize`, `/vts/rest/v2.0/detokenize`, `tokengroup`, and `tokentemplate` request fields
- Python sensitive-data wrapper sample app using Gemini-style orchestration, Akeyless, JWT, and custom sensitive-data endpoints derived from the Swagger example so it appears in scanner reports
- Native C PKCS#11-style sample showing CipherTrust/CADP-oriented signing calls
- .NET Azure Managed HSM sample using `Azure.Security.KeyVault.Cryptography` and a `managedhsm.azure.net` key identifier
- Java AWS S3 + KMS sample using `AWSKMS`, `AWSKMSClientBuilder`, `KMSEncryptionMaterialsProvider`, and `AmazonS3EncryptionClientBuilder`
- Java AWS S3 asymmetric client-side encryption sample using `EncryptionMaterials`, `StaticEncryptionMaterialsProvider`, and RSA key pairs
- Java AWS CloudTrail digest-validation sample using `ListPublicKeysRequest`, Bouncy Castle, and `SHA256withRSA` verification
- Java AWS Secrets Manager sample using `AWSSecretsManager`, `AWSSecretsManagerClientBuilder`, and `GetSecretValueRequest` to load TLS material
- Java AWS ACM / ACM PCA sample using `AWSCertificateManager`, `DescribeCertificateRequest`, `ExportCertificateRequest`, `AWSPCA`, and `IssueCertificateRequest`
- Java AWS Encryption SDK sample using `AwsCrypto`, `KmsMasterKeyProvider`, `MaterialProviders`, and KMS keyrings
- Java Oracle GoldenGate-style key-provider sample using `NAESession`, `NAEKey`, and GoldenGate-oriented key-provider logic
- Java Oracle wallet sample using `OracleWallet` and `OracleSecretStore` for secret and certificate retrieval
- Java Oracle OCI Vault / Key Management sample using `KmsManagementClient`, `KmsCryptoClient`, and `VaultsClient`
- Java Oracle OCI Certificates sample using `CertificatesManagementClient`, `CreateCertificateAuthorityRequest`, and `CreateCertificateRequest`
- Java Oracle OCI Vault secret-management sample using `VaultsClient`, `CreateSecretRequest`, and `GetSecretRequest`
- Java Oracle OCI Certificates bundle sample using `CertificatesClient`, `GetCaBundleRequest`, and `GetCertificateAuthorityBundleRequest`
- Java CipherTrust REST wrapper helper sample using `CipherTrustManagerHelper`, `cmRESTProtect`, `cmRESTSign`, `cmRESTMac`, and `/api/v1/crypto/...` routes
- Java Thales CRDP / CADP helper samples using `com.centralmanagement.*`, `ThalesCADPProtectRevealHelper`, `ThalesRestProtectRevealHelper`, and GCP batch or Vertex AI orchestration flows
- Direct Thales CRDP REST samples using vendor routes such as `/v1/protect`, `/v1/reveal`, `/v1/protectbulk`, `/v1/revealbulk`, `/v2/protect`, and `/v2/revealbulk` without a customer wrapper layer
- Java Spark-style CRDP gateway sample using abstract routes such as `/protectInput`, `/revealInput`, `/protectInputAndCallLLM`, and `/v1/chat/completions` while still relying on `com.centralmanagement.*` and `CryptoManager` behind the API boundary
- Native C AWS CloudHSM PKCS#11-style sample showing HSM-backed signing calls
- Legacy Vormetric PKCS#11 samples across Java, .NET, and native C using `Vpkcs11Session`, `Net.Pkcs11Interop`, `vorpkcs11.dll`, and `CKM_THALES_*` markers
- Voltage SecureData style Java sample using `DataMasking.mask`, `DataMasking.unmask`, `SecureData.CC`, and `usingProperty(secureData)`
- Protegrity samples using `Protector`, session-based `protect`/`unprotect`/`reprotect`, and the newer developer-edition style Python client

## Suggested scans

PII only:

```powershell
python app.py E:\codex\work\migration\sample_code --scan pii --custom-patterns E:\codex\work\migration\config/pii/examples/custom-patterns.example.json
```

PQC only:

```powershell
python app.py E:\codex\work\migration\sample_code --scan pqc --html-out E:\codex\work\migration\reports\sample_code_pqc-report.html --cbom-out E:\codex\work\migration\reports\sample_code_phase2.cbom.json
```

Combined:

```powershell
python app.py E:\codex\work\migration\sample_code --scan pii,pqc --custom-patterns E:\codex\work\migration\config/pii/examples/custom-patterns.example.json --html-out E:\codex\work\migration\reports\sample_code_combined-report.html --cbom-in E:\codex\work\migration\reports\sample_code_phase2.cbom.json
```

## What you should expect

- Front-end files should be classified as `frontend` or `frontend_with_service_calls` for PII analysis
- Java and .NET service files should be classified as back-end or back-end with data access
- JDBC-heavy files should show higher JDBC-driver candidate counts
- CRDP REST orchestration files should show higher code-change candidate counts
- `HouseholdMemberScreen.tsx` should correlate to `HouseholdController.java`
- `HouseholdProtectionRequest.java` and `HouseholdMemberProfile.java` should behave like supporting DTO/model files
- `claims-proxy.js` should look like `frontend_reference_only` while `claims-service.js` looks like the more likely backend/data owner
- `claims-api-proxy.js` and `ClaimReviewScreen.tsx` should correlate more directly to `/api/claims/...` back-end owners
- `.NET ClaimReviewController.cs` should look like an API owner, while `ClaimReviewService.cs` should look like the stronger data-access/JDBC-style owner
- `CustomerDataStore.java` should look like a likely `data_access_owner` and drive `review_data_access_change`
- `TokenSigningService.java`, `BouncyCastleKeystoreService.java`, `TruststoreTlsVerifier.java`, `ThalesCadpSigningService.java`, `VormetricPkcs11Client.java`, `VoltageSecureDataService.java`, `ProtegrityApplicationProtectorService.java`, `AzureManagedHsmSignatureService.cs`, `jwt-auth-service.js`, `mtls_client.py`, `protegrity_developer_client.py`, `customer-api-mtls.yaml`, `ciphertrust_pkcs11_client.c`, `aws_cloudhsm_pkcs11_client.c`, and `vormetric_vpkcs11_sign_verify.c` should surface as PQC migration candidates
- `LunaPqcKemSessionFactory.java`, `LunaPqcSignatureService.java`, `LunaHqcKemFallbackService.java`, and `LunaPqcTlsContextFactory.java` should surface as Thales Luna HSM examples with a green `PQC-current` tag because they contain explicit current NIST-aligned PQC or hybrid algorithm markers rather than only legacy Luna references
- `XmssFirmwareSigningProfile.java` should surface with an amber `PQC-specialized` tag because it contains stateful hash-based PQC signature markers such as `XMSS` and `HSS`
- `PqcWatchlistLabService.java` should surface with a blue `PQC-watch-list` tag because it contains experimental or watch-list algorithm names such as `FrodoKEM`, `Classic McEliece`, and `BIKE`
- `SampleCompany.Api.csproj`, `go.mod`, `package.json`, and `requirements.txt` should enrich dependency and CBOM output without overwhelming file-level findings
- `ThalesCadpSessionService.cs` and the added `CipherTrust.CADP.NETCore` package reference should surface as Thales-managed crypto dependencies
- `ThalesKmipAesGcmService.java` and `ciphertrust_kmip_aes_gcm_client.c` should surface as explicit Thales KMIP dependencies rather than being lumped into only generic HSM or KMS detection
- `ThalesCtvlTokenizationService.java`, `thales_ctvl_client.py`, and `call_thales_ctvl_tokenize.sh` should surface as explicit Thales CT-VL tokenization dependencies rather than being absorbed into only generic Thales or REST wrapper families
- `sensitive_data_wrapper_gemini_app.py` should surface as a custom wrapper-style Python service with routes such as `/stringfindsensitive`, `/stringfindreplacesensitive`, `/stringreveal`, and `/api/generate-text` that match the generated Swagger drafts
- `ciphertrust_cadp_capi_aes_gcm.c` and `ThalesCadpRsaEncryptionService.cs` should surface more explicitly as Thales CADP / CipherTrust examples for native C and .NET, not only Java-oriented CADP samples
- `ThalesCadpPkcs11Signer.java` and `ciphertrust_cadp_pkcs11_signer.c` should surface under a dedicated Thales CADP PKCS11 family instead of only the generic CADP or PKCS#11 buckets
- `AzureManagedHsmSignatureService.cs` and the added Key Vault cryptography package reference should surface as Azure Managed HSM-style dependencies
- `AwsS3KmsEncryptionClient.java` should surface as an AWS KMS and S3 encryption style managed-key dependency
- `AwsS3AsymmetricEncryptionClient.java` should surface as an AWS client-side asymmetric encryption and RSA migration candidate
- `AwsCloudTrailDigestVerifier.java` should surface as an AWS integrity-verification reference using RSA signature validation and public-key lookup
- `AwsSecretsManagerTlsMaterialLoader.java` should surface as an AWS Secrets Manager and TLS material dependency
- `AwsAcmPcaCertificateLifecycleService.java` should surface as an AWS certificate lifecycle and private PKI dependency
- `AwsEncryptionSdkKeyringService.java` should surface as an AWS Encryption SDK and KMS keyring dependency
- `OracleGoldenGateCipherTrustKeyProvider.java` should surface as an Oracle GoldenGate and Thales CADP / CipherTrust-style key-provider dependency
- `OracleWalletSecretStoreLoader.java` should surface as an Oracle PKI / wallet certificate and secret-store dependency
- `OracleOciVaultKmsClient.java` should surface as an Oracle OCI KMS managed-key dependency
- `OracleOciCertificatesAuthorityService.java` should surface as an Oracle Certificates / CA lifecycle dependency
- `OracleOciVaultSecretClient.java` should surface as an Oracle Secrets / Vault dependency
- `OracleOciCertificatesBundleClient.java` should surface as an Oracle Certificates / CA bundle dependency
- `CipherTrustManagerHelper.java` and `CipherTrustRestProtectionService.java` should surface as a wrapper-owned Thales CipherTrust REST managed-crypto dependency and likely PQC change target
- `ThalesGcpProtectRevealBatchProcessor.java`, `ThalesGcpVertexaiPromptExample.java`, `ThalesCADPProtectRevealHelper.java`, and `ThalesRestProtectRevealHelper.java` should surface as Custom Thales CRDP or CADP-style managed protection dependencies with GCP-oriented orchestration context
- `ThalesCrdpDirectRestService.java` and `thales_crdp_direct_client.py` should surface under `Thales Centralized Mgmt (CRDP,CADP)`, while helper-class abstractions should remain under Custom Thales CRDP
- `ThalesGcpProtectServerOpenAI.java` should surface as a more abstract CRDP-backed web service or API gateway example even though the public routes are application-facing rather than low-level `/v1/protect` and `/v1/reveal` endpoints
- `oracle_wallet_notes.conf` should surface wallet references such as `cwallet.sso` and `ewallet.p12` as Oracle PKI / wallet indicators
- `GcpCloudKmsEnvelopeService.java` should surface as a Google Cloud KMS-style managed key dependency
- `GcpCloudHsmKeyTemplateService.java` should surface as a Google Cloud HSM-style key-template and protection-level dependency
- `hashicorp_vault_transit_client.go`, `hashicorp_vault_transit_client.py`, `hashicorp-vault-transit-client.js`, and the added manifest dependencies should surface as an explicit HashiCorp Vault family with transit-style managed crypto usage rather than only generic KMS or other/general references
- `AkeylessCertificateAndSecretService.java`, `akeyless_secret_sync_client.go`, `akeyless_certificate_bridge.py`, `akeyless-secret-gateway.js`, `AkeylessSecretLeaseService.cs`, and the added manifest dependencies should surface as an explicit Akeyless family with managed secret, certificate, signing, and key-lifecycle usage rather than only generic secret-management references
- `AkeylessJwtSigningGateway.java`, `akeyless_ssh_cert_issuer.py`, and `akeyless-jwt-signing-proxy.js` should reinforce Akeyless coverage for JWT/signing and SSH certificate issuer workflows so the family shows up in more crypto-migration-oriented scans
- `rust-service\Cargo.toml`, `rust-service\Cargo.lock`, and `rust-service\src\main.rs` should surface Rust crates and source-level usage for TLS/certificates, JWT signing, and SSH rather than collapsing into only other/general references
- `php-service\composer.json`, `php-service\composer.lock`, and `php-service\src\TokenCertificateGateway.php` should surface PHP dependencies and source-level usage for JWT signing, certificate handling, and SSH-related crypto operations
- `scala-service\build.sbt` and `scala-service\src\main\scala\TokenKeystoreGateway.scala` should surface Scala/JVM dependencies and source-level usage for JWT signing and keystore/certificate handling
- `HashiCorpVaultTransitBridge.php`, `AkeylessPhpSigningGateway.php`, and `CipherTrustProtectClient.php` should surface HashiCorp Vault, Akeyless, and Thales CipherTrust families for PHP using namespace imports and managed-service endpoint markers
- `HashiCorpVaultTransitService.scala`, `AkeylessScalaGateway.scala`, and `ThalesCadpScalaSigningService.scala` should surface HashiCorp Vault, Akeyless, and Thales CADP / CipherTrust families for Scala using JVM imports and managed-service endpoint markers
- `hashicorp_vault_transit_ruby_service.rb`, `akeyless_ruby_gateway.rb`, and `ciphertrust_ruby_gateway.rb` should surface HashiCorp Vault, Akeyless, and Thales CipherTrust families for Ruby using gem imports, managed-service endpoint markers, and wrapper-style class names
- `hashicorp_vault_transit_rust_service.rs` and `akeyless_rust_gateway.rs` should surface HashiCorp Vault and Akeyless families for Rust using real crate and endpoint markers, while `managed_crypto_rest_gateway.rs` should remain a generic REST-wrapper example rather than implying a native Thales Rust SDK
- `aws_cloudhsm_pkcs11_client.c` should surface as CloudHSM/HSM-oriented native dependency usage
- `VormetricPkcs11Service.cs`, `VormetricPkcs11Client.java`, and `vormetric_vpkcs11_sign_verify.c` should surface as legacy Vormetric or PKCS#11-oriented dependency usage
- `VoltageSecureDataService.java` should surface as a Voltage or SecureData style managed data-protection dependency
- `ProtegrityApplicationProtectorService.java` and `protegrity_developer_client.py` should surface as Protegrity-managed protection dependencies
- `ssh_admin_client.go` should surface `SSH_USAGE`
- `ArtifactSigningService.cs` should surface `CODE_SIGNING`
- `CertificateStatusPanel.tsx` should stay visible as a lower-priority frontend reference rather than the main PQC migration owner
- `BrowserPqcEnvelopePanel.tsx` should surface with a frontend `PQC-current` tag because it contains both explicit PQC algorithm markers and real browser-side `window.crypto.subtle` implementation signals rather than only display text

