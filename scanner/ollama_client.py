from __future__ import annotations

import json
from urllib import error, request

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"


def call_ollama_text(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    url: str,
    timeout_seconds: int,
    num_predict: int,
) -> str:
    normalized_url = url.strip() or DEFAULT_OLLAMA_URL
    if normalized_url.endswith("/api/generate"):
        return _call_generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            url=normalized_url,
            timeout_seconds=timeout_seconds,
            num_predict=num_predict,
        )
    return _call_chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        url=normalized_url,
        timeout_seconds=timeout_seconds,
        num_predict=num_predict,
    )


def _call_chat(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    url: str,
    timeout_seconds: int,
    num_predict: int,
) -> str:
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": num_predict,
            },
        }
    ).encode("utf-8")
    raw = _post_json(url=url, body=body, timeout_seconds=timeout_seconds)
    payload = json.loads(raw)
    message = payload.get("message") or {}
    response_text = str(message.get("content", "")).strip()
    if not response_text:
        raise RuntimeError("Ollama chat returned an empty response.")
    return response_text


def _call_generate(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    url: str,
    timeout_seconds: int,
    num_predict: int,
) -> str:
    prompt = system_prompt.strip() + "\n\n" + user_prompt.strip()
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": num_predict,
            },
        }
    ).encode("utf-8")
    raw = _post_json(url=url, body=body, timeout_seconds=timeout_seconds)
    payload = json.loads(raw)
    response_text = str(payload.get("response", "")).strip()
    if not response_text:
        raise RuntimeError("Ollama generate returned an empty response.")
    return response_text


def _post_json(*, url: str, body: bytes, timeout_seconds: int) -> str:
    http_request = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=timeout_seconds) as response:
            return response.read().decode("utf-8")
    except error.HTTPError as exc:
        try:
            response_body = exc.read().decode("utf-8").strip()
        except Exception:
            response_body = ""
        detail = f" HTTP {exc.code}: {exc.reason}."
        if response_body:
            detail += f" Response body: {response_body}"
        raise RuntimeError(f"Failed while calling local Ollama at `{url}`.{detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Failed while calling local Ollama at `{url}`. Underlying error: {exc}") from exc
