# Responsible Talent AI

A small suite of **working, demoable prototypes** for trustworthy, measurable
Talent / People AI. The thesis is simple: AI in hiring and internal mobility
should be **governance-aware, explainable, and measured by outcomes** — not
bolted-on activity dashboards. Each tool here is built to prove that thesis on
real-shaped (synthetic) data, with a deterministic core that runs offline.

> **Honest framing.** These are *builds*, not artifacts of prior HR employment.
> They demonstrate domain fluency and an engineering point of view on
> responsible Talent AI. All data is synthetic; no real people are represented.
> Any projected or estimated figures are labeled as such. None of these tools is
> legal advice or a compliance certification — each is a screening/decision aid
> with a human in the loop.

---

## Why this matters

Algorithmic-hiring discrimination is no longer theoretical. *Mobley v. Workday*
is a certified ADEA collective action; NYC **Local Law 144** mandates independent
bias audits; **Colorado's AI Act** and the **EU AI Act** (employment AI =
"high-risk," obligations from Aug 2, 2026) are landing. Talent teams shipping AI
need a trust-and-measurement layer most of them still lack. This suite is what
that layer looks like, tool by tool.

## The suite

| Tool | What it does | Status |
|------|--------------|--------|
| [**Bias & Adverse-Impact Auditor**](tools/bias-auditor/) | Upload hiring/promotion CSV → selection rates, EEOC four-fifths impact ratios, two-proportion z-test significance, small-sample flags, downloadable audit report + optional LLM stakeholder narrative. | ✅ Complete, tested, demo-ready |
| **Internal Mobility & Skills Match** | Rank best-fit internal roles for an employee by skill adjacency, *explain* each match, and run an adverse-impact check on *who gets surfaced* by group. | 🔜 Next |
| **Coaching / Interview-Practice bot** | Rehearse an interview/coaching scenario against a simulated persona; get rubric-scored feedback + improvement tips. | 📋 Backlog |
| **Workforce Trust screener** | Surface anomaly / authenticity signals across applications (identity-drift, inconsistency, AI-generated-text) into a first-pass human review note. | 📋 Backlog |

## Design principles (every tool follows these)

1. **Runs with zero API keys.** A deterministic core works fully offline. The LLM
   is an *optional enhancement*, never a hard dependency.
2. **Model-agnostic LLM.** A shared provider-agnostic client (`LLM_PROVIDER` =
   `openai` | `anthropic` | `gemini`, lazy SDK import) — no lock-in.
3. **Streamlit demo UI** with a one-click "Use sample data" path, so a demo needs
   no setup.
4. **Synthetic data only**, shipped seeded and deterministic.
5. **Governance-aware by default** — human-in-the-loop, explainability on every
   score/recommendation, explicit "decision aid, not legal advice" caveats, and
   an adverse-impact check anywhere the tool touches a hiring decision.
6. **Tested deterministic logic** (pytest).
7. **Portfolio-grade docs** — lead with the *why* and the domain stakes.

## Repo layout

```
responsible-talent-ai/
├── README.md            # you are here — frames the suite
├── LICENSE              # MIT
├── .gitignore
└── tools/
    └── bias-auditor/    # each tool is self-contained: app.py, src/, tests/, data/, README
```

Each tool is self-contained and runnable on its own. Shared patterns (the
provider-agnostic `llm.py`, the `adverse_impact` module) are reused across tools.

## Quickstart

```bash
cd tools/bias-auditor
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py        # then click "Use sample data"
```

See each tool's own README for its demo flow and details.

## License

MIT — see [LICENSE](LICENSE).
