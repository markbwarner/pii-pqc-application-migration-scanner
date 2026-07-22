pub struct ManagedCryptoRestGateway;

impl ManagedCryptoRestGateway {
    pub fn protect_and_sign() -> Vec<&'static str> {
        vec![
            "/api/v1/crypto/encrypt",
            "/api/v1/crypto/sign",
            "/api/v1/vault/keys2/managed-signing-key",
            "https://ciphertrust.internal",
        ]
    }
}
