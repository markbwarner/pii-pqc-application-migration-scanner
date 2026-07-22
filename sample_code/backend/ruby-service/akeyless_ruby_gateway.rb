require "net/http"

class AkeylessRubyGateway
  def managed_actions(payload)
    host = "https://api.akeyless.io"
    secret_action = "create-dynamic-secret"
    rotate_action = "rotate-key"
    verify_action = "verify-pkcs1"
    [host, secret_action, rotate_action, verify_action, payload].join(":")
  end
end
