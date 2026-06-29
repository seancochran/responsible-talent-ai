from __future__ import annotations
from .models import Match
from .ontology import Ontology

def rank_seats(profile, seats: list[dict], ontology: Ontology,
               baseline: dict | None = None) -> list[Match]:
    have = profile.skill_ids()
    out: list[Match] = []
    for seat in seats:
        req = list(seat["required_skills"])
        present = [sid for sid in req if sid in have]
        missing = [sid for sid in req if sid not in have]
        coverage = (sum(profile.get(sid).proficiency for sid in present) / len(req)) if req else 0.0
        bfit = None if baseline is None else float(baseline.get(seat["id"], 0.0))
        score = coverage if bfit is None else (0.6 * coverage + 0.4 * bfit)
        evidence = [ref for sid in present for ref in profile.get(sid).evidence]
        out.append(Match(
            seat_id=seat["id"], title=seat["title"], score=round(float(score), 4),
            matched=[ontology.name(sid) for sid in present],
            gaps=[ontology.name(sid) for sid in missing],
            evidence=evidence[:5], baseline_fit=bfit))
    out.sort(key=lambda m: m.score, reverse=True)
    return out
