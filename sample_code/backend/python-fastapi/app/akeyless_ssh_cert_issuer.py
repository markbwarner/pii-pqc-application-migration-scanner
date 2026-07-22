import akeyless_python


class AkeylessSshCertIssuer:
    def __init__(self, gateway: str) -> None:
        self.gateway = gateway
        self.sdk_name = "akeyless-python"

    def update_ssh_cert_issuer(self, issuer_name: str, ca_public_key: str) -> dict:
        return {
            "gateway": self.gateway,
            "sdk": self.sdk_name,
            "operation": "update-ssh-cert-issuer",
            "issuer_name": issuer_name,
            "ca_public_key": ca_public_key,
        }

    def rotate_signing_key(self, key_name: str) -> dict:
        return {
            "operation": "rotate-key",
            "key_name": key_name,
        }
