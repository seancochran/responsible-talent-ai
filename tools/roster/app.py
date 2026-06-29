# tools/roster/app.py
from datetime import date
from pathlib import Path
import streamlit as st

from src.ontology import Ontology
from src.connectors.workday import WorkdayClient
from src.connectors.eightfold import EightfoldClient
from src.graph import run_pipeline
from src.narrative import explain_match
from src.governance import sign_off, record_to_dict
from src import llm

DATA = Path(__file__).resolve().parent / "data"
TODAY = date(2026, 6, 11)

st.set_page_config(page_title="Roster", layout="wide")
wd = WorkdayClient(DATA)
ont = Ontology.load(DATA / "ontology.json")
ef = EightfoldClient(wd.list_open_seats(), ont)

st.title("Roster — right people, right seats, proven")
st.caption(f"Trust layer over Workday + Eightfold (mock). {llm.status()}")

page = st.sidebar.radio("View", ["Decision", "Outcomes dashboard"])
if page == "Decision":
    workers = wd.list_workers()
    wid = st.sidebar.selectbox("Worker", [w["id"] for w in workers],
                               format_func=lambda i: wd.get_worker(i)["name"])
    rec = run_pipeline(wid, wd, ef, ont, today=TODAY)

    st.subheader("Evidence-grounded skills")
    if rec.reconciliation.hidden_strengths:
        st.success("Hidden strengths (evidenced, never self-reported): "
                   + ", ".join(rec.reconciliation.hidden_strengths))
    if rec.reconciliation.gaps:
        st.warning("Claimed but unevidenced: " + ", ".join(rec.reconciliation.gaps))

    st.subheader("Right-seat ranking")
    for m in rec.recommendation:
        st.markdown(f"**{m.title}** — fit {m.score:.0%}")
        st.caption(explain_match(m, wd.get_worker(wid)["name"]))

    st.subheader("Fairness red-team")
    cf = rec.counterfactual
    if cf.treatment_flag:
        st.error(f"⚠ Disparate treatment on `{cf.attribute}`: surfaced stretch seats changed "
                 f"{cf.original_stretch_seats} → {cf.twin_stretch_seats} when only the protected "
                 f"attribute was flipped.")
    else:
        st.success("No treatment flip detected on the tested attribute.")
    st.write("Aggregate impact (four-fifths on stretch-seat surfacing):")
    st.json(rec.impact_summary)

    st.subheader("Governance record")
    for d in rec.dissent:
        st.write("• " + d)
    with st.form("signoff"):
        by = st.text_input("Reviewer", "Hiring Manager")
        decision = st.selectbox("Decision", ["approved", "approved_with_review", "rejected"])
        if st.form_submit_button("Sign off"):
            rec = sign_off(rec, by, decision)
            st.success(f"Signed off by {by}: {decision}")
    st.download_button("Download audit record (JSON)",
                       data=__import__("json").dumps(record_to_dict(rec), indent=2),
                       file_name=f"roster_record_{wid}.json")
    st.caption(rec.caveat)
