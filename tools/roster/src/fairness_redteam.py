from __future__ import annotations
import pandas as pd
from . import adverse_impact

def _stretch_seat_ids(eightfold) -> set[str]:
    return {s["id"] for s in eightfold._seats if s["stretch"]}

def surfaced_table(workers: list[dict], eightfold, threshold: float = 0.5) -> pd.DataFrame:
    stretch = _stretch_seat_ids(eightfold)
    rows = []
    for w in workers:
        scores = {s["seat_id"]: s["fit_score"] for s in eightfold.score(w)}
        surfaced = any(scores.get(sid, 0.0) >= threshold for sid in stretch)
        p = w["protected"]
        rows.append({"worker_id": w["id"], "gender": p["gender"], "age_band": p["age_band"],
                     "ethnicity": p["ethnicity"], "surfaced_stretch": int(surfaced)})
    return pd.DataFrame(rows)

def aggregate_impact(workers: list[dict], eightfold, attribute: str = "age_band",
                     threshold: float = 0.5):
    df = surfaced_table(workers, eightfold, threshold)
    return adverse_impact.analyze_attribute(df, attribute, "surfaced_stretch")
