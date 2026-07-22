#!/usr/bin/env bash
set -euo pipefail

TOKEN="${TOKEN:-demo-token}"

curl -sS -X POST "https://gateway.example.internal/protectInput"   -H "Authorization: Bearer ${TOKEN}"   -H "Content-Type: application/json"   -d '{"customerId":"12345","ssn":"123-45-6789"}'

curl -sS -X POST https://gateway.example.internal/protectInputAndCallLLM   -H "Authorization: Bearer ${TOKEN}"   -d '{"prompt":"Summarize the protected record"}'
