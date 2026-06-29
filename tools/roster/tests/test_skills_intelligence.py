from datetime import date
from pathlib import Path
from src.ontology import Ontology
import src.skills_intelligence as si

ONT = Ontology.load(Path(__file__).resolve().parents[1] / "data" / "ontology.json")

WORKER = {
    "id": "w-test", "name": "Test", "current_role": "Eng", "tenure_years": 3,
    "artifacts": [
        {"id": "a1", "type": "pr", "text": "Built a RAG agent with LangGraph", "date": "2026-06-01"},
        {"id": "a2", "type": "commit", "text": "python pandas refactor", "date": "2026-05-01"},
    ],
    "self_reported_skills": ["Python"],
    "protected": {"gender": "F", "age_band": "50+", "ethnicity": "Hispanic"},
}

def test_extract_links_evidence_to_skills():
    refs = si.extract_and_classify(WORKER["artifacts"], ONT)
    assert "llm" in refs and refs["llm"][0].artifact_id == "a1"
    assert "py" in refs

def test_build_profile_scores_and_recency():
    p = si.build_profile(WORKER, ONT, today=date(2026, 6, 11))
    llm = p.get("llm")
    assert llm is not None
    assert 0.0 < llm.proficiency <= 1.0
    assert llm.recency_days == 10           # 2026-06-11 minus 2026-06-01
    assert llm.evidence[0].artifact_type == "pr"

def test_proficiency_uses_type_weight():
    # one PR (0.4) should score higher than one commit (0.2)
    refs_pr = si.extract_and_classify([{"id":"x","type":"pr","text":"python","date":"2026-06-01"}], ONT)
    refs_co = si.extract_and_classify([{"id":"y","type":"commit","text":"python","date":"2026-06-01"}], ONT)
    s_pr = si.score_skill("py", refs_pr["py"], ONT, today=date(2026,6,2))
    s_co = si.score_skill("py", refs_co["py"], ONT, today=date(2026,6,2))
    assert s_pr.proficiency > s_co.proficiency
