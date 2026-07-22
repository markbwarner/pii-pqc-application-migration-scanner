from __future__ import annotations

import base64
import os
import re
import uuid
from typing import Any

import akeyless
import jwt
import requests
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class SensitiveStringRequest(BaseModel):
    value: str


class ProtectedValueResponse(BaseModel):
    original_length: int
    protected_value: str
    findings: list[str]


app = FastAPI(title="Sensitive Data Wrapper API")


def _find_sensitive_tokens(text: str) -> list[str]:
    findings: list[str] = []
    if re.search(r"\b[0-9]{10,12}\b", text):
        findings.append("ACCOUNT_NUMBER_LITERAL")
    if re.search(r"HH-[0-9]{5,10}", text):
        findings.append("HOUSEHOLD_ID_LITERAL")
    if re.search(r"\$[0-9]{2,3},[0-9]{3}", text):
        findings.append("SALARY_LITERAL")
    return findings


def _protect_value(text: str) -> str:
    encoded = base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii")
    return f"ENC-{encoded}"


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/stringfindsensitive", response_model=ProtectedValueResponse)
def string_find_sensitive(payload: SensitiveStringRequest = Body(...)) -> ProtectedValueResponse:
    findings = _find_sensitive_tokens(payload.value)
    return ProtectedValueResponse(
        original_length=len(payload.value),
        protected_value=_protect_value(payload.value),
        findings=findings,
    )


@app.post("/stringfindreplacesensitive", response_model=ProtectedValueResponse)
def string_find_replace_sensitive(payload: SensitiveStringRequest = Body(...)) -> ProtectedValueResponse:
    findings = _find_sensitive_tokens(payload.value)
    redacted = payload.value
    redacted = re.sub(r"\b[0-9]{10,12}\b", "ACCOUNT_NUMBER", redacted)
    redacted = re.sub(r"HH-[0-9]{5,10}", "HOUSEHOLD_ID", redacted)
    redacted = re.sub(r"\$[0-9]{2,3},[0-9]{3}", "SALARY", redacted)
    return ProtectedValueResponse(
        original_length=len(payload.value),
        protected_value=_protect_value(redacted),
        findings=findings,
    )


@app.post("/stringreveal")
def string_reveal(payload: SensitiveStringRequest = Body(...)) -> JSONResponse:
    if not payload.value.startswith("ENC-"):
        raise HTTPException(status_code=400, detail="Expected protected value with ENC- prefix")
    raw = payload.value[4:]
    decoded = base64.urlsafe_b64decode(raw.encode("ascii")).decode("utf-8")
    return JSONResponse({"revealed": decoded})


@app.post("/api/generate-text")
def generate_text(payload: dict[str, Any] = Body(...)) -> JSONResponse:
    prompt = str(payload.get("prompt", ""))
    metadata = {
        "jwt_hint": bool(os.getenv("JWT_SIGNING_KEY")),
        "akeyless_hint": bool(getattr(akeyless, "__name__", None)),
        "request_trace_id": str(uuid.uuid4()),
    }
    signed = jwt.encode({"prompt_length": len(prompt)}, "demo-signing-secret", algorithm="HS256")
    _ = requests.Request("POST", "https://example.local/generate", json={"prompt": prompt}).prepare()
    return JSONResponse({
        "response": f"Processed prompt of length {len(prompt)}",
        "metadata": metadata,
        "jwt_preview": signed[:24],
    })
