# Retail CFO Conversational Analytics

An interactive, API-key-free Streamlit prototype that helps retail CFOs explore revenue performance, store profitability, pricing scenarios, and cost anomalies.

## Features

- Revenue vs. plan analysis with regional variance bridge and reconciliation.
- Store profitability bridge and peer benchmarking.
- Pricing scenario analysis with low, base, and high elasticity sensitivity.
- Cost opportunity ranking using peer cost gaps.
- Evidence panel showing selected workflow, tool calls, parameters, metric definitions, data freshness, and limitations.
- PDF analysis and JSON evidence downloads.
- Seeded synthetic data with planted East-region revenue softness and Store A cost anomalies.
- Automated tests.

## Requirements

- Python 3.10+
- macOS, Windows, or Linux
- No API key, database, Docker, or cloud account required.

## Getting Started

### macOS / Linux

1. Open Terminal.
2. Navigate to the project folder:

   ```bash
   cd retail_cfo_prototype
   ```

3. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

4. Activate it:

   ```bash
   source .venv/bin/activate
   ```

5. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Generate demo data:

   ```bash
   python generate_data.py
   ```

7. Start the application:

   ```bash
   streamlit run app.py
   ```

8. Open http://localhost:8501 in your browser.

9. Stop the application using `Control + C`.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python generate_data.py
streamlit run app.py
```

If script activation is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

## Demo Walkthrough (5–7 Minutes)

1. **Revenue performance:** Ask "Why is revenue below plan?" to explore actuals, plan, regional variance contributors, and reconciliation.
2. **Store profitability:** Ask "Why is Store A's gross margin below target?" to examine gross margin and cost gaps versus peers.
3. **Pricing strategy:** Ask "What if we increase prices by 5% on high-margin categories?" to explore elasticity sensitivity.
4. **Cost optimization:** Ask "Where can we reduce costs without hurting revenue?" to identify peer-gap opportunities.
5. **Clarification:** Ask an unsupported question to demonstrate clarification rather than unsupported assumptions.

## Running Tests

With the virtual environment activated:

```bash
pytest -q
```

Expected result: 3 tests pass.

## Project Structure

| File / Folder | Description |
|---|---|
| `app.py` | Streamlit application interface |
| `retail_analytics.py` | Analytics functions and PDF export |
| `generate_data.py` | Reproducible synthetic data generator |
| `data/` | Generated CSV datasets |
| `tests/` | Correctness and routing tests |
| `requirements.txt` | Python dependencies |

## Solution Architecture Mapping

| Blueprint Layer | Prototype Implementation |
|---|---|
| Experience | Streamlit question input, metrics, tables, charts, and downloads |
| API / Security | Demo-only access notice; production SSO not implemented |
| Agent | Rule-based router, replaceable with LLM-based typed-tool calling |
| Governed Tools | `query_metric`, `explain_variance`, `store_margin_bridge`, `peer_benchmark`, `detect_anomalies`, `simulate_scenario` |
| Semantic Layer | Explicit metric definitions and calculations in `retail_analytics.py` |
| Data | Seeded CSV datasets |
| Verification | Variance reconciliation test |
| Evidence / Export | Evidence JSON and PDF generated from result objects |

## Current Limitations

- Uses synthetic data only; it is not connected to an ERP, data warehouse, or general ledger.
- The query router is rule-based rather than LLM-powered, making the demonstration reproducible and API-key-free.
- Peer cost gaps are investigation opportunities, not approved savings.
- Scenario elasticity values are assumptions, not forecasts.
- Production SSO, row-level security, warehouse adapters, ERP write-back, and autonomous actions are not implemented.

## Roadmap to Production

1. Replace the rule-based router with an LLM that can only invoke approved, typed tools.
2. Connect customer data warehouses through read-only adapters and a finance-approved metric catalog.
3. Enforce SSO and row-level security in the data service.
4. Build a 50-question golden dataset and adversarial test suite.
5. Add audit replay, metric versioning, monitoring, and role-controlled exports.

---

**Note:** This is a demonstration prototype built using synthetic retail data to illustrate a possible Conversational Analytics solution for retail CFOs.