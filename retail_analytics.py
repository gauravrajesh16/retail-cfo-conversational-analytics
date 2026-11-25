from pathlib import Path
from io import BytesIO
import re,json
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def load_data(p):
    return tuple(pd.read_csv(p/n) for n in ["sales.csv","plan.csv","costs.csv","stores.csv","inventory.csv"])

def classify_question(q):
    x=q.lower()
    if any(k in x for k in ["what if","scenario","price increase","raise prices","increase price"]):
        m=re.search(r"(\d+(?:\.\d+)?)\s*%",x); return "scenario",{"price_increase_pct":float(m.group(1)) if m else 5.0}
    if any(k in x for k in ["store","margin","profitability","gross profit"]):
        m=re.search(r"store\s+([a-z0-9]+)",x); return "profitability",{"store":"Store "+m.group(1).upper() if m else "Store A"}
    if any(k in x for k in ["cost","saving","expense","reduce"]): return "cost",{}
    if any(k in x for k in ["revenue","sales","plan","growth","variance"]): return "revenue",{}
    return "clarify",{}

def query_metric(sales,plan):
    a=float(sales.net_revenue.sum()); p=float(plan.planned_revenue.sum()); v=a-p
    return {"actual":a,"plan":p,"variance":v,"variance_pct":v/p*100 if p else 0}

def explain_variance(sales,plan):
    a=sales.groupby("region",as_index=False).net_revenue.sum()
    p=plan.groupby("region",as_index=False).planned_revenue.sum()
    d=a.merge(p,on="region"); d["variance"]=d.net_revenue-d.planned_revenue
    d["variance_pct"]=d.variance/d.planned_revenue*100
    d=d.rename(columns={"net_revenue":"actual_revenue","planned_revenue":"plan_revenue"}).sort_values("variance")
    total=d.variance.sum()
    msg=f"Revenue is ${abs(total):,.0f} {'below' if total<0 else 'above'} plan ({total/d.plan_revenue.sum()*100:+.1f}%). {d.iloc[0].region} is the largest negative contributor at ${d.iloc[0].variance:,.0f}. Regional contributors reconcile to the total."
    return {"contributors":d,"narrative":msg}

def _joined(costs,stores):
    return costs.merge(stores[["store","peer_group","region","size_sqft"]],on="store")

def store_margin_bridge(costs,stores,name="Store A"):
    d=_joined(costs,stores); r=d[d.store==name].iloc[0]; peers=d[(d.peer_group==r.peer_group)&(d.store!=name)]
    gm=(r.net_revenue-r.cogs)/r.net_revenue*100
    pgm=((peers.net_revenue-peers.cogs)/peers.net_revenue*100).mean()
    rows=[]
    for col in ["labor","rent","utilities","shrink","logistics"]:
        avg=peers[col].mean(); rows.append({"cost_line":col.title(),"store_cost":r[col],"peer_average":avg,"gap_vs_peer":r[col]-avg})
    b=pd.DataFrame(rows).sort_values("gap_vs_peer",ascending=False)
    return {"gross_margin_pct":gm,"gap_bps":(gm-pgm)*100,"bridge":b,
            "narrative":f"{name} gross margin is {gm:.1f}% versus peer average {pgm:.1f}% ({(gm-pgm)*100:+.0f} bps). Investigate cost gaps before treating them as controllable savings."}

def peer_benchmark(costs,stores,name="Store A"):
    d=_joined(costs,stores); r=d[d.store==name].iloc[0]; peers=d[(d.peer_group==r.peer_group)&(d.store!=name)]
    return pd.DataFrame([{"cost_line":c.title(),"store_value":r[c],"peer_average":peers[c].mean(),"difference":r[c]-peers[c].mean()} for c in ["labor","rent","utilities","shrink","logistics"]])

def detect_anomalies(costs,stores):
    d=_joined(costs,stores); rows=[]
    for _,r in d.iterrows():
        p=d[(d.peer_group==r.peer_group)&(d.store!=r.store)]
        for c in ["labor","rent","utilities","shrink","logistics"]:
            gap=r[c]-p[c].mean()
            if gap>0: rows.append({"store":r.store,"cost_line":c.title(),"store_cost":r[c],"peer_average":p[c].mean(),"monthly_gap":gap,"annualized_opportunity":gap*12})
    return pd.DataFrame(rows).sort_values("annualized_opportunity",ascending=False).head(20)

def simulate_scenario(sales,pct=5):
    d=sales[sales.margin_class=="High"]; rev=d.net_revenue.sum(); cogs=d.cogs.sum(); rows=[]
    for label,e in [("Low response",-0.3),("Base response",-0.6),("High response",-0.9)]:
        vf=1+e*pct/100; sr=rev*(1+pct/100)*vf; sc=cogs*vf; gp=sr-sc
        rows.append({"elasticity_case":label,"elasticity":e,"volume_change_pct":(vf-1)*100,"revenue_change":sr-rev,"scenario_revenue":sr,"scenario_gross_profit":gp,"gross_profit_change":gp-(rev-cogs)})
    df=pd.DataFrame(rows); b=df.iloc[1]
    return {"base_revenue":rev,"scenario_revenue":b.scenario_revenue,"revenue_change":b.revenue_change,"gross_profit_change":b.gross_profit_change,"sensitivity":df,
            "narrative":f"A {pct:.1f}% price increase with base elasticity -0.6 implies volume change {b.volume_change_pct:.1f}% and revenue change ${b.revenue_change:,.0f}. Excludes substitution, promotions, competitor response and fixed-cost effects."}

def build_evidence(q,intent,params,result):
    tools={"revenue":["query_metric","explain_variance"],"profitability":["store_margin_bridge","peer_benchmark"],"scenario":["simulate_scenario"],"cost":["detect_anomalies"]}
    return {"question":q,"workflow":intent,"tool_calls":tools.get(intent,[]),"parameters":params,"data_as_of":"2026-10-31","data_source":"Seeded synthetic CSV data","metric_definitions":{"net_revenue":"Synthetic net sales after discounts and returns","gross_margin":"(Net revenue - COGS) / Net revenue","peer_gap":"Store cost less peer-group mean"},"verification":{"calculations_deterministic":True,"revenue_contributors_reconcile":True if intent=="revenue" else None,"general_ledger_reconciliation":"Not applicable: synthetic data"},"limitations":["Synthetic data only","Peer gaps are leads, not approved savings","Elasticity is assumed, not forecast"]}

def export_pdf(q,result,evidence):
    b=BytesIO(); styles=getSampleStyleSheet(); story=[Paragraph("Retail CFO — Conversational Analytics",styles["Title"]),Paragraph(result["title"],styles["Heading2"]),Paragraph(q,styles["Italic"]),Spacer(1,10),Paragraph(result["summary"],styles["BodyText"]),Spacer(1,10)]
    for name,df in result["tables"].items():
        story.append(Paragraph(name,styles["Heading3"]))
        if len(df):
            vals=[list(df.columns)]+df.head(15).astype(str).values.tolist(); t=Table(vals,repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17384D")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.3,colors.grey),("FONTSIZE",(0,0),(-1,-1),7)])); story.extend([t,Spacer(1,8)])
    story.append(Paragraph("Evidence JSON",styles["Heading2"])); story.append(Paragraph(json.dumps(evidence,indent=2).replace("\\n","<br/>"),styles["Code"]))
    doc=SimpleDocTemplate(b,pagesize=letter); doc.build(story); return b.getvalue()
