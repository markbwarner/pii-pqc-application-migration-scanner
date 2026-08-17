# Run Script Helpers

These helper scripts now include the scan domain in the filename so it is obvious whether a helper is meant for `pii`, `pqc`, or `combined` scanning.

## Quick Start

If you just want a first successful run, use the helper scripts with the local [sample_code](E:\codex\work\migration\sample_code) corpus.

### PII quick start

Windows:

```powershell
bin\run-pii-summary-only.bat sample_code
bin\run-pii-summary-dba.bat sample_code
```

Shell:

```bash
./bin/run-pii-summary-only.sh sample_code
./bin/run-pii-summary-dba.sh sample_code
```

Typical outputs:

- `sample_code_pii-impact-summary_<timestamp>.json`
- `sample_code_likely-change-targets_<timestamp>.csv`
- `sample_code_dba-planning_<timestamp>.sql`

### PQC quick start

Windows:

```powershell
bin\run-pqc-summary-only.bat sample_code
bin\run-pqc-full-assessment.bat sample_code
```

Shell:

```bash
./bin/run-pqc-summary-only.sh sample_code
./bin/run-pqc-full-assessment.sh sample_code
```

Typical outputs:

- `sample_code_pqc-impact-summary_<timestamp>.json`
- `sample_code_pqc-report_<timestamp>.html`
- `sample_code_pqc.cbom.json`

### Combined quick start

Windows:

```powershell
bin\run-combined-summary-only.bat sample_code
bin\run-combined-full-assessment.bat sample_code
```

Shell:

```bash
./bin/run-combined-summary-only.sh sample_code
./bin/run-combined-full-assessment.sh sample_code
```

Default behavior:

- input directory: `sample_code`
- output directory: `reports`
- PII and combined helpers default custom patterns to `config/pii/examples/custom-patterns.example.json`
- PQC helpers optionally accept a third argument for `--cbom-in`

Common helper families:

- `run-pii-*`
  - PII-only / CRDP-oriented helper set
- `run-pqc-*`
  - PQC-only helper set
- `run-combined-*`
  - combined `pii,pqc` helper set

Recommended scripts:

- `run-pii-summary-only.bat` and `run-pii-summary-only.sh`
- `run-pii-summary-dba.bat` and `run-pii-summary-dba.sh`
- `run-pii-detailed-report-only.bat` and `run-pii-detailed-report-only.sh`
- `run-pii-full-assessment.bat` and `run-pii-full-assessment.sh`
- `run-pqc-summary-only.bat` and `run-pqc-summary-only.sh`
- `run-pqc-detailed-report-only.bat` and `run-pqc-detailed-report-only.sh`
- `run-pqc-full-assessment.bat` and `run-pqc-full-assessment.sh`
- `run-combined-summary-only.bat` and `run-combined-summary-only.sh`
- `run-combined-detailed-report-only.bat` and `run-combined-detailed-report-only.sh`
- `run-combined-full-assessment.bat` and `run-combined-full-assessment.sh`

Windows examples:

```powershell
bin\run-pii-summary-only.bat sample_code
bin\run-pii-summary-dba.bat sample_code
bin\run-pqc-summary-only.bat sample_code
bin\run-pqc-full-assessment.bat sample_code
bin\run-combined-full-assessment.bat sample_code
```

Shell examples:

```bash
./bin/run-pii-summary-only.sh sample_code
./bin/run-pii-summary-dba.sh sample_code
./bin/run-pqc-summary-only.sh sample_code
./bin/run-pqc-full-assessment.sh sample_code
./bin/run-combined-full-assessment.sh sample_code
```

Optional arguments:

PII and combined helpers:

1. input directory to scan
2. custom patterns JSON path
3. output directory

PQC helpers:

1. input directory to scan
2. output directory
3. optional CBOM input path

Legacy compatibility wrappers are still present for the older generic names, but new documentation should prefer the explicit domain-prefixed script names.


Notes:

- `run-pii-full-assessment.*` now writes a standalone PII HTML report in addition to the JSON, CSV, and SQL outputs.
