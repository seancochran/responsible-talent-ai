from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Artifact:
    id: str
    type: str            # commit | pr | doc | ticket
    text: str
    date: str            # ISO YYYY-MM-DD

@dataclass(frozen=True)
class EvidenceRef:
    artifact_id: str
    artifact_type: str
    snippet: str

@dataclass
class SkillScore:
    skill_id: str
    name: str
    proficiency: float       # 0..1
    recency_days: int
    evidence: list[EvidenceRef] = field(default_factory=list)
    source: str = "evidence"  # evidence | self

@dataclass
class EvidenceProfile:
    worker_id: str
    skills: list[SkillScore] = field(default_factory=list)

    def skill_ids(self) -> set[str]:
        return {s.skill_id for s in self.skills}

    def get(self, skill_id: str) -> SkillScore | None:
        return next((s for s in self.skills if s.skill_id == skill_id), None)

@dataclass
class Reconciliation:
    gaps: list[str] = field(default_factory=list)             # claimed, no evidence (names)
    hidden_strengths: list[str] = field(default_factory=list) # evidence, never claimed (names)

@dataclass
class Match:
    seat_id: str
    title: str
    score: float
    matched: list[str]                # skill names present
    gaps: list[str]                   # required skill names missing
    evidence: list[EvidenceRef] = field(default_factory=list)
    baseline_fit: float | None = None

@dataclass
class CounterfactualResult:
    attribute: str
    original_stretch_seats: list[str]
    twin_stretch_seats: list[str]
    treatment_flag: bool

@dataclass
class DecisionRecord:
    worker_id: str
    recommendation: list[Match]
    reconciliation: Reconciliation
    counterfactual: CounterfactualResult
    impact_summary: dict
    dissent: list[str] = field(default_factory=list)
    signoff: dict | None = None
    caveat: str = ("Screening aid — not legal advice and not a compliance "
                   "certification. Flags are triggers for human review.")
