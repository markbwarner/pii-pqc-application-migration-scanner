import akeyless_python


class AkeylessCertificateBridge:
    def __init__(self, gateway: str) -> None:
        self.gateway = gateway
        self.sdk_name = "akeyless-python"

    def provision_certificate(self, issuer_name: str) -> dict:
        return {
            "gateway": self.gateway,
            "sdk": self.sdk_name,
            "operation": "provision-certificate",
            "issuer": issuer_name,
        }

    def rotate_key(self, key_name: str) -> dict:
        return {"operation": "rotate-key", "key_name": key_name}
