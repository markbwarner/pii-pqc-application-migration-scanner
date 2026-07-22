# CRDP Support Effort Estimator

## What This Is

`tools/generate_support_estimate_workbook.py` generates the Excel workbook:

- `docs/pii/assessment/crdp-support-effort-estimator.xlsx`

The workbook is a planning aid for **ongoing maintenance and support estimating** for a Thales CRDP or similar sensitive-data protection rollout. It should be positioned as a **PII-assessment-informed CRDP support estimator**.

## Static Vs Scan-Informed

There are now two related workbook generators in this repo:

1. Static workbook generator
   - `tools/generate_support_estimate_workbook.py`
   - uses hardcoded scenario assumptions embedded in Python
   - best for canned proposal models, early customer conversations, and reusable baseline estimates
2. Scan-informed workbook generator
   - `tools/generate_support_estimate_workbook_from_pii_report.py`
   - uses a real PII `file-reports` JSON export as input
   - best when you want workbook counts to start from actual scanner findings rather than generic `250 / 100 / 50` scenarios

## What The Static Version Depends On

This version has **no external input dependency**.

It does not read:

- source directories
- scanner JSON output
- CBOM files
- config spreadsheets

Instead, it depends entirely on embedded assumptions in the script itself, including:

- sample application portfolio scenarios
- base complexity hours
- readiness multipliers
- criticality multipliers
- data/performance multipliers
- role allocation assumptions

## What It Does

It builds a self-contained `.xlsx` workbook with formula-driven tabs for:

- instructions and planning notes
- baseline assumptions
- conservative assumptions
- three application-portfolio scenarios: `250`, `100`, and `50`
- portfolio summary
- role-based monthly effort allocation
- simple visual summary bars

The workbook models monthly hours, annual hours, and rough FTE equivalents using embedded formulas and editable assumptions.

## Important Scope Note

This workbook is aligned to the **PII / CRDP scanner use case**, not the PQC scanner use case.

Why:

- the scenarios are based on sensitive-data protection rollout patterns
- the guidance assumes front-end-only PII references can often be reduced out of true change-owner scope after assessment
- the role mix and assumptions focus on tokenization, CRDP operations, DBA support, policy administration, batch loads, and application onboarding

It should be treated as a **PII-assessment-informed CRDP support estimator**, not a general migration workbook and not a PQC planning workbook.

## What It Does Not Do

It does not:

- scan code
- parse scanner JSON output
- infer estimates directly from a report
- generate PQC migration estimates

Instead, it creates a reusable workbook template with prebuilt scenario assumptions.

## How To Run It

```powershell
python E:/codex/work/migration/tools/generate_support_estimate_workbook.py
```

After it runs, the workbook is written to:

- `E:/codex/work/migration/docs/pii/assessment/crdp-support-effort-estimator.xlsx`

## Sample Output You Can Open Now

Current sample workbooks in the repo include:

- `E:/codex/work/migration/docs/pii/assessment/crdp-support-effort-estimator.xlsx`
- `E:/codex/work/migration/docs/pii/assessment/crdp-support-effort-estimator5--27.xlsx`

## Related Tooling

A scan-informed variant is also available:

- `tools/generate_support_estimate_workbook_from_pii_report.py`
- documented in `docs/pii/assessment/crdp-support-effort-estimator-from-pii-report.md`
