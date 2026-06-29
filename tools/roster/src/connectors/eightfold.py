"""Mock EightfoldClient. Infers skills from CLAIMED (self-reported) data only and
applies a deliberate stretch-role age penalty — the vendor black-box behaviour that
Roster's evidence layer (claims gap) and fairness red-team (treatment) expose."""
from __future__ import annotations
from ..ontology import Ontology

class EightfoldClient:
    def __init__(self, seats: list[dict], ontology: Ontology,
                 stretch_age_penalty: float = 0.5, biased_band: str = "50+"):
        self._seats = seats
        self._ont = ontology
        self._penalty = stretch_age_penalty
        self._biased_band = biased_band

    def _claimed_ids(self, worker: dict) -> set[str]:
        ids = {self._ont.id_for_name(n) for n in worker.get("self_reported_skills", [])}
        ids.discard(None)
        return ids

    def score(self, worker: dict) -> list[dict]:
        claimed = self._claimed_ids(worker)
        band = worker.get("protected", {}).get("age_band")
        out = []
        for seat in self._seats:
            req = set(seat["required_skills"])
            fit = len(req & claimed) / len(req) if req else 0.0
            if seat["stretch"] and band == self._biased_band:
                fit *= self._penalty
            out.append({"seat_id": seat["id"], "fit_score": round(fit, 4)})
        return out

    def get_matching_seats(self, worker_id: str, workers: list[dict]) -> list[dict]:
        w = next(w for w in workers if w["id"] == worker_id)
        return self.score(w)
