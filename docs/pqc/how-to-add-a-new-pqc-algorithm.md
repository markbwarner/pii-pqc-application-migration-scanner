# How To Add A New PQC Algorithm

This guide explains the minimum steps needed to add a new PQC algorithm to the scanner and have it show up in the HTML report with the right status bucket.

## The 2 Required Steps

### 1. Add the algorithm to `config/pqc-rules.json`

File:

- `E:\codex\work\migration\config\pqc-rules.json`

What to change:

- Add the new algorithm name to the `PQC_CAPABLE_ALGORITHM` rule pattern.

Why it matters:

- This is what makes the scanner create a PQC finding when it sees the algorithm text in code, config, or sample files.

Examples:

- `HQC`
- `FN-DSA`
- `XMSS`
- `FrodoKEM`

## Pattern tips

- Prefer explicit word-boundary matching such as `\bHQC\b`.
- If the algorithm has common parameter-set names, include them too.
- If the algorithm has older aliases, decide whether those aliases should also be matched here.

Example fragment:

```json
"pattern": "...|\\bHQC\\b|\\bFrodoKEM\\b|..."
```

### 2. Add the algorithm to the correct status bucket in `scanner/html_reporting.py`

File:

- `E:\codex\work\migration\scanner\html_reporting.py`

What to change:

- Add the algorithm name to the correct entry in `PQC_SIGNAL_STATUS_PATTERNS`.

Current buckets:

- `nist_current`
- `approved_specialized`
- `alias_or_legacy_name`
- `experimental_or_watchlist`

Why it matters:

- This is what controls the HTML status tag and color in the PQC report.

Examples:

- `HQC` belongs in `nist_current`
- `XMSS` and `HSS` belong in `approved_specialized`
- `Kyber` and `Dilithium` belong in `alias_or_legacy_name`
- `FrodoKEM` and `BIKE` belong in `experimental_or_watchlist`

Example fragment:

```python
("experimental_or_watchlist", ("FRODOKEM", "BIKE", "SABER"))
```

## Optional But Recommended

### 3. Add or update a sample in `sample_code`

Recommended location:

- `E:\codex\work\migration\sample_code`

Why it matters:

- This is the easiest way to validate that the scanner and HTML report behave the way you expect.

Good sample ideas:

- back-end implementation example
- front-end WebCrypto example if browser-side crypto is relevant
- specialized signature example
- watch-list or lab-only example

### 4. Update the glossary if the meaning needs explanation

File:

- `E:\codex\work\migration\docs\pqc\pqc-report-metrics-and-glossary.md`

Why it matters:

- Only needed if you want the report documentation to include new wording or updated examples for the bucket definitions.

## When You Also Need Dependency Updates

If the algorithm appears only as plain code text, the two required steps above are usually enough.

If the algorithm also appears as one of these, you may need dependency enrichment updates too:

- package name
- import path
- namespace
- SDK identifier
- manifest dependency
- header or module name

In that case also review:

- `E:\codex\work\migration\config\dependency-hints.json`
- `E:\codex\work\migration\config\dependency-explanations.json`

Use those files when you want the algorithm or provider to influence:

- dependency enrichment
- CBOM component inventory
- plain-English dependency meaning in the report

## Frontend-Specific Note

Front-end files do not get a PQC status tag just because they mention PQC text.

A front-end file must also look like real browser-side cryptographic implementation, such as:

- `window.crypto`
- `crypto.subtle`
- `subtle.generateKey`
- `subtle.importKey`
- `subtle.deriveBits`
- `subtle.encrypt`
- `subtle.decrypt`
- `subtle.sign`
- `subtle.verify`

This keeps display-only UI files from being mislabeled as true PQC implementation owners.

## Example: Add `SNOVA` As A Watch-List Algorithm

1. Edit `E:\codex\work\migration\config\pqc-rules.json`
2. Add `\bSNOVA\b` to the `PQC_CAPABLE_ALGORITHM` pattern
3. Edit `E:\codex\work\migration\scanner\html_reporting.py`
4. Add `SNOVA` to `experimental_or_watchlist` in `PQC_SIGNAL_STATUS_PATTERNS`
5. Add a small sample file under `sample_code`
6. Run a validation scan

Example validation command:

```powershell
python E:\codex\work\migration\app.py E:\codex\work\migration\sample_code --scan pqc --html-out E:\codex\work\migration\reports\pqc_status_validation.html --quiet
```

## Quick Rule Of Thumb

- file-content detection: `pqc-rules.json`
- HTML bucket and color: `html_reporting.py`
- dependency and CBOM recognition: `dependency-hints.json`
- human-readable wording: `dependency-explanations.json` and glossary docs
