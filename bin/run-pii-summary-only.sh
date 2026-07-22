#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

INPUT_DIR="${1:-sample_code}"
CUSTOM_PATTERNS="${2:-$ROOT_DIR/config/pii/examples/custom-patterns.example.json}"
OUTPUT_DIR="${3:-$ROOT_DIR/reports}"
INPUT_NAME="$(basename "$INPUT_DIR")"
STAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUTPUT_DIR"

SUMMARY_JSON="$OUTPUT_DIR/${INPUT_NAME}_pii_impact-summary_${STAMP}.json"

python "$ROOT_DIR/app.py" "$INPUT_DIR" \
  --scan pii \
  --json-summary-out "$SUMMARY_JSON"

echo "Wrote $SUMMARY_JSON"
