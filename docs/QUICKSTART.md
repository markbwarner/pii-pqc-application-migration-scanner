# Quick Start

This page is the fastest way to get the scanner running against the local sample corpus.

Use the helper scripts in [bin](E:\codex\work\migration\bin) with the sample applications in [sample_code](E:\codex\work\migration\sample_code).

The basic process is:

1. Install Python and open a terminal in the project root.
2. Point the scanner at the code you want to assess, or start with `sample_code`.
3. Run one of the helper scripts or run `app.py` directly.
4. Review the generated JSON, CSV, HTML, SQL, or CBOM outputs in [reports](E:\codex\work\migration\reports).

## Before You Start

The core scanner uses only the Python standard library, so there is no required `pip install` step for the main scan flow.

Minimum setup:

1. Install Python 3.
2. Open a terminal in the project root.
3. Optionally create and activate a virtual environment.

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python app.py --help
```

If `python` is not recognized on Windows, try:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py app.py --help
```

Linux or macOS shell:

```bash
python3 -m venv .venv
source .venv/bin/activate
python app.py --help
```

If the help command works, the scanner is ready to run.

## PII Quick Start

Best first run:

```powershell
bin\run-pii-summary-dba.bat sample_code
```

Shell:

```bash
./bin/run-pii-summary-dba.sh sample_code
```

What you get:

- PII summary JSON
- likely-change-targets CSV
- DBA planning SQL

This is the best first demo for:

- developers
- DBAs
- project planners
- PII migration and impact discussions

## PQC Quick Start

Best first run:

```powershell
bin\run-pqc-full-assessment.bat sample_code
```

Shell:

```bash
./bin/run-pqc-full-assessment.sh sample_code
```

What you get:

- PQC summary and detailed outputs
- PQC HTML report
- CBOM-style output

This is the best first demo for:

- PQC readiness discussions
- architecture reviews
- dependency and certificate posture reviews

## Combined Quick Start

Best first run:

```powershell
bin\run-combined-full-assessment.bat sample_code
```

Shell:

```bash
./bin/run-combined-full-assessment.sh sample_code
```

What you get:

- combined PII and PQC outputs
- HTML reporting
- likely-change-targets CSV
- DBA planning SQL
- CBOM-style output

This is the best option when you want one end-to-end demonstration of the full scanner.

## Fastest Summary-Only Runs

If you want the lightest-weight first validation:

```powershell
bin\run-pii-summary-only.bat sample_code
bin\run-pqc-summary-only.bat sample_code
bin\run-combined-summary-only.bat sample_code
```

## Output Location

By default, the helper scripts write timestamped files under [reports](E:\codex\work\migration\reports).

Examples:

- `sample_code_pii-impact-summary_<timestamp>.json`
- `sample_code_likely-change-targets_<timestamp>.csv`
- `sample_code_dba-planning_<timestamp>.sql`
- `sample_code_pqc-report_<timestamp>.html`

## Where To Read More

- [README.md](E:\codex\work\migration\README.md)
- [bin/README.md](E:\codex\work\migration\bin\README.md)
- [sample_code/README.md](E:\codex\work\migration\sample_code\README.md)
