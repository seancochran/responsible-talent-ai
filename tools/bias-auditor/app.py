"""
Talent Bias & Adverse-Impact Auditor — Streamlit app.

Run:
    pip install -r requirements.txt
    streamlit run app.py

Upload a hiring/promotion CSV (one row per candidate), pick the protected
attribute column(s) and a binary outcome column, and get a four-fifths-rule
adverse-impact analysis with an optional LLM-generated audit narrative.
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import streamlit as st

from src import llm
from src.adverse_impact import analyze, coerce_outcome
from src.narrative import deterministic_summary, llm_narrative

st.set_page_config(page_title="Talent Bias & Adverse-Impact Auditor",
                   page_icon="\u2696\ufe0f", layout="wide")

SAMPLE = Path(__file__).parent / "data" / "sample_hiring_funnel.csv"


def likely_binary(series: pd.Series) -> bool:
    vals = set(str(v).strip().lower() for v in series.dropna().unique())
    return 0 < len(vals) <= 3


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("About")
    st.write(
        "A screening aid that flags potential **adverse impact** in hiring or "
        "promotion data using the EEOC **four-fifths (80%) rule** plus a "
        "two-proportion significance test."
    )
    st.info(llm.status())
    st.caption(
        "Not legal advice and not a compliance certification. A flag is a "
        "trigger for review, not a finding of discrimination."
    )

# ---------------------------------------------------------------- header
st.title("\u2696\ufe0f Talent Bias & Adverse-Impact Auditor")
st.write(
    "Built for Talent/People teams shipping AI in hiring. Upload candidate-level "
    "data, choose protected attributes and an outcome, and surface where "
    "selection rates diverge — before a regulator or plaintiff does."
)

# ---------------------------------------------------------------- data load
col_a, col_b = st.columns([3, 1])
with col_a:
    upload = st.file_uploader("Upload a CSV (one row per candidate)", type=["csv"])
with col_b:
    use_sample = st.button("Use sample data", use_container_width=True)

df: pd.DataFrame | None = None
if upload is not None:
    df = pd.read_csv(upload)
elif use_sample and SAMPLE.exists():
    df = pd.read_csv(SAMPLE)
elif "df" in st.session_state:
    df = st.session_state["df"]

if df is not None:
    st.session_state["df"] = df

if df is None:
    st.warning("Upload a CSV or click **Use sample data** to begin.")
    st.stop()

st.subheader("Data preview")
st.dataframe(df.head(20), use_container_width=True)
st.caption(f"{len(df):,} rows \u00d7 {df.shape[1]} columns")

# ---------------------------------------------------------------- column picks
cols = list(df.columns)
binary_cols = [c for c in cols if likely_binary(df[c])]

st.subheader("Configure analysis")
c1, c2 = st.columns(2)
with c1:
    outcome_col = st.selectbox(
        "Outcome column (the selection decision, e.g. hired / advanced)",
        options=cols,
        index=(cols.index(binary_cols[0]) if binary_cols else 0),
    )
with c2:
    default_attrs = [c for c in cols
                     if c != outcome_col
                     and any(k in c.lower()
                             for k in ("gender", "sex", "race", "ethnic", "age"))]
    attributes = st.multiselect(
        "Protected attribute column(s)",
        options=[c for c in cols if c != outcome_col],
        default=default_attrs,
    )

with st.expander("Outcome column sanity check"):
    preview = pd.DataFrame({
        "raw": df[outcome_col],
        "coerced (1 = selected)": coerce_outcome(df[outcome_col]),
    }).head(10)
    st.dataframe(preview, use_container_width=True)
    rate = coerce_outcome(df[outcome_col]).mean()
    st.caption(f"Overall selection rate: {rate*100:.1f}%")

run = st.button("Run adverse-impact analysis", type="primary",
                disabled=not attributes)

# ---------------------------------------------------------------- analysis
if run:
    results = analyze(df, attributes, outcome_col)
    st.session_state["results"] = results

results = st.session_state.get("results")
if results:
    any_flag = any(r.any_flag for r in results)
    if any_flag:
        st.error("\u26a0\ufe0f Potential adverse impact detected — review below.")
    else:
        st.success("\u2705 No attribute fell below the 0.80 four-fifths threshold.")

    for r in results:
        st.markdown(f"### {r.attribute}")
        frame = r.to_frame()
        st.dataframe(frame, use_container_width=True, hide_index=True)

        chart_df = pd.DataFrame(
            {g.group: g.selection_rate for g in r.groups}, index=["selection rate"]
        ).T
        st.bar_chart(chart_df)

        ref = next((g for g in r.groups if g.is_reference), None)
        if ref:
            st.caption(
                f"Reference group **{ref.group}** = {ref.selection_rate*100:.1f}%. "
                f"Four-fifths threshold = {ref.selection_rate*0.8*100:.1f}% "
                "(groups below this are flagged)."
            )

    st.divider()
    st.subheader("Audit summary")
    summary_md = deterministic_summary(results)
    st.markdown(summary_md)

    narrative_md = None
    if llm.is_configured():
        if st.button("Generate stakeholder narrative (LLM)"):
            with st.spinner("Generating narrative..."):
                try:
                    narrative_md = llm_narrative(results)
                    st.session_state["narrative"] = narrative_md
                except Exception as e:  # noqa: BLE001
                    st.warning(f"LLM call failed: {e}")
        narrative_md = st.session_state.get("narrative")
        if narrative_md:
            st.markdown("#### Stakeholder narrative")
            st.markdown(narrative_md)
    else:
        st.caption("Set an LLM provider (see sidebar) to also generate a "
                   "plain-English stakeholder narrative.")

    # ----- downloadable report
    report = "# Adverse-Impact Audit Report\n\n" + summary_md
    if narrative_md:
        report += "\n\n## Stakeholder narrative\n\n" + narrative_md
    st.download_button(
        "Download report (Markdown)",
        data=report.encode("utf-8"),
        file_name="adverse_impact_report.md",
        mime="text/markdown",
    )
