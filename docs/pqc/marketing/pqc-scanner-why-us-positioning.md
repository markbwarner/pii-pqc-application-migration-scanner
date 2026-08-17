# Why Use This PQC Scanner Versus Other Crypto Inventory Tools

This document is intended to help position the Application PQC Readiness Scanner Assessment Tool against CBOM generators, static-analysis frameworks, network-monitoring tools, simple code scanners, and enterprise cryptographic inventory products.

The goal is not to argue that other tools are unnecessary. The goal is to explain where this scanner is differentiated and why a customer may want to use it first, or use it together with those other tools.

## Short Positioning Statement

Most crypto inventory tools are very good at telling you **what cryptography exists**.

This scanner is designed to help answer the harder delivery question:

**What is most likely to change, who will likely need to change it, and how much migration effort is it likely to take?**

That is why it is best positioned as an **application migration planning scanner**, not just an inventory scanner.

## The Core Buyer Message

A customer often does not need just another list of algorithms, certificates, or crypto libraries.

They usually need to know:

- which files are likely true migration owners
- which findings are implementation-heavy versus reference-only
- which back-end services matter more than front-end references
- which applications are higher-likelihood change targets
- which migration work packages should be reviewed first
- how to export the output into project-planning, architecture-review, or remediation workflows

That is where this scanner is strongest.

## Where This Scanner Is Differentiated

### 1. Easier To Use For Migration Planning

Many tools are optimized for inventory creation, policy validation, or broad enterprise discovery.

This scanner is optimized for planning questions such as:

- where are the real post-quantum migration touchpoints
- what is likely only passive evidence
- what looks like a protocol-stack change
- what looks like signing or certificate-lifecycle work
- what should a team review first

The output is designed to be understandable by architects, project planners, application teams, and security teams without requiring them to build a separate analytics pipeline first.

### 2. Better At File-Level Change Prioritization

This scanner produces file-level findings and recommended actions such as:

- `review_pqc_protocol_stack`
- `review_pqc_application_signing`
- `review_pqc_dependency_and_kms`
- `review_pqc_certificate_lifecycle`
- `reference_only_frontend`
- `reference_only_or_low_priority`

That is materially different from a generic inventory report because it helps separate:

- likely implementation work
- dependency review work
- certificate lifecycle work
- lower-priority reference evidence

### 3. Better At Distinguishing Reference From Implementation

One of the most common frustrations with broad discovery tools is that they often show the presence of a crypto library, certificate file, or API family without making it easy to see whether that finding is:

- a true implementation path
- a wrapper or abstraction layer
- a passive dependency
- a frontend reference
- a documentation or configuration artifact

This scanner is designed to help reduce that ambiguity.

### 4. Better For Multi-Tier Application Analysis

In many enterprises, the question is not just "where is RSA or TLS visible?"

The real question is:

**Which tier is the likely migration owner?**

This scanner is stronger than most inventory-first tools at highlighting:

- frontend versus backend context
- likely implementation-heavy files
- likely lower-priority reference-only files
- more actionable change-target groupings

That is especially valuable in large enterprise environments where front-end references can overstate true migration scope.

### 5. Better Output Options For Working Teams

This scanner already supports output formats that are useful for actual remediation planning:

- JSON outputs for system-to-system processing
- CSV outputs for Excel, Power Query, and BI workflows
- HTML reports for executive or architecture review
- CBOM import and export support

This matters because customers often need to move quickly from scan results to:

- architecture workshops
- project plans
- change-owner reviews
- remediation tracking

### 6. Stronger For Custom Wrapper And Swagger / OpenAPI Onboarding

Many real customer environments do not call vendor crypto APIs directly in a clean, obvious way.

They often use:

- internal wrappers
- custom security helper libraries
- shared API clients
- generated OpenAPI or Swagger clients

This scanner has a better story than many inventory-only tools for onboarding those patterns into the scan model so they can be recognized and grouped in a repeatable way.

### 7. Better At Turning Findings Into Work Packages

Many tools stop at:

- inventory
- exposure
- dashboard findings

This scanner is better positioned to support:

- migration review queues
- application-team triage
- likely owner identification
- recommended action grouping
- initial effort sizing

That makes it more useful for real program execution.

## How To Position The Other Tool Families

The strongest message is not that other tools are bad.

It is that they answer **different questions**.

### CBOM / CycloneDX Tools

Best at:

- portable machine-readable crypto inventories
- dependency baselines
- governance and exchange formats

Less strong at:

- determining likely change owners
- file-level migration prioritization
- differentiating implementation from reference-only context

### Static Analysis Frameworks Such As CodeQL Or SonarQube Plugins

Best at:

- customizable rules
- integration with existing code-scanning platforms
- developer-centric static findings

Less strong at:

- out-of-the-box migration work package planning
- ownership-oriented reporting
- program-level prioritization without additional rule and reporting work

### Network Monitoring Tools Such As Zeek

Best at:

- observing deployed TLS, ciphers, certificates, and protocol behavior
- understanding real runtime posture

Less strong at:

- file-level remediation ownership
- source-code attribution
- explaining which development teams are likely to change which files

### Simple Grep-Like Scanners

Best at:

- speed
- low cost
- first-pass triage

Less strong at:

- context
- prioritization
- confidence
- ownership grouping
- export quality for structured remediation planning

### Enterprise Crypto Discovery Products

Best at:

- broad estate visibility
- asset coverage
- key, certificate, service, and policy posture
- enterprise dashboards

Less strong at:

- source-level change planning
- file-by-file developer worklists
- implementation-versus-reference separation
- migration effort estimation

## Best Customer-Facing Positioning

If you want a short message for a slide, brochure, or sales discussion:

> CBOM and discovery tools are good at telling you what cryptography exists.  
> This scanner is designed to tell you what is most likely to change, who likely owns the change, and how to turn those findings into an application migration plan.

## Best Use Cases For This Scanner

This scanner is especially strong when the customer wants to:

- narrow true migration scope
- prioritize likely change targets
- distinguish backend implementation from frontend awareness
- identify likely application teams that need to engage
- create Excel- or BI-friendly worklists
- export findings into JSON, CSV, HTML, and CBOM-driven workflows
- onboard custom wrappers or Swagger/OpenAPI-generated clients into the scan story

## Suggested Competitive Themes

These are safe and useful themes to emphasize:

- **Ease of use**
  - faster to move from findings to planning output
- **Actionable outputs**
  - JSON, CSV, HTML, and change-target worklists
- **Migration specificity**
  - built for planning, not just inventory
- **Ownership context**
  - helps identify likely change owners
- **Multi-tier awareness**
  - better at separating frontend references from backend implementation paths
- **Extensibility**
  - supports custom wrappers, CBOM enrichment, and Swagger/OpenAPI onboarding
- **Program-planning value**
  - better suited to architecture reviews, effort sizing, and remediation sequencing

## A Good Closing Message

Customers do not usually struggle to generate more findings.

They struggle to determine:

- which findings matter first
- which teams should act
- which files are likely to change
- how to scope the migration realistically

That is the reason to lead with this scanner.
