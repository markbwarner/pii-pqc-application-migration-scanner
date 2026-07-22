# Swagger Drafts

This folder holds review-first draft config files generated from raw Swagger JSON input.

Example command:

```powershell
python E:\codex\work\migration\app.py --swagger-only --swagger-in C:\tmp\swaggar-example\sampleswaggarfile\openapi_export.json
```

Default output files:

- `*_cbom-vendor-families.json`
- `*_dependency-hints.json`
- `*_dependency-explanations.json`
- `*_pqc-rules.json`
- `*_review.md`

These are drafts only and are intended to be reviewed and selectively copied into the live config files under `config`.

## Behavior Before Import

Swagger draft generation does not automatically update the live config files under `config`. That means a sample application can still appear in scan results because it lives under `sample_code`, but it will not yet inherit the generated custom family name until the draft content is manually reviewed and promoted.

Example: `sensitive_data_wrapper_gemini_app.py` already appears in scan output today because the current scanner detects generic signals such as JWT-related logic, service-style behavior, and existing dependency heuristics. In the current live config state it does **not** yet show up as `Custom Sensitive Data Wrapper API`.

Current behavior before promoting the Swagger drafts:

- the file still appears in the report because it is part of the scanned sample corpus
- it currently lands through existing generic findings rather than the generated Swagger-derived family
- it can still contribute observed CBOM-style components even before any draft config is merged

For the current sample, observed components can include items such as:

- `fastapi`
- `pydantic`
- `sensitive-data-wrapper`
- `requests`
- `jwt`
- `akeyless`
- `vertexai`
- `google`

This is expected. The draft files are intended to improve how those routes, helpers, and wrapper semantics are classified, but they do not take effect until you choose to copy the reviewed content into the live config files.

