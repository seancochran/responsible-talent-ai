from datetime import date
from pathlib import Path
import json
from src.ontology import Ontology
import src.skills_intelligence as si
from src.matching import rank_seats

ROOT = Path(__file__).resolve().parents[1]
ONT = Ontology.load(ROOT / "data" / "ontology.json")
SEATS = json.loads((ROOT / "data" / "seats.json").read_text())
WORKERS = json.loads((ROOT / "data" / "workers.json").read_text())
MARIA = next(w for w in WORKERS if w["id"] == "w-maria")

def test_rank_surfaces_evidence_based_match_with_explanation():
    p = si.build_profile(MARIA, ONT, today=date(2026, 6, 11))
    ranked = rank_seats(p, SEATS, ONT)
    top = ranked[0]
    assert top.score >= ranked[-1].score          # sorted desc
    # Maria has evidence of LLM + Python -> the LLM stretch seat should score and explain
    llm_seat = next(m for m in ranked if m.seat_id == "s-llm-lead")
    assert "LLM Engineering" in llm_seat.matched
    assert llm_seat.evidence                       # carries provenance

def test_baseline_blended_when_provided():
    p = si.build_profile(MARIA, ONT, today=date(2026, 6, 11))
    base = {"s-data": 1.0}
    blended = {m.seat_id: m.score for m in rank_seats(p, SEATS, ONT, baseline=base)}
    nobl = {m.seat_id: m.score for m in rank_seats(p, SEATS, ONT)}
    assert blended["s-data"] != nobl["s-data"]
