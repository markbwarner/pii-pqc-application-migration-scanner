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
CHANGE_CSV="$OUTPUT_DIR/${INPUT_NAME}_pii_likely-change-targets_${STAMP}.csv"
DBA_SQL="$OUTPUT_DIR/${INPUT_NAME}_pii_dba-planning_${STAMP}.sql"

python "$ROOT_DIR/app.py" "$INPUT_DIR" \
  --scan pii \
  --custom-patterns "$CUSTOM_PATTERNS" \
  --json-summary-out "$SUMMARY_JSON" \
  --csv-out "$CHANGE_CSV" \
  --sql-out "$DBA_SQL"

echo "Wrote $SUMMARY_JSON"
echo "Wrote $CHANGE_CSV"
echo "Wrote $DBA_SQL"
