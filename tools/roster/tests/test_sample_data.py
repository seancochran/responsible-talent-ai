import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def _gen():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_sample.py")], check=True)

def test_generates_all_fixtures():
    _gen()
    for name in ("ontology.json", "workers.json", "seats.json", "outcomes_history.json"):
        assert (DATA / name).exists(), f"missing {name}"

def test_dataset_is_coherent():
    _gen()
    ont = json.loads((DATA / "ontology.json").read_text())
    seats = json.loads((DATA / "seats.json").read_text())
    workers = json.loads((DATA / "workers.json").read_text())
    skill_ids = {s["skill_id"] for s in ont}
    # every required skill exists in the ontology
    for seat in seats:
        for sid in seat["required_skills"]:
            assert sid in skill_ids, f"{seat['id']} requires unknown {sid}"
    # at least one stretch seat and one worker in the 50+ band (to exercise bias)
    assert any(s["stretch"] for s in seats)
    assert any(w["protected"]["age_band"] == "50+" for w in workers)
    # deterministic: regenerating yields identical bytes
    first = (DATA / "workers.json").read_bytes(); _gen()
    assert (DATA / "workers.json").read_bytes() == first
