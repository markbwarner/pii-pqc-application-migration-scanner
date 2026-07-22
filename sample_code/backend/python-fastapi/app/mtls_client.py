import httpx
import ssl
from pathlib import Path


CERT_DIR = Path("/etc/customer-api/certs")
CLIENT_CERT = CERT_DIR / "client.crt"
CLIENT_KEY = CERT_DIR / "client.key"
CA_CERT = CERT_DIR / "ca-chain.pem"


def build_secure_client() -> httpx.Client:
    context = ssl.create_default_context(cafile=str(CA_CERT))
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(certfile=str(CLIENT_CERT), keyfile=str(CLIENT_KEY))
    return httpx.Client(base_url="https://partner.example.com", verify=context)


def fetch_statement(customer_id: str) -> dict:
    with build_secure_client() as client:
        response = client.get(f"/v1/statements/{customer_id}")
        response.raise_for_status()
        return response.json()
