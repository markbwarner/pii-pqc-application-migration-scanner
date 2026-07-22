from cryptography import x509
from fastapi import APIRouter, Header

router = APIRouter()


class ThalesProtectGatewayService:
    def authenticateRequest(self, authorization: str | None) -> None:
        if not authorization:
            raise ValueError("Missing Authorization header")


@router.post("/protectInput")
def protectInput(payload: dict, authorization: str | None = Header(default=None)):
    ThalesProtectGatewayService().authenticateRequest(authorization)
    x509.load_pem_x509_certificate(payload["certificate"].encode("utf-8"))
    return {"route": "/protectInput", "status": "protected"}


@router.post("/protectInputAndCallLLM")
def protectInputAndCallLLM(payload: dict, authorization: str | None = Header(default=None)):
    ThalesProtectGatewayService().authenticateRequest(authorization)
    return {"route": "/protectInputAndCallLLM", "status": "protected-and-forwarded"}


@router.post("/revealInput")
def revealInput(payload: dict, authorization: str | None = Header(default=None)):
    ThalesProtectGatewayService().authenticateRequest(authorization)
    return {"route": "/revealInput", "status": "revealed"}
