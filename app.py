from pathlib import Path
import json
import streamlit as st
import plotly.express as px
from retail_analytics import *

st.set_page_config(page_title="Retail CFO Analytics",page_icon="📊",layout="wide")
st.title("📊 Conversational Analytics for the Retail CFO")
st.caption("FDE prototype | Synthetic data | Deterministic calculations | Evidence-backed answers")
sales,plan,costs,stores,inventory=load_data(Path(__file__).parent/"data")

with st.sidebar:
    st.success("Seeded synthetic dataset")
    st.caption("Data as of 31 Oct 2026 · Demo access: all stores")
    st.subheader("Try a use case")
    examples=["Why is revenue below plan?","Why is Store A's gross margin below target?",
              "What if we increase prices by 5% on high-margin categories?",
              "Where can we reduce costs without hurting revenue?"]
    for q in examples:
        if st.button(q,use_container_width=True): st.session_state.question=q

q=st.text_input("Ask a financial question",key="question",placeholder="e.g. Why is revenue below plan?")
if st.button("Analyze",type="primary",disabled=not q.strip()):
    intent,params=classify_question(q)
    result={"title":"Analysis","summary":"","tables":{}}
    st.divider()
    st.caption(f"Detected workflow: `{intent}` · deterministic router")
    if intent=="revenue":
        m=query_metric(sales,plan); v=explain_variance(sales,plan)
        a,b,c=st.columns(3)
        a.metric("Actual revenue",f"${m['actual']:,.0f}")
        b.metric("Plan revenue",f"${m['plan']:,.0f}")
        c.metric("Variance",f"{m['variance_pct']:+.1f}%",delta=f"${m['variance']:,.0f}")
        st.write(v["narrative"]); st.dataframe(v["contributors"],hide_index=True,use_container_width=True)
        st.plotly_chart(px.bar(v["contributors"],x="region",y="variance",color="variance",title="Revenue variance by region"),use_container_width=True)
        result={"title":"Revenue vs plan","summary":v["narrative"],"tables":{"Regional variance":v["contributors"]}}
    elif intent=="profitability":
        store=params.get("store","Store A"); b=store_margin_bridge(costs,stores,store); p=peer_benchmark(costs,stores,store)
        a,c=st.columns(2); a.metric("Gross margin",f"{b['gross_margin_pct']:.1f}%"); c.metric("Gap vs peer",f"{b['gap_bps']:+.0f} bps")
        st.write(b["narrative"]); st.dataframe(b["bridge"],hide_index=True,use_container_width=True)
        st.subheader("Peer benchmark"); st.dataframe(p,hide_index=True,use_container_width=True)
        st.plotly_chart(px.bar(b["bridge"],x="cost_line",y="gap_vs_peer",color="gap_vs_peer",title="Store cost gap vs peer average"),use_container_width=True)
        result={"title":f"{store} profitability bridge","summary":b["narrative"],"tables":{"Margin bridge":b["bridge"],"Peer benchmark":p}}
    elif intent=="scenario":
        s=simulate_scenario(sales,params.get("price_increase_pct",5))
        a,b,c=st.columns(3); a.metric("Baseline revenue",f"${s['base_revenue']:,.0f}"); b.metric("Scenario revenue",f"${s['scenario_revenue']:,.0f}",delta=f"${s['revenue_change']:,.0f}"); c.metric("Gross profit change",f"${s['gross_profit_change']:,.0f}")
        st.write(s["narrative"]); st.warning("Illustrative elasticity assumptions, not a forecast.")
        st.dataframe(s["sensitivity"],hide_index=True,use_container_width=True)
        st.plotly_chart(px.bar(s["sensitivity"],x="elasticity_case",y="revenue_change",title="Revenue sensitivity"),use_container_width=True)
        result={"title":"Price scenario","summary":s["narrative"],"tables":{"Sensitivity":s["sensitivity"]}}
    elif intent=="cost":
        a=detect_anomalies(costs,stores); total=a.annualized_opportunity.sum() if len(a) else 0
        st.write("Peer gaps are investigation leads, not approved savings.")
        st.metric("Indicative annualized opportunity",f"${total:,.0f}")
        st.dataframe(a,hide_index=True,use_container_width=True)
        result={"title":"Cost opportunities","summary":f"Indicative opportunity ${total:,.0f}; validate before booking savings.","tables":{"Opportunities":a}}
    else:
        st.warning("Please specify revenue vs plan, a store margin issue, a price scenario, or cost opportunities.")
        result={"title":"Clarification required","summary":"Please clarify the supported financial question.","tables":{}}
    evidence=build_evidence(q,intent,params,result)
    with st.expander("Evidence, assumptions & lineage",expanded=True): st.json(evidence)
    st.download_button("Download PDF analysis",export_pdf(q,result,evidence),"retail_cfo_analysis.pdf","application/pdf")
    st.download_button("Download evidence JSON",json.dumps(evidence,indent=2),"retail_cfo_evidence.json","application/json")

st.divider()
st.subheader("Prototype boundaries")
st.markdown("- Synthetic data only; not connected to ERP, warehouse or general ledger.\\n- Rule-based router is a reproducible stand-in for future LLM typed-tool orchestration.\\n- Scenario elasticity is assumed, not learned.\\n- Peer cost gaps are not validated savings.\\n- No write-back or autonomous action.")
