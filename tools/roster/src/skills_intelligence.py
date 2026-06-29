from __future__ import annotations
from datetime import date
from .models import EvidenceRef, SkillScore, EvidenceProfile, Reconciliation
from .ontology import Ontology

TYPE_WEIGHTS = {"pr": 0.4, "doc": 0.25, "commit": 0.2, "ticket": 0.15}

def extract_and_classify(artifacts: list[dict], ontology: Ontology) -> dict[str, list[EvidenceRef]]:
    out: dict[str, list[EvidenceRef]] = {}
    for art in artifacts:
        for sid in ontology.match_text(art["text"]):
            out.setdefault(sid, []).append(
                EvidenceRef(artifact_id=art["id"], artifact_type=art["type"],
                            snippet=art["text"][:120]))
    return out

def score_skill(skill_id: str, refs: list[EvidenceRef], ontology: Ontology, today: date) -> SkillScore:
    proficiency = min(1.0, round(sum(TYPE_WEIGHTS.get(r.artifact_type, 0.1) for r in refs), 4))
    # recency_days computed by build_profile (needs artifact dates); default 0 here
    return SkillScore(skill_id=skill_id, name=ontology.name(skill_id),
                      proficiency=proficiency, recency_days=0, evidence=list(refs),
                      source="evidence")

def build_profile(worker: dict, ontology: Ontology, today: date) -> EvidenceProfile:
    by_skill = extract_and_classify(worker["artifacts"], ontology)
    date_by_art = {a["id"]: date.fromisoformat(a["date"]) for a in worker["artifacts"]}
    skills: list[SkillScore] = []
    for sid, refs in by_skill.items():
        s = score_skill(sid, refs, ontology, today)
        recents = [date_by_art[r.artifact_id] for r in refs]
        s.recency_days = (today - max(recents)).days
        skills.append(s)
    skills.sort(key=lambda s: (-s.proficiency, s.recency_days))
    return EvidenceProfile(worker_id=worker["id"], skills=skills)

def reconcile(profile, self_reported_names: list[str], ontology: Ontology) -> Reconciliation:
    claimed_ids = {ontology.id_for_name(n) for n in self_reported_names}
    claimed_ids.discard(None)
    evidenced_ids = profile.skill_ids()
    gaps = sorted(ontology.name(i) for i in claimed_ids - evidenced_ids)
    hidden = sorted(ontology.name(i) for i in evidenced_ids - claimed_ids)
    return Reconciliation(gaps=gaps, hidden_strengths=hidden)
