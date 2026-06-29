from pathlib import Path
from src.ontology import Ontology
from src.connectors.eightfold import EightfoldClient

ROOT = Path(__file__).resolve().parents[1]
ONT = Ontology.load(ROOT / "data" / "ontology.json")
import json
SEATS = json.loads((ROOT / "data" / "seats.json").read_text())

def _worker(band):
    return {"id": "w", "name": "X", "self_reported_skills": ["LLM Engineering", "Technical Leadership", "Python"],
            "protected": {"age_band": band}}

def test_eightfold_penalizes_stretch_for_biased_band():
    ef = EightfoldClient(SEATS, ONT)
    young = {s["seat_id"]: s["fit_score"] for s in ef.score(_worker("30-39"))}
    older = {s["seat_id"]: s["fit_score"] for s in ef.score(_worker("50+"))}
    # identical claimed skills; only the protected band differs
    assert young["s-llm-lead"] > older["s-llm-lead"]      # stretch seat penalized
    assert young["s-data"] == older["s-data"]             # non-stretch seat unaffected
