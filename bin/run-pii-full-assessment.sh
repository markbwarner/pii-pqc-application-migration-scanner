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

FULL_JSON="$OUTPUT_DIR/${INPUT_NAME}_pii_impact-report_${STAMP}.json"
SUMMARY_JSON="$OUTPUT_DIR/${INPUT_NAME}_pii_impact-summary_${STAMP}.json"
FILE_REPORTS_JSON="$OUTPUT_DIR/${INPUT_NAME}_pii_file-reports_${STAMP}.json"
FILE_REPORTS_CSV="$OUTPUT_DIR/${INPUT_NAME}_pii_file-reports_${STAMP}.csv"
CHANGE_CSV="$OUTPUT_DIR/${INPUT_NAME}_pii_likely-change-targets_${STAMP}.csv"
DBA_SQL="$OUTPUT_DIR/${INPUT_NAME}_pii_dba-planning_${STAMP}.sql"
HTML_OUT="$OUTPUT_DIR/${INPUT_NAME}_pii-report_${STAMP}.html"

python "$ROOT_DIR/app.py" "$INPUT_DIR" \
  --scan pii \
  --custom-patterns "$CUSTOM_PATTERNS" \
  --json-out "$FULL_JSON" \
  --json-summary-out "$SUMMARY_JSON" \
  --json-file-reports-out "$FILE_REPORTS_JSON" \
  --csv-file-reports-out "$FILE_REPORTS_CSV" \
  --csv-out "$CHANGE_CSV" \
  --sql-out "$DBA_SQL" \
  --html-out "$HTML_OUT" \
  --include-file-reports

echo "Wrote $FULL_JSON"
echo "Wrote $SUMMARY_JSON"
echo "Wrote $FILE_REPORTS_JSON"
echo "Wrote $FILE_REPORTS_CSV"
echo "Wrote $CHANGE_CSV"
echo "Wrote $DBA_SQL"
echo "Wrote $HTML_OUT"
