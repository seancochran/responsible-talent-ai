# Roster — Reference Architecture (AWS)

Roster is a trust-and-measurement layer over the talent platforms an org already
owns. The demo runs locally on mock adapters; production targets AWS.

```mermaid
flowchart TD
  WD[(Workday — system of record\nprofiles · seats · outcomes)] -->|RaaS / REST| ING
  EF[(Eightfold — match engine\nbaseline fit scores)] -->|API| ING
  subgraph ROSTER[Roster trust layer · AWS]
    ING[Ingest + PII redaction] --> SI[Skills Intelligence\nLangGraph]
    SI --> MM[Right-Seat Matching]
    MM --> FR[Fairness Red-Team\ncounterfactual + adverse impact]
    FR --> GV[Governance Record\nHITL sign-off]
    BR{{Amazon Bedrock + Guardrails}} -.serves LLM nodes.- SI
    BR -.-> FR
    GV --> ES[(Immutable audit store)]
    GV --> OS[(Outcomes store)]
  end
  GV -->|write-back| WD
  OS --> DASH[Outcomes & Fairness Dashboard]
```

**Security/governance controls:** PII redaction at ingest; Bedrock Guardrails for
prompt-injection/abuse; immutable audit store; human-in-the-loop sign-off;
explainability on every score; synthetic data only in this build.
