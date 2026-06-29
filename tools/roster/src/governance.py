from __future__ import annotations
from dataclasses import asdict
from .models import DecisionRecord

def build_record(worker_id, recommendation, reconciliation, counterfactual, impact) -> DecisionRecord:
    dissent: list[str] = []
    if counterfactual.treatment_flag:
        dissent.append(f"Disparate treatment: flipping {counterfactual.attribute} changed surfaced "
                       f"stretch seats {counterfactual.original_stretch_seats} -> "
                       f"{counterfactual.twin_stretch_seats}.")
    if bool(impact.any_flag):
        dissent.append("Disparate impact: a group falls below the four-fifths surfacing threshold.")
    impact_summary = {
        "attribute": impact.attribute, "reference_group": impact.reference_group,
        "any_flag": bool(impact.any_flag), "any_significant_flag": bool(impact.any_significant_flag),
        "groups": [{"group": g.group, "n": int(g.n), "selection_rate": round(float(g.selection_rate), 4),
                    "impact_ratio": round(float(g.impact_ratio), 4),
                    "four_fifths_flag": bool(g.four_fifths_flag)} for g in impact.groups],
    }
    return DecisionRecord(worker_id=worker_id, recommendation=recommendation,
                          reconciliation=reconciliation, counterfactual=counterfactual,
                          impact_summary=impact_summary, dissent=dissent)

def sign_off(record: DecisionRecord, by: str, decision: str) -> DecisionRecord:
    record.signoff = {"by": by, "decision": decision}
    return record

def record_to_dict(record: DecisionRecord) -> dict:
    d = asdict(record)   # dataclasses -> nested dicts/lists of native types
    return d
