"""LangGraph StateGraph wiring the deterministic Roster core into one pipeline.
The shared state IS the accumulating decision record."""
from __future__ import annotations
from datetime import date
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from . import skills_intelligence as si
from .matching import rank_seats
from .fairness_redteam import counterfactual_seat_test, aggregate_impact
from .governance import build_record

class RosterState(TypedDict, total=False):
    worker_id: str
    worker: dict
    today: object
    flips: dict
    profile: object
    reconciliation: object
    recommendation: list
    counterfactual: object
    impact: object
    record: object
    _ctx: dict   # carries non-serialized clients/ontology/seats/workers

def _profile_node(state: RosterState) -> dict:
    ctx = state["_ctx"]
    w = state["worker"]
    profile = si.build_profile(w, ctx["ontology"], state["today"])
    rec = si.reconcile(profile, w["self_reported_skills"], ctx["ontology"])
    return {"profile": profile, "reconciliation": rec}

def _match_node(state: RosterState) -> dict:
    ctx = state["_ctx"]
    baseline = {s["seat_id"]: s["fit_score"] for s in ctx["eightfold"].score(state["worker"])}
    return {"recommendation": rank_seats(state["profile"], ctx["seats"], ctx["ontology"], baseline)}

def _fairness_node(state: RosterState) -> dict:
    ctx = state["_ctx"]
    cf = counterfactual_seat_test(state["worker"], ctx["eightfold"], state["flips"])
    imp = aggregate_impact(ctx["workers"], ctx["eightfold"], next(iter(state["flips"])))
    return {"counterfactual": cf, "impact": imp}

def _govern_node(state: RosterState) -> dict:
    return {"record": build_record(state["worker_id"], state["recommendation"],
                                   state["reconciliation"], state["counterfactual"], state["impact"])}

def _build_graph():
    g = StateGraph(RosterState)
    g.add_node("profile", _profile_node)
    g.add_node("match", _match_node)
    g.add_node("fairness", _fairness_node)
    g.add_node("govern", _govern_node)
    g.add_edge(START, "profile")
    g.add_edge("profile", "match")
    g.add_edge("match", "fairness")
    g.add_edge("fairness", "govern")
    g.add_edge("govern", END)
    return g.compile()

_GRAPH = _build_graph()

def run_pipeline(worker_id, workday, eightfold, ontology, today: date, flips: dict | None = None):
    worker = workday.get_worker(worker_id)
    ctx = {"ontology": ontology, "eightfold": eightfold, "seats": workday.list_open_seats(),
           "workers": workday.list_workers()}
    state = _GRAPH.invoke({"worker_id": worker_id, "worker": worker, "today": today,
                           "flips": flips or {"age_band": "30-39"}, "_ctx": ctx})
    return state["record"]
