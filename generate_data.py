from pathlib import Path
import numpy as np,pandas as pd
out=Path(__file__).parent/"data"; out.mkdir(exist_ok=True); rng=np.random.default_rng(42)
stores=[]
for i in range(1,13):
    stores.append({"store":"Store "+("A" if i==1 else chr(64+i)),"region":["East","West","North","South"][(i-1)%4],"format":"Large" if i%3==0 else "Standard","size_sqft":18000+(i%4)*2500,"peer_group":"Large" if i%3==0 else "Standard"})
sd=pd.DataFrame(stores); sd.to_csv(out/"stores.csv",index=False)
sales=[]; plan=[]; costs=[]
for _,s in sd.iterrows():
    sf=rng.uniform(.85,1.15)
    for month in pd.date_range("2026-01-01","2026-10-01",freq="MS"):
        for cat,mc,rate in [("Fresh","Medium",.68),("Apparel","High",.48),("Home","High",.48),("Electronics","Low",.82),("Beauty","High",.48)]:
            base=185000*sf*(1+.015*(month.month-1))*rng.uniform(.88,1.12)
            if s.region=="East" and month.month>=9: base*=.88
            sales.append({"month":month.strftime("%Y-%m"),"store":s.store,"region":s.region,"category":cat,"margin_class":mc,"net_revenue":base,"units":base/rng.uniform(35,90),"cogs":base*rate})
            plan.append({"month":month.strftime("%Y-%m"),"store":s.store,"region":s.region,"category":cat,"planned_revenue":base*1.035})
    rev=sum(x["net_revenue"] for x in sales if x["store"]==s.store); cg=sum(x["cogs"] for x in sales if x["store"]==s.store); mult=1.22 if s.store=="Store A" else 1
    costs.append({"store":s.store,"net_revenue":rev,"cogs":cg,"labor":rev*.105*rng.uniform(.94,1.06)*mult,"rent":s.size_sqft*31/12*rng.uniform(.92,1.08)*(1.25 if s.store=="Store A" else 1),"utilities":rev*.018*rng.uniform(.9,1.1)*(1.45 if s.store=="Store A" else 1),"shrink":rev*.012*rng.uniform(.9,1.1)*mult,"logistics":rev*.025*rng.uniform(.9,1.1)})
pd.DataFrame(sales).to_csv(out/"sales.csv",index=False); pd.DataFrame(plan).to_csv(out/"plan.csv",index=False); pd.DataFrame(costs).to_csv(out/"costs.csv",index=False)
pd.DataFrame([{"store":s.store,"inventory_value":rng.uniform(180000,450000),"aged_inventory_value":rng.uniform(10000,50000)} for _,s in sd.iterrows()]).to_csv(out/"inventory.csv",index=False)
print("Synthetic dataset created.")
