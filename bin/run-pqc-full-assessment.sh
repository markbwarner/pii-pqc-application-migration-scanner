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

FULL_JSON="$OUTPUT_DIR/${INPUT_NAME}_pqc_impact-report_${STAMP}.json"
SUMMARY_JSON="$OUTPUT_DIR/${INPUT_NAME}_pqc_impact-summary_${STAMP}.json"
FILE_REPORTS_JSON="$OUTPUT_DIR/${INPUT_NAME}_pqc_file-reports_${STAMP}.json"
FILE_REPORTS_CSV="$OUTPUT_DIR/${INPUT_NAME}_pqc_file-reports_${STAMP}.csv"
CHANGE_CSV="$OUTPUT_DIR/${INPUT_NAME}_pqc_likely-change-targets_${STAMP}.csv"
HTML_OUT="$OUTPUT_DIR/${INPUT_NAME}_pqc-report_${STAMP}.html"
CBOM_OUT="$OUTPUT_DIR/${INPUT_NAME}_pqc_cbom_${STAMP}.json"

cmd=(python "$ROOT_DIR/app.py" "$INPUT_DIR" --scan pqc --json-out "$FULL_JSON" --json-summary-out "$SUMMARY_JSON" --json-file-reports-out "$FILE_REPORTS_JSON" --csv-file-reports-out "$FILE_REPORTS_CSV" --csv-out "$CHANGE_CSV" --html-out "$HTML_OUT" --cbom-out "$CBOM_OUT" --include-file-reports)
if [[ -n "$CBOM_IN" ]]; then
  cmd+=(--cbom-in "$CBOM_IN")
fi
"${cmd[@]}"

echo "Wrote $FULL_JSON"
echo "Wrote $SUMMARY_JSON"
echo "Wrote $FILE_REPORTS_JSON"
echo "Wrote $FILE_REPORTS_CSV"
echo "Wrote $CHANGE_CSV"
echo "Wrote $HTML_OUT"
echo "Wrote $CBOM_OUT"
