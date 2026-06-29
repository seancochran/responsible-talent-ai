# Roster — Design Spec

> **Roster grounds skills in verifiable evidence, then matches people to the right
> seats — fairly, auditably, and measured by outcomes.** It is a trust-and-measurement
> layer that sits on top of the talent platforms an organization already owns
> (Workday, Eightfold), rather than replacing them.

Status: **design approved → implementation planning.** Part of the
`responsible-talent-ai` suite; reuses the bias-auditor's `adverse_impact` module.

---

## 1. Problem

Every talent platform — Workday Skills Cloud, Eightfold, internal marketplaces —
runs on a skills graph that is **self-reported or inferred from *claimed* career
data** (titles, résumé text). Even the inference-based systems predict skills from
claims, not from demonstrated work, and **none carry an evidence trail**.

Two consequences:

1. **Garbage-in matching.** You cannot put the right person in the right seat if
   the skills data is shallow, stale, or inflated. Generative AI has made the
   underlying artifacts (résumés, profiles, writing samples) trivially fakeable,
   so claim-based skills data is degrading further.
2. **Unaccountable fairness.** When a system decides *who gets surfaced* for the
   best roles and stretch assignments, that is opportunity allocation. Vendors
   optimize the match; almost none independently test whether the allocation
   exhibits disparate treatment, give the deployer a vendor-neutral audit record,
   or measure whether placements actually improved outcomes.

**Roster fixes the foundation, then governs the decision.** It builds
evidence-grounded skill profiles (with receipts), matches people to seats on that
stronger foundation, stress-tests the matching for fairness, records every
decision auditably, and measures outcomes — not activity.

## 2. Goals / non-goals

**Goals**
- Identify, classify, and **verify** skills from real work artifacts, with a
  provenance receipt for every inferred skill.
- Rank best-fit internal **seats** (roles *and* stretch gigs) for a person, with a
  human-readable explanation per match.
- Detect disparate **treatment** (counterfactual matched-pairs) and disparate
  **impact** (aggregate adverse-impact) in *who gets surfaced*.
- Emit an auditable decision record with a human sign-off gate.
- Measure **outcomes** (regrettable-attrition proxy, time-to-productivity,
  internal-fill rate) and fairness drift over time.
- Run **key-free and offline** via a deterministic fallback; upgrade to LLM agents
  when a provider key is present.

**Non-goals**
- Roster does **not** make hiring/placement decisions. It instruments and audits a
  *human* decision ("AI supports judgment, it does not replace it").
- Roster does **not** re-implement skills *matching as a commodity*; it consumes a
  baseline match (mock Eightfold) and adds the trust/evidence/fairness/outcomes
  layer on top. Build vs. buy is explicit (§3).
- No real personal data. Synthetic, seeded data only.

## 3. Architecture — build / buy / integrate

```
┌─ WORKDAY  (system of record) ─────────────────────────────┐  INTEGRATE
│  worker profiles · open positions/seats · performance ·   │  (mock adapter,
│  post-move outcomes        [REST · RaaS reports · WWS]     │   real-API shape)
└───────────────────────────┬───────────────────────────────┘
                            │ WorkdayClient
                            ▼
┌─ EIGHTFOLD  (match engine) ───────────────────────────────┐  BUY / INTEGRATE
│  baseline skill inference + person↔role fit scores        │  (mock adapter)
│  [Position: Get Matching Candidates · minStarThreshold]   │
└───────────────────────────┬───────────────────────────────┘
                            │ EightfoldClient
                            ▼
╔═ ROSTER — trust & measurement layer (BUILD) ══════════════════════════╗
║  ① Skills Intelligence   evidence → classified skills + provenance    ║
║  ② Right-Seat Matching   evidence-grounded fit + per-seat explanation ║
║  ③ Fairness Red-Team     counterfactual treatment + adverse impact    ║
║  ④ Governance Record     receipts · recorded dissent · HITL sign-off  ║
║  ⑤ Outcomes Dashboard    activity vs. OUTCOMES · fairness drift        ║
╚════════════════════════════╤══════════════════════════════════════════╝
                             │ write-back
                             ├─► audit record → Workday
                             └─► metrics → Outcomes store
```

**Reference deployment target (AWS).** In production the LLM agents run via **Amazon
Bedrock** behind **Bedrock Guardrails**; PII is redacted at ingest; the audit
record is written to an immutable event store. The LangGraph orchestration is the
application tier. The demo runs locally against mock adapters; the cloud reference
architecture is delivered as a diagram + this design, not provisioned infra.

