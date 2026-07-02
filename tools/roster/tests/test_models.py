from src.models import SkillScore, EvidenceProfile, EvidenceRef

def test_profile_lookup_and_ids():
    s = SkillScore(skill_id="py", name="Python", proficiency=0.6, recency_days=10,
                   evidence=[EvidenceRef("a1", "pr", "python pandas")], source="evidence")
    p = EvidenceProfile(worker_id="w1", skills=[s])
    assert p.skill_ids() == {"py"}
    assert p.get("py").proficiency == 0.6
    assert p.get("missing") is None
