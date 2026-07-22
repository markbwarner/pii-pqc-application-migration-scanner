import hvac


class HashiCorpVaultTransitClient:
    def __init__(self, url: str, token: str) -> None:
        self.client = hvac.Client(url=url, token=token)

    def sign_customer_payload(self, key_name: str, input_b64: str) -> dict:
        return self.client.secrets.transit.sign_data(
            name=key_name,
            hash_input=input_b64,
            signature_algorithm="pkcs1v15",
            prehashed=True,
        )

    def verify_customer_payload(self, key_name: str, input_b64: str, signature: str) -> dict:
        return self.client.secrets.transit.verify_signed_data(
            name=key_name,
            hash_input=input_b64,
            signature=signature,
        )