**The build/buy/integrate rationale** (the layer is deliberately *not* a purchase):
- The **match** is commodity — *buy* it (Eightfold/Workday already do skills
  inference + matching).
- Profiles, seats, and outcomes live in the system of record — *integrate* (Workday
  APIs).
- The **trust + evidence + fairness + outcomes** layer must be *vendor-neutral by
  definition* — you cannot outsource auditing a vendor to that same vendor — and it
  encodes organization-specific judgment vendors do not model. Therefore *build*.

## 4. Components

### ① Skills Intelligence (the core — a LangGraph pipeline)
Input: a worker's real artifacts (commits/PRs, docs, tickets, shipped work
descriptions — synthetic in the demo). Stages:

1. **Extract** — artifacts → raw skill signals.
2. **Classify** — normalize signals to a published ontology (Lightcast Open Skills
   taxonomy) → stable skill IDs.
3. **Score** — proficiency + **recency** per skill (depth × frequency × recency),
   not a binary "has skill".
4. **Evidence-link** — each skill carries a **provenance receipt** (the specific
   artifact that substantiates it). Auditable, not a black box.
5. **Reconcile** — evidence-skills vs. self-reported/claimed skills → flag **gaps**
   (claimed, no evidence) and **hidden strengths** (evidence, never claimed).
6. **Fairness guard** — verify that evidence *availability/type* does not proxy a
   protected attribute (e.g., public-repo access correlates with free time).

### ② Right-Seat Matching
Consumes the evidence-grounded profile plus the baseline (mock Eightfold) fit
score; ranks **seats** — permanent roles *and* stretch gigs — and produces a
per-seat **explanation** (matched skills, adjacent skills, gaps). Default ranking
is deterministic (TF-IDF cosine + evidence weighting); LLM polish is optional.

### ③ Fairness Red-Team
- **Counterfactual (disparate treatment):** an adversary generates matched-pair
  variants of a profile flipping only protected proxies (name→gender/ethnicity
  signal, grad-year→age, caregiving gap) while holding qualifications constant;
  re-runs matching; flags any change to the surfaced seat set, with the pair as the
  receipt.
- **Adverse impact (disparate impact):** **reuses `adverse_impact`** from the
  bias-auditor on the surfaced-vs-not outcome by group (four-fifths ratio +
  two-proportion z-test + small-sample flags).

