import requests

PROTECT_PATH = "/v1/protect"
REVEAL_PATH = "/v1/reveal"
PROTECT_BULK_PATH = "/v1/protectbulk"
REVEAL_BULK_PATH = "/v1/revealbulk"


class CrdpRestClient:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def protect(self, payload: dict) -> dict:
        return requests.post(f"{self.base_url}{PROTECT_PATH}", json=payload, headers=self.headers, timeout=20).json()

    def reveal(self, payload: dict) -> dict:
        return requests.post(f"{self.base_url}{REVEAL_PATH}", json=payload, headers=self.headers, timeout=20).json()

    def protect_bulk(self, payload: dict) -> dict:
        return requests.post(f"{self.base_url}{PROTECT_BULK_PATH}", json=payload, headers=self.headers, timeout=20).json()

    def reveal_bulk(self, payload: dict) -> dict:
        return requests.post(f"{self.base_url}{REVEAL_BULK_PATH}", json=payload, headers=self.headers, timeout=20).json()
