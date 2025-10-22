import pandas as pd
from pathlib import Path
import numpy as np
from colorama import init, Fore, Style

init(autoreset=True)

DATA = Path("data")

def load_csv(name):
    df = pd.read_csv(DATA / name, dtype=str).rename(columns=lambda c: c.strip())
    # strip stray unnamed columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    # normalize common keys if present
    for col in ("cpt_code","icd10_code","payer_id"):
        if col in df.columns: df[col] = df[col].str.strip().str.upper()
    return df

claims = load_csv("example_claims.csv")
cpt_ok  = load_csv("cpt_dx_approved.csv")
rules   = load_csv("payer_rules.csv")
denials = load_csv("denial_codes.csv")

# fast whitelist
claims["approved_combo"] = claims.merge(
    cpt_ok[["cpt_code","icd10_code"]].drop_duplicates(),
    on=["cpt_code","icd10_code"], how="left", indicator=True
)["_merge"].eq("both")

# simple duplicate detector (same patient + CPT + DX + DOS)
dup_key = ["patient_id","cpt_code","icd10_code","dos"]
claims["is_duplicate"] = claims.duplicated(dup_key, keep=False)

# helper: add a risk
def add_risk(risks, code):
    row = denials.loc[denials["code"]==code]
    if not row.empty:
        r = row.iloc[0]
        risks.append({"code": r.code, "reason": r.reason, "tip": r.prevention_tip, "cat": r.denial_category})
    return risks

risk_list = []
for _, x in claims.iterrows():
    risks = []
    # CO-15: missing/invalid auth
    if pd.isna(x.get("auth_number")) or str(x.get("auth_number","")).strip()=="":
        risks = add_risk(risks, "CO-15")
    # CO-11: CPT/DX mismatch (not in approved pairs)
    if not bool(x["approved_combo"]):
        risks = add_risk(risks, "CO-11")
    # CO-18: duplicate
    if bool(x["is_duplicate"]):
        risks = add_risk(risks, "CO-18")
    # CO-222: naive example, flag units > 2
    try:
        if float(x.get("units", "0")) > 2:
            risks = add_risk(risks, "CO-222")
    except: pass
    # CO-45: naive check, charge > 400 triggers
    try:
        if float(x.get("charge_amount","0")) > 400:
            risks = add_risk(risks, "CO-45")
    except: pass
    # CO-16: missing critical demographics/NPI/CLIA
    critical = ["rendering_npi","referring_provider_id"]
    if any(str(x.get(c,"")).strip()=="" for c in critical):
        risks = add_risk(risks, "CO-16")
    risk_list.append(risks)

claims["risks"] = risk_list

# score
weights = {"CO-29":25,"CO-15":20,"CO-11":20,"CO-18":15,"CO-222":15,"CO-97":15,"CO-45":15,"CO-16":10,"CO-167":15}
def score(row):
    s = 100
    for r in row["risks"]:
        s -= weights.get(r["code"], 10)
    if row["approved_combo"]: s += 5
    return max(0, min(100, s))

claims["Glitch_Score"] = claims.apply(score, axis=1)

# human-readable summary fields
claims["denial_codes"] = claims["risks"].apply(lambda rs: ", ".join(sorted({r["code"] for r in rs})) or "—")
claims["prevention_tips"] = claims["risks"].apply(lambda rs: list(dict.fromkeys([r["tip"] for r in rs])))

# select output columns
out_cols = [
    "claim_id","payer_id","cpt_code","icd10_code","units","charge_amount",
    "approved_combo","denial_codes","Glitch_Score","prevention_tips","notes"
]

def claim_status(row):
    # anything with denial codes or very low score = DENY
    has_denial = bool(row.get("denial_codes")) and str(row["denial_codes"]).strip() != "[]"
    score = int(row["Glitch_Score"])
    if has_denial or score < 70:
        return "DENY"
    elif score < 100:
        return "WARN"
    else:
        return "PASS"

def colorize(status, text):
    if status == "DENY":
        return Fore.RED + text + Style.RESET_ALL
    if status == "WARN":
        return Fore.YELLOW + text + Style.RESET_ALL
    return Fore.GREEN + text + Style.RESET_ALL

# --- colorized list view ---
sorted_df = claims[out_cols].sort_values("Glitch_Score")
print("\n" + colorize("PASS", "=== RX GLITCH — RESULTS (sorted by score) ==="))
header = f"{'STATUS':<7} {'CLAIM':<9} {'PAYER':<18} {'CPT':<6} {'DX':<7} {'U':<2} {'CHARGE':>7} {'SCORE':>5}  {'DENIALS / NOTES'}"
print(header)
print("-" * len(header))

for _, r in sorted_df.iterrows():
    status = claim_status(r)
    line = (
        f"{status:<7} "
        f"{str(r['claim_id']):<9} "
        f"{str(r['payer_id']):<18} "
        f"{str(r['cpt_code']):<6} "
        f"{str(r['icd10_code']):<7} "
        f"{int(r['units']):<2} "
        f"{int(r['charge_amount']):>7} "
        f"{int(r['Glitch_Score']):>5} "
        f"{str(r['denial_codes']) if r['denial_codes'] else ''} "
        f"{str(r['notes']) if r['notes'] else ''}"
    )
    print(colorize(status, line))

print(Fore.CYAN + Style.BRIGHT + "\n🟢 PASS  |  🟡 WARN  |  🔴 DENY\n" + Style.RESET_ALL)


# --- flagged section (keep it tight) ---
flagged = claims[claims["Glitch_Score"] < 100]
if not flagged.empty:
    print(colorize("WARN", "\n⚠️  FLAGGED CLAIMS (Potential Issues):"))
    print(flagged[out_cols].to_string(index=False))
else:
    print(colorize("PASS", "\n✅ All claims passed glitch checks. No issues detected."))

# --- Export flagged claims ---
# --- Export flagged claims ---
flagged.to_csv("flagged_claims_output.csv", index=False)
print(Fore.CYAN + "\n💾 Saved flagged claims to flagged_claims_output.csv" + Style.RESET_ALL)

# ======================================================
#  WRAPPER FUNCTION FOR STREAMLIT APP
# ======================================================

from pathlib import Path
import pandas as pd

def predict_denial_risk(claim: dict) -> float:
    """
    claim example:
      {
        "cpt": "93000",
        "icd10": ["I10", "J30.9"],
        "plan_id": "PAYER-XXX-001",  # or payer name
        "dob": "1980-01-01"
      }
    """
    DATA = Path("data")

    # Load approved CPT/ICD combos if available
    cpt_ok_path = DATA / "cpt_dx_approved.csv"
    if cpt_ok_path.exists():
        cpt_ok = pd.read_csv(cpt_ok_path, dtype=str)
    else:
        cpt_ok = pd.DataFrame(columns=["cpt_code", "icd10_code"])

    cpt = str(claim.get("cpt", "")).strip()
    icds = [str(x).strip().upper() for x in claim.get("icd10", []) if str(x).strip()]

    # Simple heuristic: approved combo = low denial risk
    approved = False
    if not cpt_ok.empty and cpt and icds:
        match = cpt_ok[cpt_ok["cpt_code"].astype(str) == cpt]
        if not match.empty:
            approved_icds = set(match["icd10_code"].astype(str).str.upper())
            approved = any(ic in approved_icds for ic in icds)

    glitch_score = 100 if approved else 70
    denial_risk = max(0.0, min(1.0, 1 - glitch_score / 100.0))
    return denial_risk