### ④ Governance Record
Per-decision audit record: recommendation, evidence receipts, the counterfactual
results, fairness flags, recorded dissent, and a **human-in-the-loop sign-off**
gate. Carries an explicit caveat ("screening aid — not legal advice, not a
compliance certification").

### ⑤ Outcomes & Fairness Dashboard
Separates **activity** (matches surfaced) from **outcomes**:
- Outcome: regrettable-attrition proxy, time-to-productivity, internal-fill rate,
  placement-retention.
- Fairness: opportunity adverse-impact ratio by group, counterfactual flip rate,
  stretch-role access parity.
- Trust/adoption: human override rate, % decisions with recorded dissent, sign-off
  latency.

Seeded with synthetic history spanning multiple talent pillars (acquisition,
management/mobility, comp, operations); all clearly labeled synthetic.

### Mock integration adapters
`WorkdayClient` and `EightfoldClient` expose methods whose **shapes mirror the real
APIs** (Workday objects such as `Worker`, `Job_Requisition`, `Job_Posting`;
Eightfold "matching candidates / matching jobs" with `minStarThreshold`), backed
by seeded synthetic fixtures. Swapping a mock for the real endpoint is a
constructor change. (Source notes: `connector-api-reference.md`.)

## 5. Data model (synthetic)

- `worker`: id, current_role, tenure, artifacts[], self_reported_skills[],
  protected_attributes{} (synthetic, used only by the fairness module).
- `skill_claim`: skill_id, source (self|inferred|evidence), proficiency, recency,
  evidence_ref?.
- `seat`: id, type (role|gig), title, required_skills[], visibility (stretch flag).
- `match`: worker_id, seat_id, score, explanation, evidence_refs[].
- `decision_record`: match, counterfactual_results[], fairness_flags[], dissent[],
  signoff{by,at,decision}.
- `outcome_event`: decision_id, metric, value, observed_at.

## 6. LLM strategy

- **Model-agnostic** provider layer (`LLM_PROVIDER` = `anthropic` | `openai` |
  `gemini`, lazy SDK import) — reuse the bias-auditor `src/llm.py` pattern.
- **Deterministic zero-key fallback** for every agent stage, so the app runs
  offline and the live demo cannot fail on a network/key error. The LLM is an
  *enhancement*, never a hard dependency.
- **LangGraph `StateGraph`** orchestrates the Skills Intelligence pipeline and the
  Fairness Red-Team. The typed shared state object *is* the accumulating decision
  record; parallel fan-out (panel/red-team) and a human-in-the-loop interrupt
  (sign-off gate) are graph primitives, so the audit artifact is a byproduct of the
  architecture.
- Each node uses structured output (Pydantic schema) so every contribution to the
  record is schema-validated and machine-checkable.
- **Stretch only:** a Gemini Live multimodal "skills interview" capture feeding a
  profile; explicitly out of the core build.

## 7. Governance & security (designed in, not bolted on)

Synthetic data only · PII redaction at ingest · Bedrock Guardrails
(prompt-injection / abuse) in the reference deployment · immutable audit store ·
human-in-the-loop sign-off · explainability on every score · explicit non-legal
caveat. Delivered as design + diagram, not provisioned infrastructure.

## 8. Tech stack & repo layout

Python 3.10+, Streamlit, pandas, numpy, scikit-learn (TF-IDF default, no key),
LangGraph; optional provider SDKs commented in requirements. Stats implemented by
hand (no scipy), consistent with the suite. Lives at `tools/roster/`:

```
tools/roster/
├── app.py                      # Streamlit UI
├── src/
│   ├── skills_intelligence.py  # extract→classify→score→evidence→reconcile→guard
│   ├── matching.py             # right-seat ranking + explanations
│   ├── fairness_redteam.py     # counterfactual generation + detection
│   ├── adverse_impact.py       # reused from bias-auditor (shared)
│   ├── governance.py           # decision record + sign-off
│   ├── graph.py                # LangGraph StateGraph wiring
│   ├── llm.py                  # provider-agnostic client (copy from bias-auditor)
│   └── connectors/
│       ├── workday.py          # WorkdayClient (mock, real-API shape)
│       └── eightfold.py        # EightfoldClient (mock)
├── scripts/generate_sample.py  # seeded synthetic workers/seats/outcomes
├── data/                       # sample fixtures
├── tests/                      # pytest for all deterministic logic
├── requirements.txt  .env.example  README.md  LICENSE
```

## 9. Scope (what is built vs. mocked vs. diagrammed)

- **Built for real (key-free):** Skills Intelligence pipeline, Right-Seat matcher +
  explanations, Fairness Red-Team, Governance Record, Outcomes Dashboard, mock
  adapters.
- **Mocked / seeded:** Workday + Eightfold adapters (interface mirrors real APIs);
  cross-pillar dashboard history (labeled synthetic).
- **Diagram only:** the AWS / Bedrock reference architecture + security design.
- **Stretch (only if time):** Gemini Live multimodal capture; seat→people
  (manager-side) flip.

## 10. Demo walkthrough (~90 seconds)

1. Pick a worker → Roster builds the **evidence-grounded** skill profile, surfacing
   a **hidden strength** the baseline missed.
2. **Right-seat ranking** with per-seat explanations.
3. **"Stress-test fairness"** → a counterfactual twin flips a stretch-seat
   recommendation → flagged with the receipt.
4. **Governance record** renders → human sign-off.
5. **Zoom out to the dashboard** — the decision is one point in an outcomes (not
   activity) and fairness-drift view across pillars.

## 11. Testing

Unit tests on all deterministic logic: classification mapping, proficiency/recency
scoring, evidence-linking, reconciliation (gaps/hidden strengths), matcher ranking,
counterfactual generation, and the reused adverse-impact math. Cast numpy results
to native Python types (numpy `bool_`/`float64` break `is`/JSON). One end-to-end
"golden path" test over the seeded sample, exercised on the deterministic
(key-free) path so CI needs no provider key.

## 12. Build order

1. Seeded synthetic data + mock connectors (`generate_sample.py`, `connectors/`).
2. Skills Intelligence deterministic core + tests.
3. Right-Seat matching + explanations + tests.
4. Fairness Red-Team (counterfactual + reused adverse-impact) + tests.
5. Governance record + sign-off.
6. LangGraph wiring + optional LLM enhancement behind the fallback.
7. Streamlit UI + Outcomes dashboard.
8. AWS/Bedrock reference-architecture diagram; suite README update.
