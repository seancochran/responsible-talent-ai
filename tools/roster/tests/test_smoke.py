import importlib

def test_core_modules_import():
    for m in ["src.models", "src.ontology", "src.skills_intelligence", "src.matching",
              "src.fairness_redteam", "src.governance", "src.graph", "src.narrative",
              "src.connectors.workday", "src.connectors.eightfold"]:
        importlib.import_module(m)
