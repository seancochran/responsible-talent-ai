from pathlib import Path
from src.connectors.workday import WorkdayClient

DATA = Path(__file__).resolve().parents[1] / "data"

def test_workday_reads_fixtures():
    wd = WorkdayClient(DATA)
    assert any(w["id"] == "w-maria" for w in wd.list_workers())
    assert wd.get_worker("w-maria")["current_role"] == "Data Engineer"
    assert any(s["stretch"] for s in wd.list_open_seats())

def test_write_decision_record_returns_id():
    wd = WorkdayClient(DATA)
    rid = wd.write_decision_record({"worker_id": "w-maria"})
    assert isinstance(rid, str) and rid.startswith("REC-")
