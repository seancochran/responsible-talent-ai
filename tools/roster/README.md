# Roster

**Roster grounds skills in verifiable evidence, then matches people to the right
seats — fairly, auditably, and measured by outcomes.** It is a trust layer that
sits on top of Workday + Eightfold (mocked here), not a replacement for them.

## Why
Skills graphs run on self-reported or claim-inferred data with no evidence trail.
Roster builds evidence-grounded skill profiles (with provenance), surfaces hidden
strengths, matches to seats, red-teams the matching for disparate treatment and
impact, records an auditable decision, and measures outcomes — not activity.

## Run (no API key needed)
```bash
cd tools/roster
pip install -r requirements.txt
python scripts/generate_sample.py
streamlit run app.py
```
Select **Maria Alvarez** to see a hidden strength surfaced and a disparate-treatment
flag the mock vendor would have hidden.

## Optional LLM polish
Set `LLM_PROVIDER` + the matching key (see `.env.example`). Everything works without it.

## Design
- Spec: `../../docs/superpowers/specs/2026-06-28-roster-design.md`
- Architecture: `docs/architecture.md`
- Build/buy/integrate, fairness method, and KPIs are described in the spec.

Screening aid — not legal advice, not a compliance certification.
