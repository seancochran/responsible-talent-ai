# ⚖️ Talent Bias & Adverse-Impact Auditor

A lightweight, provider-agnostic tool that flags potential **adverse impact** in
hiring or promotion data using the EEOC **four-fifths (80%) rule** plus a
two-proportion significance test — and (optionally) writes a plain-English audit
narrative for HR and Legal stakeholders.

Built as a portfolio prototype for applied-AI work in the **Talent / People**
domain: the kind of governance layer most teams shipping hiring AI still lack.

> **Why this matters.** Algorithmic-hiring discrimination is no longer
> theoretical. *Mobley v. Workday* is now a certified ADEA collective action;
> NYC Local Law 144 mandates independent bias audits; Colorado's AI Act and the
> EU AI Act (employment AI = "high-risk," obligations from Aug 2, 2026) are
> landing. This tool does the first thing any responsible Talent AI team should
> do: measure selection rates by group and surface disparities *before* a
> regulator or plaintiff does.

---

## What it does

- Reads candidate-level CSV data (one row per applicant).
- Computes, for each protected attribute you choose:
  - selection rate per group,
  - **impact ratio** vs. the highest-rate (reference) group,
  - a **four-fifths-rule flag** when the ratio falls below 0.80,
  - a **two-proportion z-test** p-value (significance) vs. the reference,
  - a small-sample warning (N < 30).
- Produces a deterministic, source-linked **audit summary** (works with no API
  key) and an optional **LLM stakeholder narrative**.
- Exports a Markdown report.

## Screenshot / demo flow

1. `streamlit run app.py`
2. Click **Use sample data** (a synthetic funnel with a deliberately embedded
   disparity).
3. Pick `gender` and `race_ethnicity` as attributes, `hired` as the outcome.
4. The sample clearly flags **Female** (impact ratio 0.62, p < 0.001) and
   **Black** (0.58, p = 0.008) — both statistically significant.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# optional: enable the LLM narrative
cp .env.example .env        # then add ONE provider key

streamlit run app.py
```

Regenerate the synthetic sample any time:

```bash
python scripts/generate_sample.py
```

Run the tests:

```bash
pip install pytest && pytest -q
```

## Provider-agnostic by design

Set `LLM_PROVIDER` to `openai`, `anthropic`, or `gemini` and supply the matching
key (see `.env.example`). Only the SDK you choose is imported. With no provider
set, the app runs fully in **deterministic mode** — the math and the rule-based
narrative need no LLM at all.

## Input format

| column | meaning |
|---|---|
| protected attribute(s) | e.g. `gender`, `race_ethnicity`, `age_group` (categorical) |
| outcome | a binary decision column, e.g. `hired` (`1/0`, `yes/no`, `hired`, `advanced`…) |

Anything else (IDs, department, stage) is ignored by the analysis but fine to
keep in the file. To analyze a specific funnel stage (e.g. screen → interview),
point the outcome column at that stage's pass/fail flag.

## Methodology & honest limits

- The **four-fifths rule** is the EEOC's rule-of-thumb *trigger* for review, not
  a verdict. A flagged practice can still be lawful if it is **job-related and
  consistent with business necessity** and no less-discriminatory alternative
  exists.
- The reference group follows the common convention of the **highest selection
  rate** group.
- Significance uses a pooled two-proportion z-test (normal approximation); for
  small samples treat results as directional.
- This is a **screening and monitoring aid — not legal advice and not a
  compliance certification.** Real audits (e.g., NYC LL 144) require an
  independent auditor and additional rigor.

## Project layout

```
talent-bias-auditor/
├── app.py                      # Streamlit UI
├── src/
│   ├── adverse_impact.py       # four-fifths + z-test (no scipy)
│   ├── narrative.py            # deterministic + LLM narratives
│   └── llm.py                  # provider-agnostic LLM client
├── scripts/generate_sample.py  # synthetic demo data
├── data/sample_hiring_funnel.csv
└── tests/test_adverse_impact.py
```

## Roadmap (the rest of the suite)

This is the first tool in a small **Responsible Talent AI** set. Planned
companions: a structured-interview-kit + bias-aware rubric generator, a
job-description inclusivity rewriter, and a Greenhouse-MCP recruiting copilot
with PII redaction.

---

*Author: Sean Cochran. Synthetic data only; no real candidates. MIT License.*
