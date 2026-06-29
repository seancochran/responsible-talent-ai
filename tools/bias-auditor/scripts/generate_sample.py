"""
Generate a synthetic hiring-funnel CSV with a deliberately embedded disparity,
so the auditor has something clear to flag in a demo. Fully synthetic — no real
people. Deterministic via a fixed seed.

    python scripts/generate_sample.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 600

genders = rng.choice(
    ["Male", "Female", "Non-binary"], size=N, p=[0.52, 0.45, 0.03]
)
races = rng.choice(
    ["White", "Black", "Hispanic", "Asian", "Two or more / Other"],
    size=N, p=[0.50, 0.16, 0.16, 0.13, 0.05],
)
dept = rng.choice(["Engineering", "Content", "Marketing", "Data"], size=N)

# Base hire probability, then nudge DOWN for certain groups to create a
# realistic-looking adverse impact the tool should catch.
base = 0.42
prob = np.full(N, base)
prob = np.where(genders == "Female", prob - 0.13, prob)        # ~0.29
prob = np.where(genders == "Non-binary", prob - 0.10, prob)
prob = np.where(races == "Black", prob - 0.14, prob)           # impact < 0.8
prob = np.where(races == "Hispanic", prob - 0.06, prob)
prob += rng.normal(0, 0.03, size=N)                            # noise
prob = np.clip(prob, 0.03, 0.95)

hired = (rng.random(N) < prob).astype(int)

df = pd.DataFrame(
    {
        "candidate_id": [f"C{1000+i}" for i in range(N)],
        "department": dept,
        "gender": genders,
        "race_ethnicity": races,
        "hired": hired,
    }
)

out = Path(__file__).resolve().parents[1] / "data" / "sample_hiring_funnel.csv"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
print(f"Wrote {len(df)} rows to {out}")
print("Overall hire rate:", round(df['hired'].mean(), 3))
print(df.groupby('gender')['hired'].mean().round(3).to_dict())
print(df.groupby('race_ethnicity')['hired'].mean().round(3).to_dict())
