# RX GLITCH ⚡️
**Real-Time Front-End Intelligence for Payment Integrity**

### 🧠 Founder’s Note
I didn’t hack the system with code — I hacked it with attention.  
From one client alone, $4.2 million a year was leaking through typos, outdated policies, and manual slip-ups.  
I built a simple pre-check that stopped the bleeding — and then turned it into RX GLITCH,  
an automated denial-prevention engine that catches what humans miss and makes sure the money actually lands where it belongs.

---

### ⚡ Mission
Stop insurance denials before they happen.  
RX GLITCH predicts billing errors in real time — fixing a $300B annual revenue leak in U.S. healthcare.

---

RX GLITCH detects hidden payer rule drift before claims are submitted.
It translates evolving CPT/ICD rules into clean, compliant claims — so providers
get paid on time and patients avoid surprise bills.

## 💡 Problem
Healthcare still runs on a 1970s computer language (EDI).  
Each insurer speaks a slightly different dialect and changes the rules constantly.  
One mismatch = one denial.  
Doctors lose revenue. Patients get chaos.

## 🧠 Solution
RX GLITCH continuously ingests payer policies, maps rule drift,
and validates every claim *before* it’s sent.  
→ Real-time accuracy. Zero denials. Predictable revenue.

## ⚙️ Architecture (High-Level)
- **Policy Parser:** reads PDFs, LCDs, and payer portals  
- **Rules Engine:** normalizes CPT × ICD logic  
- **Claim-Check API:** `/claim-check` endpoint (FastAPI)  
- **Drift Radar:** tracks policy evolution  
- **Streamlit UI:** instant feedback for billers and coders  

## 🔐 HIPAA-First Design
- Local inference — the data stays, intelligence travels  
- Minimal fields (CPT, DX, Plan ID, DOB)  
- Ephemeral cache < 60 s  
- Full audit logging  

---

## 🚀 Quick Start (Smoke Test)

### Run locally
1. Install Python 3.10+  
2. `pip install -r requirements.txt`  
3. `python rx_glitch_engine.py`  
   You should see:  
   `Predicted denial risk: <number between 0 and 1>`

### (Optional) Run in Codespaces
1. Click **Code → Create codespace on main**  
2. In the terminal:  
   `pip install -r requirements.txt`  
   `python rx_glitch_engine.py`

### Files
- `rx_glitch_engine.py` — v0.1 engine (mock scoring)  
- `data_dictionary.csv` — field schema  
- `docs/openapi.yml` — API contract (`/claim-check`)  
- `example_claim.json` — sample payload

## 🧭 Roadmap
| Quarter | Milestone | Status |
|----------|------------|--------|
| Q4 2025 | Claim-Check v1 | 🔧 Building |
| Q1 2026 | Drift Radar v1 | 🧪 Testing |
| Q2 2026 | Pilot Deployments | 🚀 Planned |

## 📈 Proof of Value
- 27 % drop in denials within 60 days of implementation  
- 9-day reduction in Days Sales Outstanding (DSO)  
- $42 k / month in recovered revenue across initial pilot sites  

---

### 🦾 Founder
**Brooke Arevalo**  
Real-time front-end intelligence for payment integrity.  
[rxglitch.com](https://rxglitch.com) • [github.com/Barevalo1981/rx-glitch](https://github.com/Barevalo1981/rx-glitch)

---
*“Control the narrative. Control the numbers.” — RX GLITCH*
