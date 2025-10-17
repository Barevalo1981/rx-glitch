import json
import streamlit as st
from rx_glitch_engine import predict_denial_risk

st.set_page_config(page_title="RX GLITCH — Claim Check", layout="centered")
st.title("RX GLITCH ⚡ Claim Check")
st.caption("Real-time front-end intelligence for payment integrity")

with st.form("claim_form"):
    cpt = st.text_input("CPT", "93000")
    icd10_text = st.text_input("ICD-10 (comma separated)", "I10")
    plan_id = st.text_input("Plan ID", "PAYER-ACME-123")
    dob = st.text_input("DOB (YYYY-MM-DD)", "1980-01-01")
    submitted = st.form_submit_button("Predict Denial Risk")

if submitted:
    claim = {
        "cpt": cpt.strip(),
        "icd10": [x.strip() for x in icd10_text.split(",") if x.strip()],
        "plan_id": plan_id.strip(),
        "dob": dob.strip()
    }
    try:
        score = predict_denial_risk(claim)
        st.success(f"Predicted denial risk: **{score:.2f}**")
        st.json(claim)
    except Exception as e:
        st.error(f"Error: {e}")
