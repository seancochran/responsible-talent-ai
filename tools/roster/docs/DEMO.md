# Roster — Demo Runbook

A tight, ~90-second walkthrough that shows Roster grounding skills in evidence,
matching to the right seats, catching disparate treatment, and measuring outcomes.
Runs fully offline with no API key.

## One-time setup

```bash
cd tools/roster
python3 -m pip install -r requirements.txt        # streamlit, pandas, numpy, scikit-learn, langgraph
python3 scripts/generate_sample.py                 # writes seeded synthetic data/ (deterministic)
```

## Run

```bash
cd tools/roster
streamlit run app.py
```

The app opens at `http://localhost:8501`. The caption reads *"No LLM provider set
(deterministic mode)"* — that is expected; everything works key-free. (Optional:
set `LLM_PROVIDER` + a key per `.env.example` to enable LLM-polished explanations.)

## The walkthrough (Decision view, worker = **Maria Alvarez** — the default)

Five beats. Suggested spoken line in *italics*; what to look at in plain text.

1. **Evidence-grounded skills — the hidden strength.**
   The green banner reads **"Hidden strengths (evidenced, never self-reported):
   LLM Engineering."**
   *"Maria never claimed LLM skills, but her actual work — shipping a RAG agent —
   proves them. A claims-based skills graph misses this entirely; Roster reads the
   evidence."*

2. **Right-seat ranking — explainable matches.**
   Scroll to the ranked seats. Each has a fit % and a one-line explanation naming
   the matched skills, the evidence, and the gaps.
   *"Every match is explainable and grounded in evidence, not a black-box score —
   here's what she's matched on and what's missing."*

3. **Fairness red-team — the disparate-treatment flip (the centerpiece).**
   The red banner reads **"Disparate treatment on `age_band`: surfaced stretch
   seats changed from [none] to [ML Tech Lead (stretch)] when only the protected
   attribute was flipped."**
   *"This is a counterfactual matched-pair test. We flip only Maria's age band —
   nothing about her qualifications — and a stretch-role recommendation appears
   that wasn't there before. That's disparate treatment, caught with the receipt."*
   Below it, the aggregate four-fifths impact JSON shows the group-level view.

4. **Governance record — recorded dissent + human sign-off.**
   The dissent bullets capture both the treatment flag and the impact flag. Set a
   reviewer + decision and click **Sign off** → a confirmation appears. Then
   **Download audit record (JSON)** produces the machine-checkable record.
   *"Nothing is auto-decided. The system records its dissent and routes to a human
   to sign off — AI supports the judgment, it doesn't replace it — and emits an
   auditable record."*

5. **Outcomes dashboard — outcomes, not activity.**
   Switch the sidebar to **Outcomes dashboard**. Three outcome metrics
   (regrettable attrition ↓, time-to-productivity ↓, internal-fill ↑, all green =
   improving), an activity chart labeled *"context, not the goal,"* and fairness-
   drift + override-rate trends.
   *"And we measure what actually matters — did placements reduce regrettable
   attrition and speed time-to-productivity — plus whether fairness is improving
   over time. Outcomes, not activity."*

## The one-sentence frame

> *Roster is the trust layer on top of the talent tools you already own: it grounds
> skills in real evidence, matches fairly, and proves the outcome — the part no
> vendor sells you because it has to be the thing that watches the vendors.*

## Reset between runs

State is recomputed on every interaction; just reselect **Maria Alvarez** (or
re-run `streamlit run app.py`). To regenerate data: `python3 scripts/generate_sample.py`.

## What's real vs. mocked

- **Real:** the full skills-intelligence → matching → fairness → governance →
  dashboard logic, the LangGraph pipeline, and the deterministic + optional-LLM paths.
- **Mocked:** the Workday/Eightfold connectors (interface mirrors the real APIs;
  swap the mock for a live endpoint to go live) and the dashboard's historical
  series (seeded synthetic).
- **Design-only:** the AWS/Bedrock production architecture (`docs/architecture.md`).

Synthetic data only — no real people. Screening aid, not legal advice.
