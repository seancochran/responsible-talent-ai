from __future__ import annotations
import json, re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class OntologySkill:
    skill_id: str
    name: str
    aliases: tuple[str, ...]

class Ontology:
    def __init__(self, skills: list[OntologySkill]):
        self._skills = skills
        self._by_id = {s.skill_id: s for s in skills}

    @classmethod
    def load(cls, path) -> "Ontology":
        raw = json.loads(Path(path).read_text())
        return cls([OntologySkill(s["skill_id"], s["name"], tuple(s["aliases"])) for s in raw])

    def name(self, skill_id: str) -> str:
        return self._by_id[skill_id].name

    def match_text(self, text: str) -> set[str]:
        low = text.lower()
        hits = set()
        for s in self._skills:
            for term in (s.name, *s.aliases):
                if re.search(rf"\b{re.escape(term.lower())}\b", low):
                    hits.add(s.skill_id)
                    break
        return hits

    def id_for_name(self, name: str) -> str | None:
        low = name.strip().lower()
        for s in self._skills:
            if s.name.lower() == low or low in (a.lower() for a in s.aliases):
                return s.skill_id
        return None
