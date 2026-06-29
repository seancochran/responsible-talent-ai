from pathlib import Path
import json
from src.ontology import Ontology
from src.connectors.eightfold import EightfoldClient
from src.fairness_redteam import surfaced_table, aggregate_impact

ROOT = Path(__file__).resolve().parents[1]
ONT = Ontology.load(ROOT / "data" / "ontology.json")
SEATS = json.loads((ROOT / "data" / "seats.json").read_text())
WORKERS = json.loads((ROOT / "data" / "workers.json").read_text())

def test_surfaced_table_has_one_row_per_worker():
    ef = EightfoldClient(SEATS, ONT)
    df = surfaced_table(WORKERS, ef)
    assert len(df) == len(WORKERS)
    assert set(["age_band", "surfaced_stretch"]).issubset(df.columns)

def test_aggregate_impact_runs_four_fifths():
    ef = EightfoldClient(SEATS, ONT)
    res = aggregate_impact(WORKERS, ef, attribute="age_band")
    # AttributeResult exposes groups + any_flag (native bool)
    assert isinstance(res.any_flag, bool)
    assert any(g.group == "50+" for g in res.groups)
