require "net/http"

class CipherTrustRubyGateway
  def protect_and_sign(payload)
    encrypt_path = "/api/v1/crypto/encrypt"
    sign_path = "/api/v1/crypto/sign"
    key_path = "/api/v1/vault/keys2/managed-signing-key"
    [encrypt_path, sign_path, key_path, payload].join(":")
  end
end
