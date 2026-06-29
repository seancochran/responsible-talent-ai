from pathlib import Path
from src.ontology import Ontology

ONT = Path(__file__).resolve().parents[1] / "data" / "ontology.json"

def test_match_text_finds_aliases():
    o = Ontology.load(ONT)
    ids = o.match_text("Built a RAG agent with LangGraph and pandas")
    assert "llm" in ids        # rag/agent/langgraph
    assert "py" in ids         # pandas
    assert "cloud" not in ids

def test_name_and_id_for_name():
    o = Ontology.load(ONT)
    assert o.name("py") == "Python"
    assert o.id_for_name("Python") == "py"
    assert o.id_for_name("python") == "py"   # alias, case-insensitive
    assert o.id_for_name("Underwater Basket Weaving") is None
