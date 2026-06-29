"""Mock WorkdayClient. Method shapes mirror Workday Web Services / RaaS.
Swap the JSON reads for real Get_Workers / Get_Job_Requisitions calls to go live."""
from __future__ import annotations
import json
from pathlib import Path

class WorkdayClient:
    def __init__(self, data_dir):
        self._dir = Path(data_dir)

    def _load(self, name):
        return json.loads((self._dir / name).read_text())

    def list_workers(self) -> list[dict]:           # ~ Get_Workers
        return self._load("workers.json")

    def get_worker(self, worker_id: str) -> dict:
        return next(w for w in self.list_workers() if w["id"] == worker_id)

    def list_open_seats(self) -> list[dict]:        # ~ Get_Job_Requisitions (+ gigs)
        return self._load("seats.json")

    def get_outcomes(self) -> list[dict]:           # ~ RaaS report rows
        return self._load("outcomes_history.json")

    def write_decision_record(self, record_dict: dict) -> str:  # ~ Put_* (mock no-op)
        return f"REC-{abs(hash(record_dict.get('worker_id', ''))) % 100000:05d}"
