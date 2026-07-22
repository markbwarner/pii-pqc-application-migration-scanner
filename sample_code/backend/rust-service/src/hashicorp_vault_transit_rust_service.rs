use vaultrs::client::VaultClient;

pub struct HashiCorpVaultTransitRustService;

impl HashiCorpVaultTransitRustService {
    pub fn transit_paths() -> Vec<&'static str> {
        vec![
            "auth/approle/login",
            "/v1/transit/encrypt/customer-signing-key",
            "/v1/transit/sign/customer-signing-key",
            "https://vault.internal:8200",
        ]
    }
}
