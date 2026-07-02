from src.models import Match
from src.narrative import explain_match

def test_explanation_is_deterministic_without_key(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    m = Match("s-llm-lead", "LLM Platform Lead (stretch)", 0.82,
              ["LLM Engineering", "Python"], ["Technical Leadership"], [], 0.4)
    text = explain_match(m, "Maria Alvarez")
    assert "LLM Platform Lead" in text
    assert "Technical Leadership" in text      # names the gap
    assert isinstance(text, str) and len(text) > 0
