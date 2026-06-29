from datetime import date
from pathlib import Path
from src.ontology import Ontology
from src.connectors.workday import WorkdayClient
from src.connectors.eightfold import EightfoldClient
from src.graph import run_pipeline
from src.models import DecisionRecord

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ONT = Ontology.load(DATA / "ontology.json")

def test_pipeline_end_to_end_produces_record():
    wd = WorkdayClient(DATA)
    ef = EightfoldClient(wd.list_open_seats(), ONT)
    rec = run_pipeline("w-maria", wd, ef, ONT, today=date(2026, 6, 11))
    assert isinstance(rec, DecisionRecord)
    assert rec.recommendation                      # ranked seats present
    assert rec.reconciliation.hidden_strengths     # Maria's hidden LLM strength surfaced
    assert rec.counterfactual.treatment_flag is True
