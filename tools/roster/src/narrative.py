from __future__ import annotations
from .models import Match
from . import llm

def _deterministic(match: Match, worker_name: str) -> str:
    matched = ", ".join(match.matched) or "no evidenced skills"
    gaps = ", ".join(match.gaps) or "none"
    return (f"{worker_name} fits {match.title} at {match.score:.0%} "
            f"(evidence: {matched}; gaps: {gaps}).")

def explain_match(match: Match, worker_name: str) -> str:
    base = _deterministic(match, worker_name)
    if not llm.is_configured():
        return base
    try:
        polished = llm.complete(
            system="Rewrite the talent-match explanation in one crisp, neutral sentence. "
                   "Keep every skill name. No new claims.",
            prompt=base, max_tokens=120, temperature=0.2)
        return polished or base
    except Exception:
        return base
