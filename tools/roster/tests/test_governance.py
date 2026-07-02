import json
from pathlib import Path
from src.ontology import Ontology
from src.connectors.eightfold import EightfoldClient
from src.fairness_redteam import counterfactual_seat_test, aggregate_impact
from src.models import Match, Reconciliation
from src.governance import build_record, sign_off, record_to_dict

ROOT = Path(__file__).resolve().parents[1]
ONT = Ontology.load(ROOT / "data" / "ontology.json")
SEATS = json.loads((ROOT / "data" / "seats.json").read_text())
WORKERS = json.loads((ROOT / "data" / "workers.json").read_text())
MARIA = next(w for w in WORKERS if w["id"] == "w-maria")

def _record():
    ef = EightfoldClient(SEATS, ONT)
    cf = counterfactual_seat_test(MARIA, ef, {"age_band": "30-39"})
    imp = aggregate_impact(WORKERS, ef, "age_band")
    rec = build_record("w-maria",
                       [Match("s-data", "Senior Data Engineer", 0.8, ["Python"], [], [], None)],
                       Reconciliation(gaps=[], hidden_strengths=["LLM Engineering"]),
                       cf, imp)
    return rec

def test_treatment_flag_records_dissent():
    rec = _record()
    assert any("treatment" in d.lower() for d in rec.dissent)

def test_signoff_and_serialization():
    rec = sign_off(_record(), by="Hiring Manager", decision="approved_with_review")
    d = record_to_dict(rec)
    assert d["signoff"]["by"] == "Hiring Manager"
    json.dumps(d)   # must not raise (native types only)
