"""Deterministically write synthetic Roster fixtures to data/. Seeded; no real people."""
import json, random
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
SEED = 42

ONTOLOGY = [
    {"skill_id": "py", "name": "Python", "aliases": ["python", "pytest", "pandas"]},
    {"skill_id": "ml", "name": "Machine Learning", "aliases": ["machine learning", "model", "scikit", "training"]},
    {"skill_id": "llm", "name": "LLM Engineering", "aliases": ["llm", "prompt", "rag", "agent", "langgraph"]},
    {"skill_id": "data", "name": "Data Engineering", "aliases": ["sql", "etl", "pipeline", "warehouse", "dbt"]},
    {"skill_id": "lead", "name": "Technical Leadership", "aliases": ["led", "mentored", "roadmap", "stakeholder"]},
    {"skill_id": "cloud", "name": "Cloud Architecture", "aliases": ["aws", "terraform", "bedrock", "infra"]},
    {"skill_id": "fe", "name": "Frontend", "aliases": ["react", "typescript", "ui", "streamlit"]},
]

def _artifact(i, atype, text, date):
    return {"id": f"a{i}", "type": atype, "text": text, "date": date}

def build():
    rnd = random.Random(SEED)
    workers = []
    # Maria: strong evidence of LLM work she did NOT self-report (hidden strength); age 50+
    workers.append({
        "id": "w-maria", "name": "Maria Alvarez", "current_role": "Data Engineer",
        "tenure_years": 7,
        "artifacts": [
            _artifact(1, "pr", "Built a RAG agent with LangGraph and prompt routing", "2026-05-20"),
            _artifact(2, "commit", "tune retrieval model training loop", "2026-05-02"),
            _artifact(3, "doc", "ETL pipeline + warehouse dbt design", "2026-04-10"),
            _artifact(4, "pr", "Python pandas refactor with pytest", "2026-06-01"),
        ],
        "self_reported_skills": ["Python", "Data Engineering"],  # NOTE: no LLM claim
        "protected": {"gender": "F", "age_band": "50+", "ethnicity": "Hispanic"},
    })
    names = ["Alex Kim","Sam Patel","Jordan Lee","Riley Cohen","Casey Wong","Drew Olsen",
             "Taylor Reed","Jamie Ford","Morgan Diaz","Avery Singh","Pat Nolan"]
    roles = ["Software Engineer","Data Engineer","ML Engineer","Product Analyst"]
    bands = ["20-29","30-39","40-49","50+"]
    skillsets = [["Python","Machine Learning"],["Python","LLM Engineering"],
                 ["Data Engineering","Python"],["Cloud Architecture","Python"],
                 ["Technical Leadership","Python"],["Frontend","Python"]]
    texts = {
        "Python": "python pandas pytest refactor", "Machine Learning": "model training scikit",
        "LLM Engineering": "llm prompt rag agent", "Data Engineering": "sql etl pipeline dbt",
        "Cloud Architecture": "aws terraform bedrock infra", "Technical Leadership": "led mentored roadmap",
        "Frontend": "react typescript ui",
    }
    for i, nm in enumerate(names):
        sset = skillsets[i % len(skillsets)]
        arts = [_artifact(100 + i * 10 + j, ("pr" if j == 0 else "commit"),
                          texts[s], f"2026-0{(i % 5) + 1}-1{j}") for j, s in enumerate(sset)]
        workers.append({
            "id": f"w-{i}", "name": nm, "current_role": roles[i % len(roles)],
            "tenure_years": 2 + (i % 8), "artifacts": arts,
            "self_reported_skills": sset,
            "protected": {"gender": ("F" if i % 2 else "M"),
                          "age_band": bands[i % len(bands)],
                          "ethnicity": ["White","Black","Asian","Hispanic"][i % 4]},
        })

    seats = [
        {"id": "s-llm-lead", "type": "gig", "title": "LLM Platform Lead (stretch)",
         "required_skills": ["llm", "lead", "py"], "stretch": True},
        {"id": "s-ml-stretch", "type": "gig", "title": "ML Tech Lead (stretch)",
         "required_skills": ["ml", "lead", "py"], "stretch": True},
        {"id": "s-data", "type": "role", "title": "Senior Data Engineer",
         "required_skills": ["data", "py"], "stretch": False},
        {"id": "s-cloud", "type": "role", "title": "Cloud Architect",
         "required_skills": ["cloud", "py"], "stretch": False},
        {"id": "s-fe", "type": "role", "title": "Frontend Engineer",
         "required_skills": ["fe", "py"], "stretch": False},
    ]

    # Seeded dashboard history: monthly activity vs outcomes + fairness drift.
    months = ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06"]
    outcomes = []
    for m in months:
        outcomes.append({
            "month": m,
            "matches_surfaced": 40 + rnd.randint(0, 20),       # activity
            "placements": 6 + rnd.randint(0, 6),               # activity
            "regrettable_attrition_rate": round(0.12 - 0.01 * months.index(m), 3),  # outcome ↓
            "time_to_productivity_days": 70 - 4 * months.index(m),                  # outcome ↓
            "internal_fill_rate": round(0.45 + 0.03 * months.index(m), 3),          # outcome ↑
            "opportunity_impact_ratio": round(0.70 + 0.04 * months.index(m), 3),    # fairness ↑→1.0
            "override_rate": round(0.30 - 0.02 * months.index(m), 3),               # trust
        })
    return ONTOLOGY, workers, seats, outcomes

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    ont, workers, seats, outcomes = build()
    for name, obj in [("ontology.json", ont), ("workers.json", workers),
                      ("seats.json", seats), ("outcomes_history.json", outcomes)]:
        (DATA / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    main()
