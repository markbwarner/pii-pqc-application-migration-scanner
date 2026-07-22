# CRDP Support Effort Estimator From PII Report

## What This Is

`tools/generate_support_estimate_workbook_from_pii_report.py` creates a **scan-informed** CRDP support-estimate workbook from a PII file-reports JSON export.

Unlike the static estimator, this version starts from real scanner output and derives a planning baseline from:

- likely change-owner hints
- likely change-target counts
- complexity ratings
- context and ownership distribution
- JDBC-style reduction candidates

## Difference From The Static Version

Use the two versions this way:

1. Static version
   - `tools/generate_support_estimate_workbook.py`
   - no external input dependency
   - uses canned assumptions only
   - best for reusable baseline conversations and early proposal modeling
2. Scan-informed version
   - `tools/generate_support_estimate_workbook_from_pii_report.py`
   - depends on a real PII `file-reports` JSON export
   - derives application buckets and support-estimating counts from actual findings
   - best for customer-specific planning once a scan has already been run

## What It Depends On

This version depends on a PII file-reports JSON export produced by the main scanner.

Required input dependency:

- a JSON file created with `--scan pii`
- and `--json-file-reports-out`
- and `--include-file-reports`

Example dependency-generation command:

```powershell
python E:/codex/work/migration/app.py E:/codex/work/migration/sample_code --scan pii --json-file-reports-out E:/codex/work/migration/reports/sample_code_pii_file-reports.json --include-file-reports
```

Example real input file:

- `E:/codex/work/migration/reports/sample_code_pii_file-reports_20260721_154735.json`

## What It Uses From That Input

The scan-informed generator reads file-report content such as:

- likely change-owner hints
- likely change-target flags
- recommended change actions
- complexity ratings
- classification contexts
- JDBC and code-change candidate counts
- total findings per file

It uses those to derive workbook rows that are more representative of the scanned estate.

## What It Still Needs Human Judgment For

Even this scan-informed version is not fully automatic. It still expects humans to review and adjust:

- readiness assumptions
- business criticality
- data/performance multipliers
- operating-model and support-team assumptions

## What It Produces

It writes a timestamped Excel workbook under:

- `docs/pii/assessment/generated`

The workbook includes sheets for:

- instructions
- input overview
- derived applications
- editable assumptions
- derived support scenarios
- portfolio summary

## Example Command

```powershell
python E:/codex/work/migration/tools/generate_support_estimate_workbook_from_pii_report.py --pii-file-reports E:/codex/work/migration/reports/sample_code_pii_file-reports_20260721_154735.json --label sample_code
```

## Optional Arguments

- `--label`
  - optional label used in the workbook title and output filename
- `--output`
  - optional explicit output `.xlsx` path

## Sample Output You Can Open Now

A generated sample workbook is available here:

- `E:/codex/work/migration/docs/pii/assessment/generated/sample_code_crdp-support-estimator_20260721_200805.xlsx`
