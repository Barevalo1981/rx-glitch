# 🧠 RX GLITCH — Architecture Overview

## 🔍 Mission
Detect and prevent payer-policy drift *before* it hits revenue.

Every medical claim is a sentence written in a 1970s language (EDI).  
RX GLITCH translates that chaos into clarity — predicting denials, enforcing compliance, and giving providers real-time visibility into what will or won’t be paid.

---

## ⚙️ Core Components

| Layer | Name | Purpose |
|-------|------|----------|
| **Ingestion** | Policy Parser | Scrapes, downloads, and converts payer PDFs (LCDs, NCDs, Coverage Policies) into structured data. |
| **Normalization** | Rules Engine | Maps CPT × ICD logic into a unified schema. Handles payer-specific quirks. |
| **Inference** | Claim-Check API | FastAPI endpoint that scores each claim: `risk`, `reason`, and `references`. |
| **Drift Radar** | Policy Diff Model | Compares new vs old payer policies; flags silent changes (“drift”). |
| **Interface** | Streamlit UI | Clean dashboard for coders, billers, and admins. |
| **Data Store** | PostgreSQL / S3 | Houses rule triples and logs (no PHI). |
| **Security Layer** | Local Inference | Runs fully inside the customer’s private environment — no PHI leaves the perimeter. |

---

## 🧩 Data Flow

1. **Collect Policies** — PDFs pulled from payer portals and CMS.  
2. **Parse & Extract** — convert to rule triples `(CPT, ICD10[], Coverage_Reason)`.  
3. **Normalize** — standardize language and tag by payer.  
4. **Store Rules** — lightweight database (Postgres).  
5. **Run Claim-Check** — user sends claim data to API; engine predicts denial risk.  
6. **Return Insight** — JSON response with risk score + explanation.  
7. **Log & Learn** — anonymized outcomes retrain the drift model.

---

## 🔐 Security & Compliance

- **Local inference**: the algorithm travels; the data stays.  
- **Ephemeral cache**: clears in < 60 seconds.  
- **No PHI** stored or transmitted outside client VPC.  
- **Role-based access** + audit logging.  
- **HIPAA** + SOC2 readiness from day one.

---

## 🧭 Technology Stack

| Layer | Tool |
|-------|------|
| Backend API | **FastAPI (Python)** |
| Frontend UI | **Streamlit** |
| Data Store | **PostgreSQL / S3** |
| Model Pipeline | **spaCy + transformers + NLP** |
| Deployment | **Docker + AWS PrivateLink** |
| Monitoring | **Prometheus / Grafana** |

---

## 🚀 Scalability Vision
- Modular microservices — each payer runs as its own container.  
- Continuous learning loop from anonymous drift updates.  
- Self-healing deployment with versioned policy diffs.  
- API marketplace for billing vendors, RCMs, and payers.

---

## 🧩 Next Files
- [`api_spec.md`](api_spec.md) → technical endpoints.  
- [`hipaa_notes.md`](hipaa_notes.md) → compliance checklist.  
- [`roi_case_studies.md`](roi_case_studies.md) → pilot data + metrics.

---

*Control the narrative. Control the numbers.* ⚡️
