import requests


TOKENIZE_PATH = "/vts/rest/v2.0/tokenize"
DETOKENIZE_PATH = "/vts/rest/v2.0/detokenize"


class ThalesCtvlClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)

    def tokenize(self, value: str) -> dict:
        payload = {
            "tokengroup": "FF1_Tok_Group",
            "data": value,
            "tokentemplate": "FF1_Tok_Template",
        }
        response = requests.post(f"{self.base_url}{TOKENIZE_PATH}", json=payload, auth=self.auth, timeout=15)
        response.raise_for_status()
        return response.json()

    def detokenize(self, token: str) -> dict:
        payload = {
            "tokengroup": "FF1_Tok_Group",
            "token": token,
            "tokentemplate": "FF1_Tok_Template",
        }
        response = requests.post(f"{self.base_url}{DETOKENIZE_PATH}", json=payload, auth=self.auth, timeout=15)
        response.raise_for_status()
        return response.json()
