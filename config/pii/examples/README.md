# PII Example Config Files

This folder contains example PII scanner config inputs.

Files here are intended as starting points you can copy, review, and adapt for customer-specific scanning.

Included examples:

- `custom-patterns.example.json`
  - sample custom keyword and alias patterns for the PII scanner
- `custom-reg-express-patterns.example.json`
  - sample custom regex-style patterns for more specialized matching

Typical usage:

```powershell
python E:\codex\work\migration\app.py E:\codex\work\migration\sample_code --scan pii --custom-patterns E:\codex\work\migration\config\pii\examples\custom-patterns.example.json
```

These are example artifacts, not the live scanner config.
