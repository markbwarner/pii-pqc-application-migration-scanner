require "vault"
require "jwt"

class HashiCorpVaultTransitRubyService
  def encrypt_and_sign(payload)
    login_path = "auth/approle/login"
    encrypt_path = "/v1/transit/encrypt/customer-signing-key"
    sign_path = "/v1/transit/sign/customer-signing-key"
    client = Vault::Client.new(address: "https://vault.internal:8200")
    logical = Vault::Logical.new(client)
    [login_path, encrypt_path, sign_path, payload, client.class.name, logical.class.name].join(":")
  end
end
