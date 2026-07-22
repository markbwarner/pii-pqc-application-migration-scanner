#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

INPUT_DIR="${1:-sample_code}"
OUTPUT_DIR="${2:-$ROOT_DIR/reports}"
CBOM_IN="${3:-}"
INPUT_NAME="$(basename "$INPUT_DIR")"
STAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUTPUT_DIR"

SUMMARY_JSON="$OUTPUT_DIR/${INPUT_NAME}_pqc_impact-summary_${STAMP}.json"

python "$ROOT_DIR/app.py" "$INPUT_DIR" \
  --scan pqc \
  --json-summary-out "$SUMMARY_JSON"

echo "Wrote $SUMMARY_JSON"
