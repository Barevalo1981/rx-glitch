from __future__ import annotations
import json
from datetime import datetime
import streamlit as st
import os
import streamlit as st

# ==========================================================
# Password Gate (runs before any UI)
# ==========================================================

APP_PASSWORD = st.secrets.get("APP_PASSWORD") or os.getenv("APP_PASSWORD")

def check_password():
    """Returns True if password is correct."""

    # If no password set, do not block (fails open during dev)
    if not APP_PASSWORD:
        st.warning("Password gate disabled (no APP_PASSWORD set).")
        return True

    # If already authenticated this session
    if st.session_state.get("authenticated", False):
        return True

    # Ask for password
    password = st.text_input("Enter demo password:", type="password")

    if password:
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            return True
        else:
            st.error("Incorrect password")

    return False

if not check_password():
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Page config + light polish
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RX GL⚡TCH",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
/* Keep header visible (Streamlit adds big top padding) */
.block-container {
  padding-top: 2.5rem !important;
  padding-bottom: 3rem !important;
}

/* UI polish */
.small { color:#6b7280; font-size:12px; }
.badge { display:inline-block; padding:4px 10px; border-radius:999px; color:#fff; font-weight:700; }
.badge-green { background:#16a34a; } /* good */
.badge-amber { background:#f59e0b; } /* borderline */
.badge-red   { background:#ef4444; } /* bad */

.progress-wrap { height:10px; background:#e5e7eb; border-radius:8px; overflow:hidden; }
.progress-bar  { height:10px; background:#3b82f6; }

label.css-16idsys, .stTextInput label, .stSelectbox label { font-size:12px; }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Sample claims library (intentionally different risk profiles)
# ─────────────────────────────────────────────────────────────────────────────
SAMPLES = {
    "✅ Clean Claim": {
        "reason": "Annual Checkup",
        "cpt": "80050",                # CMP panel — typically preventive
        "dx": "Z00.00",                # General adult medical exam
        "payer": "Aetna – PPO (NJ)",
        "dob": "1985-06-10",
        "dos": datetime.now().strftime("%Y-%m-%d"),
        "sex": "Female",
    },
    "⚠️ Borderline Claim": {
        "reason": "Headache",
        "cpt": "99213",                # Office/outpatient established
        "dx": "R51.9",                 # Headache, unspecified
        "payer": "Horizon (NJ)",
        "dob": "1990-01-01",
        "dos": datetime.now().strftime("%Y-%m-%d"),
        "sex": "Male",
    },
    "❌ Broken Claim": {
        "reason": "Chest Pain",
        "cpt": "93000",                # EKG
        "dx": "H52.13",                # Myopia (eye) — deliberately incompatible
        "payer": "United (NJ)",
        "dob": "1974-02-12",
        "dos": datetime.now().strftime("%Y-%m-%d"),
        "sex": "Male",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Deterministic rules engine (HIGHER = CLEANER)
# ─────────────────────────────────────────────────────────────────────────────
def rule_score(cpt: str, dx: str, payer: str, dob: str, dos: str) -> dict:
    """
    Simple, deterministic heuristics for a consistent demo.
    Returns: {"denial_risk": str, "score": int, "reasons": list[str], "recommended_fixes": list[str]}
    """
    cpt = (cpt or "").strip()
    dx = (dx or "").strip().upper()
    payer_l = (payer or "").lower()

    reasons, fixes = [], []

    # Start from a middle cleanliness baseline. We’ll nudge up/down.
    score = 60  # 0 = worst (likely denial), 100 = best (clean)

    # CPT/DX compatibility:
    # Clean: Preventive panel with preventive dx -> strong positive
    if cpt == "80050" and dx.startswith("Z00"):
        score += 30  # -> ~90
        reasons.append("Preventive service likely covered when paired with Z00.00.")
        fixes.append("Document preventive context; include annual exam note.")

    # Borderline: E/M for headache -> mild positive (needs documentation)
    if cpt == "99213" and dx in {"R51.9", "J06.9", "M54.5"}:
        score += 0  # keep close to ~60 (borderline)
        reasons.append("E/M visit often hinges on documentation of medical necessity.")
        fixes.append("Include symptom duration/severity and prior self-care; ensure level-of-service criteria.")

    # Broken: EKG with myopia dx -> strong negative
    if cpt == "93000" and dx.startswith("H52"):
        score -= 40  # -> ~20
        reasons.append("Diagnosis unrelated to cardiac test; likely medical necessity denial.")
        fixes.append("Use a cardiac-related ICD-10 (e.g., R07.9, I20.9) if appropriate and documented.")

    # Payer tendencies
    if "horizon" in payer_l:
        score += 5
        reasons.append("Payer expects strong preventive documentation.")
    if "united" in payer_l:
        score -= 5
        reasons.append("Payer frequently enforces medical necessity edits for diagnostics.")

    # DOS sanity: future DOS penalizes cleanliness
    try:
        d_dos = datetime.strptime(dos, "%Y-%m-%d").date()
        if (d_dos - datetime.now().date()).days > 2:
            score -= 10
            reasons.append("Date of service is in the future.")
            fixes.append("Correct DOS or defer claim until service is performed.")
    except Exception:
        pass

    # Clamp to [0, 100]
    score = max(0, min(100, score))

    # Label thresholds (HIGHER = CLEANER)
    if score >= 80:
        risk = "good"        # green
    elif score >= 40:
        risk = "borderline"  # amber
    else:
        risk = "bad"         # red

    if not reasons:
        reasons = ["Coverage depends on plan specifics and documentation quality."]
    if not fixes:
        fixes = ["Verify payer policy; ensure notes support medical necessity."]

    return {
        "denial_risk": risk,
        "score": score,
        "reasons": reasons,
        "recommended_fixes": fixes,
    }

# Optional: OpenAI assist (disabled in demo)
def ai_validate(cpt, dx, payer, dob, dos) -> dict | None:
    return None

def validate_claim(cpt, dx, payer, dob, dos) -> dict:
    data = ai_validate(cpt, dx, payer, dob, dos)
    return data or rule_score(cpt, dx, payer, dob, dos)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers to render result
# ─────────────────────────────────────────────────────────────────────────────
def risk_badge(score: int) -> str:
    if score >= 80:
        cls = "badge badge-green"   # ✅ clean
    elif score >= 40:
        cls = "badge badge-amber"   # ⚠️ borderline
    else:
        cls = "badge badge-red"     # ❌ bad
    return f"<span class='{cls}'>{score}/100</span>"

def progress(score: int) -> str:
    pct = max(0, min(100, score))
    return f"""
<div class='progress-wrap'>
  <div class='progress-bar' style='width:{pct}%;'></div>
</div>
<div class='small'>0 = likely denial · 100 = clean</div>
"""

def show_result(payload: dict):
    r = payload["result"]
    st.markdown(f"**Risk Score:** {risk_badge(r['score'])}", unsafe_allow_html=True)
    st.markdown(progress(r["score"]), unsafe_allow_html=True)

    ins = payload["inputs"]
    st.caption(
        f"Inputs → CPT: {ins['cpt']} | ICD-10: {ins['dx']} | Payer: {ins['payer']} | DOS: {ins['dos']}"
    )

    st.markdown("**What would’ve happened (without RX GL⚡TCH)**")
    for item in r.get("reasons", []):
        st.write(f"• {item}")

    st.markdown("**How RX GL⚡TCH fixes it**")
    for fix in r.get("recommended_fixes", []):
        st.write(f"✅ {fix}")

# ─────────────────────────────────────────────────────────────────────────────
# UI — Two columns
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### RX GL⚡TCH")
st.caption("Real-Time Front-End Intelligence for Payment Integrity")
st.divider()

left, right = st.columns([1, 1.25], gap="large")

with left:
    st.subheader("Load Sample Claim")

    selected = st.selectbox(
        "Select a sample to test:",
        list(SAMPLES.keys()),
        index=0,
        key="sample_selector",
    )

    # Auto-populate on selection
    sample_claim = SAMPLES[selected]
    st.session_state.update(sample_claim)
    st.session_state["demo_sample"] = selected

    st.button("Load Selected Claim", use_container_width=True)

    st.markdown("##### Input")
    with st.form("claim_form", clear_on_submit=False):
        reason = st.text_input("Disease / Reason for Visit", st.session_state.get("reason", ""))
        cpt    = st.text_input("CPT Code",                       st.session_state.get("cpt", ""))
        dx     = st.text_input("ICD-10 Code",                    st.session_state.get("dx", ""))
        payer  = st.text_input("Insurance Plan",                 st.session_state.get("payer", ""))
        col1, col2, col3 = st.columns(3)
        with col1:
            dob = st.text_input("Patient DOB (YYYY-MM-DD)",     st.session_state.get("dob", ""))
        with col2:
            dos = st.text_input("Date of Service",              st.session_state.get("dos", ""))
        with col3:
            sex = st.text_input("Sex",                          st.session_state.get("sex", ""))

        submitted = st.form_submit_button("Validate", use_container_width=True)

    # Persist inputs
    st.session_state.update(
        dict(reason=reason, cpt=cpt, dx=dx, payer=payer, dob=dob, dos=dos, sex=sex)
    )

with right:
    st.subheader("Result")

    if submitted:
        with st.spinner("Analyzing…"):
            result = validate_claim(cpt, dx, payer, dob, dos)
        st.session_state.last_result = {
            "inputs": dict(cpt=cpt, dx=dx, payer=payer, dob=dob, dos=dos),
            "result": result,
        }

    if "last_result" in st.session_state:
        show_result(st.session_state["last_result"])
    else:
        st.info("Load a sample or enter values, then click **Validate**.")

st.divider()
st.caption("Demo mode: educational, not billing advice. © RX GL⚡TCH")
