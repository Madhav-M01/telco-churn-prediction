import streamlit as st
import joblib
import pandas as pd
import numpy as np
import requests
import json

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
MODEL_PATH = r"C:\TELCO CUSTOMER CHURN\anaconda_projects\db\artifacts\churn_model_20260418_121842.pkl"
THRESHOLD  = 0.22
CLAUDE_API = "https://api.anthropic.com/v1/messages"
CLAUDE_KEY = "YOUR_ANTHROPIC_API_KEY"   # ← apni key yahan daalo

st.set_page_config(
    page_title="Churn Prediction Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
body { background-color: #0e1117; }
.chat-bubble-bot {
    background: linear-gradient(135deg, #1a1f35, #1e2a45);
    border-left: 3px solid #4cf;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 8px 0;
    color: #e0e0e0;
    font-size: 15px;
    line-height: 1.6;
}
.chat-bubble-user {
    background: linear-gradient(135deg, #1a2a1a, #1e3a1e);
    border-left: 3px solid #4fc;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 8px 0;
    color: #e0e0e0;
    font-size: 15px;
    text-align: right;
}
.prediction-churn {
    background: linear-gradient(135deg, #3a1a1a, #4a2020);
    border: 2px solid #e74c3c;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    color: #ff6b6b;
    font-size: 22px;
    font-weight: bold;
    margin: 12px 0;
}
.prediction-safe {
    background: linear-gradient(135deg, #1a3a1a, #204a20);
    border: 2px solid #2ecc71;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    color: #55efc4;
    font-size: 22px;
    font-weight: bold;
    margin: 12px 0;
}
.explain-box {
    background: linear-gradient(135deg, #1a1f35, #1e2a45);
    border: 1px solid #4cf;
    border-radius: 12px;
    padding: 18px;
    color: #cce;
    font-size: 14px;
    line-height: 1.8;
    margin: 10px 0;
}
.stButton > button {
    background: linear-gradient(135deg, #1a2a4a, #1e3a6e);
    color: #4af;
    border: 1px solid #4af;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 14px;
    transition: all 0.2s;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2a3a6a, #2e4a8e);
    color: #fff;
}
h1 { color: #4cf !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    obj = joblib.load(MODEL_PATH)
    # Agar dict format mein save hua hai
    if isinstance(obj, dict):
        return obj["model"]
    return obj

try:
    model = load_model()
except Exception as e:
    st.error(f"❌ Model load nahi hua: {e}\nCheck karo ke MODEL_PATH sahi hai!")
    st.stop()

# ─────────────────────────────────────────────
# QUESTIONS FLOW
# ─────────────────────────────────────────────
QUESTIONS = [
    {
        "key":     "gender",
        "ask":     "What is the customer's **gender**?",
        "options": ["Male", "Female"],
        "type":    "choice"
    },
    {
        "key":     "SeniorCitizen",
        "ask":     "Is the customer a **Senior Citizen** (age 65+)?",
        "options": ["Yes", "No"],
        "type":    "choice",
        "map":     {"Yes": 1, "No": 0}
    },
    {
        "key":     "Partner",
        "ask":     "Does the customer have a **Partner** (spouse/companion)?",
        "options": ["Yes", "No"],
        "type":    "choice"
    },
    {
        "key":     "Dependents",
        "ask":     "Does the customer have **Dependents** (children/family members)?",
        "options": ["Yes", "No"],
        "type":    "choice"
    },
    {
        "key":     "tenure",
        "ask":     "How many **months** has the customer been with the company?\n\n*(Type a number, e.g. 12)*",
        "type":    "number",
        "min":     0,
        "max":     72
    },
    {
        "key":     "PhoneService",
        "ask":     "Does the customer have a **Phone Service**?",
        "options": ["Yes", "No"],
        "type":    "choice"
    },
    {
        "key":     "MultipleLines",
        "ask":     "Does the customer have **Multiple Lines**?",
        "options": ["Yes", "No", "No phone service"],
        "type":    "choice"
    },
    {
        "key":     "InternetService",
        "ask":     "What type of **Internet Service** does the customer have?",
        "options": ["DSL", "Fiber optic", "No"],
        "type":    "choice"
    },
    {
        "key":     "OnlineSecurity",
        "ask":     "Does the customer have **Online Security** add-on?",
        "options": ["Yes", "No", "No internet service"],
        "type":    "choice"
    },
    {
        "key":     "OnlineBackup",
        "ask":     "Does the customer have **Online Backup** add-on?",
        "options": ["Yes", "No", "No internet service"],
        "type":    "choice"
    },
    {
        "key":     "DeviceProtection",
        "ask":     "Does the customer have **Device Protection** plan?",
        "options": ["Yes", "No", "No internet service"],
        "type":    "choice"
    },
    {
        "key":     "TechSupport",
        "ask":     "Does the customer have **Tech Support** service?",
        "options": ["Yes", "No", "No internet service"],
        "type":    "choice"
    },
    {
        "key":     "StreamingTV",
        "ask":     "Does the customer use **Streaming TV**?",
        "options": ["Yes", "No", "No internet service"],
        "type":    "choice"
    },
    {
        "key":     "StreamingMovies",
        "ask":     "Does the customer use **Streaming Movies**?",
        "options": ["Yes", "No", "No internet service"],
        "type":    "choice"
    },
    {
        "key":     "Contract",
        "ask":     "What is the customer's **Contract type**?\n\n*(This is one of the biggest churn drivers!)*",
        "options": ["Month-to-month", "One year", "Two year"],
        "type":    "choice"
    },
    {
        "key":     "PaperlessBilling",
        "ask":     "Is the customer enrolled in **Paperless Billing**?",
        "options": ["Yes", "No"],
        "type":    "choice"
    },
    {
        "key":     "PaymentMethod",
        "ask":     "What is the customer's **Payment Method**?",
        "options": [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ],
        "type":    "choice"
    },
    {
        "key":     "MonthlyCharges",
        "ask":     "What are the customer's **Monthly Charges** (in $)?\n\n*(Type a number, e.g. 65.5)*",
        "type":    "number",
        "min":     0.0,
        "max":     200.0
    },
    {
        "key":     "TotalCharges",
        "ask":     "What are the customer's **Total Charges** till date (in $)?\n\n*(Type a number, e.g. 840.0)*",
        "type":    "number",
        "min":     0.0,
        "max":     10000.0
    },
]

# ─────────────────────────────────────────────
# FEATURE ENGINEERING (same as training)
# ─────────────────────────────────────────────
def engineer_features(data: dict) -> pd.DataFrame:
    d = pd.DataFrame([data])
    d["TotalCharges"]        = pd.to_numeric(d["TotalCharges"], errors="coerce").fillna(0)
    d["TenureGroup"]         = pd.cut(d["tenure"], bins=[-1,6,12,24,48,72],
                                      labels=["0-6m","6-12m","12-24m","24-48m","48m+"]).astype(str)
    d["IsNewCustomer"]       = (d["tenure"] <= 6).astype(int)
    d["AvgMonthlySpend"]     = d["TotalCharges"] / (d["tenure"] + 1)
    d["SpendRatio"]          = d["MonthlyCharges"] / (d["AvgMonthlySpend"] + 1e-3)
    d["SpendAcceleration"]   = d["MonthlyCharges"] - d["AvgMonthlySpend"]
    svc = ["OnlineSecurity","OnlineBackup","DeviceProtection",
           "TechSupport","StreamingTV","StreamingMovies"]
    d["NumServices"]         = d[svc].apply(lambda r: sum(1 for v in r if v=="Yes"), axis=1)
    d["HasProtectionBundle"] = ((d["OnlineSecurity"]=="Yes") & (d["DeviceProtection"]=="Yes")).astype(int)
    d["HasStreamingBundle"]  = ((d["StreamingTV"]=="Yes") & (d["StreamingMovies"]=="Yes")).astype(int)
    d["ContractRiskScore"]   = d["Contract"].map({"Month-to-month":3,"One year":1,"Two year":0})
    d["HighRiskPayment"]     = (d["PaymentMethod"]=="Electronic check").astype(int)
    d["FamilyStability"]     = ((d["Partner"]=="Yes") | (d["Dependents"]=="Yes")).astype(int)
    d["IsFiberCustomer"]     = (d["InternetService"]=="Fiber optic").astype(int)
    return d

# ─────────────────────────────────────────────
# CLAUDE EXPLANATION
# ─────────────────────────────────────────────
def get_explanation(data: dict, prob: float, prediction: str) -> str:
    key_factors = []
    if data.get("Contract") == "Month-to-month":
        key_factors.append("month-to-month contract (highest churn risk)")
    if data.get("tenure", 99) <= 6:
        key_factors.append(f"very new customer (only {data['tenure']} months tenure)")
    if data.get("PaymentMethod") == "Electronic check":
        key_factors.append("electronic check payment method (associated with higher churn)")
    if data.get("InternetService") == "Fiber optic":
        key_factors.append("fiber optic internet (premium but high-churn segment)")
    if data.get("OnlineSecurity") == "No":
        key_factors.append("no online security add-on")
    if data.get("NumServices", 0) <= 1:
        key_factors.append("low service engagement (few add-ons)")

    factors_str = ", ".join(key_factors) if key_factors else "multiple risk indicators"

    prompt = f"""You are an expert telecom data scientist explaining a churn prediction to a business user.

Customer Profile:
- Contract: {data.get('Contract')}
- Tenure: {data.get('tenure')} months
- Monthly Charges: ${data.get('MonthlyCharges')}
- Internet Service: {data.get('InternetService')}
- Payment Method: {data.get('PaymentMethod')}
- Online Security: {data.get('OnlineSecurity')}
- Senior Citizen: {data.get('SeniorCitizen')}
- Partner: {data.get('Partner')}

Churn Probability: {prob:.1%}
Prediction: {prediction}
Key Risk Factors Identified: {factors_str}

Write ONE clear, professional paragraph (4-5 sentences) explaining:
1. What the prediction is and how confident the model is
2. Which 2-3 specific factors are driving this prediction
3. What business action should be taken

Write in simple English. Be direct and actionable. Do not use bullet points."""

    try:
        response = requests.post(
            CLAUDE_API,
            headers={
                "x-api-key": CLAUDE_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        result = response.json()
        return result["content"][0]["text"]
    except Exception:
        # Fallback explanation
        return (
            f"Based on our machine learning model, this customer has a **{prob:.1%} probability of churning**, "
            f"which is {'above' if prob >= THRESHOLD else 'below'} our decision threshold of {THRESHOLD:.0%}. "
            f"The key risk factors identified are: {factors_str}. "
            f"{'Immediate retention action is recommended — consider offering a contract upgrade or loyalty discount.' if prediction == 'CHURN' else 'This customer appears stable. Continue standard engagement.'}"
        )

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "step"       not in st.session_state: st.session_state.step       = 0
if "answers"    not in st.session_state: st.session_state.answers    = {}
if "chat_log"   not in st.session_state: st.session_state.chat_log   = []
if "predicted"  not in st.session_state: st.session_state.predicted  = False
if "num_input"  not in st.session_state: st.session_state.num_input  = ""

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.title("🤖 Churn Prediction Chatbot")
st.markdown("<p style='text-align:center;color:#778;font-size:13px;'>Powered by your trained ML model · Threshold @ 0.22</p>", unsafe_allow_html=True)
st.markdown("---")

# Welcome message
if st.session_state.step == 0 and not st.session_state.chat_log:
    welcome = (
        "👋 Hello! I'm your **AI-powered Churn Prediction Assistant**.\n\n"
        "I will ask you a few questions about a customer — one at a time — "
        "and then predict whether they are likely to **churn (leave)** or **stay**.\n\n"
        "At the end, I'll also explain *why* the model made that prediction.\n\n"
        "Let's begin! 🚀"
    )
    st.session_state.chat_log.append(("bot", welcome))

# Render chat history
for role, msg in st.session_state.chat_log:
    if role == "bot":
        st.markdown(f"<div class='chat-bubble-bot'>🤖 {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-user'>{msg} 👤</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONVERSATION FLOW
# ─────────────────────────────────────────────
if not st.session_state.predicted:
    step = st.session_state.step

    if step < len(QUESTIONS):
        q = QUESTIONS[step]

        # Show question bubble
        st.markdown(f"<div class='chat-bubble-bot'>🤖 **Question {step+1}/{len(QUESTIONS)}**<br><br>{q['ask']}</div>", unsafe_allow_html=True)

        # Progress bar
        st.progress((step) / len(QUESTIONS))

        # Input based on type
        if q["type"] == "choice":
            cols = st.columns(min(len(q["options"]), 3))
            for i, opt in enumerate(q["options"]):
                with cols[i % len(cols)]:
                    if st.button(opt, key=f"btn_{step}_{i}"):
                        val = q.get("map", {}).get(opt, opt)
                        st.session_state.answers[q["key"]] = val
                        st.session_state.chat_log.append(("bot",
                            f"**Question {step+1}/{len(QUESTIONS)}**<br><br>{q['ask']}"))
                        st.session_state.chat_log.append(("user", f"**{opt}**"))
                        st.session_state.step += 1
                        st.rerun()

        elif q["type"] == "number":
            num_val = st.number_input(
                "Enter value:",
                min_value=float(q["min"]),
                max_value=float(q["max"]),
                value=float(q["min"]),
                step=0.5 if q["max"] > 10 else 1.0,
                key=f"num_{step}"
            )
            if st.button("✅ Confirm", key=f"confirm_{step}"):
                st.session_state.answers[q["key"]] = num_val
                st.session_state.chat_log.append(("bot",
                    f"**Question {step+1}/{len(QUESTIONS)}**<br><br>{q['ask']}"))
                st.session_state.chat_log.append(("user", f"**{num_val}**"))
                st.session_state.step += 1
                st.rerun()

    # ── ALL QUESTIONS DONE → PREDICT ──
    else:
        st.markdown("<div class='chat-bubble-bot'>🤖 ✅ All information collected! Let me analyze and predict now...</div>",
                    unsafe_allow_html=True)

        with st.spinner("🔍 Model is thinking..."):
            try:
                df_input = engineer_features(st.session_state.answers)
                prob      = model.predict_proba(df_input)[:, 1][0]
                label     = "CHURN" if prob >= THRESHOLD else "No Churn"

                # Prediction box
                if label == "CHURN":
                    st.markdown(f"""
                    <div class='prediction-churn'>
                        ⚠️ PREDICTION: HIGH CHURN RISK<br>
                        <span style='font-size:32px;'>{prob:.1%}</span> Churn Probability
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='prediction-safe'>
                        ✅ PREDICTION: CUSTOMER LIKELY TO STAY<br>
                        <span style='font-size:32px;'>{prob:.1%}</span> Churn Probability
                    </div>""", unsafe_allow_html=True)

                # Explanation
                st.markdown("<br>**📝 Model Explanation:**", unsafe_allow_html=True)
                explanation = get_explanation(st.session_state.answers, prob, label)
                st.markdown(f"<div class='explain-box'>💡 {explanation}</div>",
                            unsafe_allow_html=True)

                # Summary table
                st.markdown("<br>**📊 Customer Summary:**", unsafe_allow_html=True)
                summary = {k: v for k, v in st.session_state.answers.items()
                           if k in ["Contract","tenure","MonthlyCharges",
                                    "InternetService","PaymentMethod","SeniorCitizen"]}
                st.table(pd.DataFrame(summary.items(), columns=["Feature", "Value"]))

                st.session_state.predicted = True

            except Exception as e:
                st.error(f"Prediction error: {e}")

# ── RESTART ──
if st.session_state.predicted:
    st.markdown("---")
    if st.button("🔄 Predict for Another Customer", use_container_width=True):
        for key in ["step","answers","chat_log","predicted","num_input"]:
            del st.session_state[key]
        st.rerun()
