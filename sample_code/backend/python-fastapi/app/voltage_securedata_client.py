from securedata import SimpleAPI
from dataclasses import dataclass


@dataclass
class SecureDataPolicy:
    policy_name: str
    identity: str


class VoltageSecureDataClient:
    package_name = "Voltage SecureData SimpleAPI"
    sdk_family = "SecureData Appliance"

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def protect_value(self, value: str, policy: SecureDataPolicy) -> str:
        client = SimpleAPI()
        request_descriptor = {
            "provider": "Voltage",
            "sdk": "SimpleAPI",
            "service": "SecureData",
            "policy": policy.policy_name,
            "identity": policy.identity,
            "endpoint": self.endpoint,
            "client": client.__class__.__name__,
        }
        return f"protect({value}) via {request_descriptor['sdk']} at {request_descriptor['endpoint']}"

    def reveal_value(self, tokenized_value: str, policy: SecureDataPolicy) -> str:
        request_descriptor = {
            "provider": "Voltage Fusion",
            "sdk": "SecureData SimpleAPI",
            "policy": policy.policy_name,
            "identity": policy.identity,
        }
        return f"unprotect({tokenized_value}) via {request_descriptor['provider']}"
