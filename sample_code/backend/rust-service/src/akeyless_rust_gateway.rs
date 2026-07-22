use akeyless_openapi::apis::configuration::Configuration;

pub struct AkeylessRustGateway;

impl AkeylessRustGateway {
    pub fn managed_actions() -> Vec<&'static str> {
        let _config = Configuration::default();
        vec!["https://api.akeyless.io", "create-dynamic-secret", "rotate-key", "verify-pkcs1"]
    }
}
