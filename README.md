# Retail CFO Conversational Analytics — runnable prototype

A local, API-key-free Streamlit prototype based on the Retail CFO solution blueprint.

## Features
- Revenue vs plan with regional variance bridge and reconciliation.
- Store profitability bridge and peer benchmarking.
- Price scenario with low/base/high elasticity sensitivity.
- Cost opportunity ranking using peer cost gaps.
- Evidence panel: selected workflow, tool calls, parameters, metric definitions, data freshness and limitations.
- PDF analysis and JSON evidence downloads.
- Seeded synthetic data with planted East-region revenue softness and Store A cost anomalies.
- Automated tests.

## Requirements
Python 3.10+; macOS, Windows or Linux. No API key, database, Docker or cloud account required.

## Run on macOS / Linux
1. Unzip the project and open Terminal.
2. `cd` into the `retail_cfo_prototype` folder.
3. Create environment: `python3 -m venv .venv`
4. Activate: `source .venv/bin/activate`
5. Install: `python -m pip install --upgrade pip && pip install -r requirements.txt`
6. Generate demo data: `python generate_data.py`
7. Run: `streamlit run app.py`
8. Open `http://localhost:8501` if the browser does not open automatically.
9. Stop with `Control + C`.

## Run on Windows PowerShell
```powershell
cd $HOME\Downloads\retail_cfo_prototype
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python generate_data.py
streamlit run app.py
```
If script activation is blocked: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.

## Demo walkthrough (5–7 minutes)
1. Ask `Why is revenue below plan?` — show actual, plan, regional variance contributors and reconciliation.
2. Ask `Why is Store A's gross margin below target?` — show gross margin and cost gaps versus peers.
3. Ask `What if we increase prices by 5% on high-margin categories?` — show elasticity sensitivity.
4. Ask `Where can we reduce costs without hurting revenue?` — show peer-gap opportunities.
5. Ask an unsupported question — demonstrate clarification rather than guessing.

## Tests
With the environment active: `pytest -q` (expected: 3 tests pass).

## Project map
- `app.py`: Streamlit interface.
- `retail_analytics.py`: typed deterministic analytics functions and PDF export.
- `generate_data.py`: reproducible synthetic data generator.
- `data/`: generated CSVs.
- `tests/`: basic correctness and routing tests.

## Architecture mapping
| Blueprint layer | Prototype |
|---|---|
| Experience | Streamlit question input, metrics, tables, charts, downloads |
| API/security | Demo-only access notice; production SSO not implemented |
| Agent | Rule-based router (replaceable with LLM typed-tool calling) |
| Governed tools | `query_metric`, `explain_variance`, `store_margin_bridge`, `peer_benchmark`, `detect_anomalies`, `simulate_scenario` |
| Semantic layer | Explicit metric definitions/calculations in `retail_analytics.py` |
| Data | Seeded CSV files |
| Verification | Variance reconciliation test |
| Evidence/export | Evidence JSON and PDF from result objects |

## Honest limitations
Synthetic data only; not connected to ERP, warehouse or general ledger. The router is deliberately rule-based, not an LLM, so the demo is reproducible and needs no key. Peer gaps are not approved savings. Scenario elasticity is assumed, not a forecast. No production SSO, row-level security, warehouse adapter, ERP write-back or autonomous actions.

## Next steps toward production
1. Replace the rule-based router with an LLM that can only call typed tools.
2. Connect a customer warehouse through a read-only adapter and finance-approved metric catalog.
3. Enforce SSO and row-level security in the data service.
4. Build a 50-question golden set plus adversarial tests.
5. Add audit replay, metric versioning, monitoring and role-controlled exports.
