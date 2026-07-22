# CBOM Usage Notes

## What CBOM Is Good For

A CBOM in this scanner is best understood as a crypto and dependency inventory artifact.

Typical uses:

- capture the crypto-relevant components a codebase depends on
- share that inventory with security, platform, PKI, or compliance teams
- compare apps, releases, or environments over time
- enrich migration assessments when source is incomplete or unavailable

## Why Generate A CBOM

Generating a CBOM is useful when you want a portable output from a source scan.

What source scanning gives you:

- what the code and manifests reveal locally
- where crypto-relevant libraries seem to be used
- whether findings look like implementation, configuration, docs, tests, or references

What CBOM export gives you:

- a reusable artifact that can be reviewed outside the scanner
- something that can be versioned, diffed, archived, or merged with other inventories
- a handoff format for teams who do not need the full source-scan detail

Mental model:

- source scan = usage context
- CBOM = dependency inventory

## Why Use CBOM As Input Too

CBOM input is useful for enrichment, not just generation.

Typical reasons to feed a CBOM back into the scanner:

- you do not have the full source tree, but you do have BOM data
- a build pipeline or package-management tool knows about packaged dependencies that a local scan may not fully see
- you want to merge inventories from multiple teams or scanning steps into one migration view
- you want to carry forward known crypto dependencies from an earlier assessment

This means the two directions serve different purposes:

- `source -> CBOM`
  - tell me what this codebase appears to use
- `CBOM -> scan enrichment`
  - use this already-known inventory to improve or extend the assessment

## Practical Example

A common workflow might look like this:

1. Team A scans a Java service and exports a CBOM.
2. Team B scans Kubernetes or deployment configuration for the same app.
3. Security has a build-pipeline BOM or package inventory.
4. Those inventories are fed back in to produce a more complete migration report.

That combined view is useful when the source tree alone does not tell the whole story.

## Why CBOM Alone Is Not Enough

A CBOM tells you what components exist.
A source scan helps tell you how they appear to be used.

That difference matters for PQC migration planning.

Examples:

- a CBOM may show `jsonwebtoken` is present
- source scanning may show it is actually tied to `RS256` token signing in implementation code
- a CBOM may show `cryptography` or `KeyStore` exists
- source scanning may help distinguish docs, config, test, frontend reference, or true backend implementation

So the best result comes from combining both.

## Recommended Mental Model

Use source scanning when you want implementation context.
Use CBOM when you want inventory portability and governance.
Use both together when you want stronger migration planning input.

In short:

- generating CBOM is useful for portability and governance
- ingesting CBOM is useful for enrichment, reuse, and partial-information scenarios
