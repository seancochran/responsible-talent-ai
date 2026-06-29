from pathlib import Path
import json
from src.ontology import Ontology
from src.connectors.eightfold import EightfoldClient
from src.fairness_redteam import make_counterfactual, counterfactual_seat_test

ROOT = Path(__file__).resolve().parents[1]
ONT = Ontology.load(ROOT / "data" / "ontology.json")
SEATS = json.loads((ROOT / "data" / "seats.json").read_text())
WORKERS = json.loads((ROOT / "data" / "workers.json").read_text())
MARIA = next(w for w in WORKERS if w["id"] == "w-maria")  # age_band 50+

def test_make_counterfactual_only_flips_protected():
    twin = make_counterfactual(MARIA, {"age_band": "30-39"})
    assert twin["protected"]["age_band"] == "30-39"
    assert twin["self_reported_skills"] == MARIA["self_reported_skills"]   # qualifications held constant
    assert twin["artifacts"] == MARIA["artifacts"]
    assert MARIA["protected"]["age_band"] == "50+"   # original untouched

def test_counterfactual_detects_treatment_flip():
    ef = EightfoldClient(SEATS, ONT)
    res = counterfactual_seat_test(MARIA, ef, {"age_band": "30-39"})
    # flipping age off the biased band re-surfaces a stretch seat -> treatment flag
    assert res.treatment_flag is True
    assert set(res.twin_stretch_seats) != set(res.original_stretch_seats)
