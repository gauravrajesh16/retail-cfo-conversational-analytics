from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from retail_analytics import *
def data(): return load_data(Path(__file__).resolve().parents[1]/"data")
def test_variance_reconciles():
    s,p,*_=data(); m=query_metric(s,p); v=explain_variance(s,p)
    assert abs(v["contributors"].variance.sum()-m["variance"])<0.01
def test_router():
    assert classify_question("Why is revenue below plan?")[0]=="revenue"
    assert classify_question("Why is Store A margin low?")[0]=="profitability"
    assert classify_question("What if price rises 5%?")[0]=="scenario"
    assert classify_question("Where can we reduce costs?")[0]=="cost"
def test_scenario():
    s,*_=data(); r=simulate_scenario(s,5)
    assert len(r["sensitivity"])==3 and r["scenario_revenue"]>0
