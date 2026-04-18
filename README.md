# 🤖 Telco Customer Churn Prediction
### End-to-End Production-Grade Machine Learning Pipeline with AI Chatbot

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-orange?style=for-the-badge&logo=scikit-learn)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-green?style=for-the-badge)](https://xgboost.readthedocs.io)

---

## 📌 Project Overview

Customer churn costs telecom companies **5–25× more** to replace a lost customer than to retain one *(Harvard Business Review)*. This project builds a **production-ready churn prediction system** optimized for **business impact**, not just accuracy.

The system predicts whether a telecom customer will churn, explains *why*, and delivers predictions through an **AI-powered conversational chatbot** — all backed by a rigorous ML pipeline.

---

## 🎯 Business Problem

| Metric | Value |
|--------|-------|
| Avg. Customer Monthly Value | $64.76 |
| Cost of Missing a Churner (FN) | $500 (lost CLTV) |
| Cost of False Alarm (FP) | $50 (wasted retention offer) |
| FN : FP Cost Ratio | **10 : 1** |
| Retention Success Rate | 30% |

> **Key Insight:** Missing a real churner is 10× more costly than a false alarm → model heavily optimizes **Recall** over Precision.

---

## 📊 Final Model Performance

| Metric | Value |
|--------|-------|
| **ROC-AUC** | **0.8503** |
| **Average Precision** | **0.6419** |
| **Recall** | **0.825** |
| **F1 Score** | **0.636** |
| **MCC** | **0.490** |
| **Brier Score** | **0.134** |
| **Expected Value/User** | **$0.15** |
| **Total Test-Set EV** | **$164** |
| Production Threshold | 0.22 |
| Test Set Size | 1,057 customers |

> **Why threshold 0.22?** PR-curve based max-F1 optimization. Low threshold intentionally set to maximize recall given the 10:1 cost asymmetry.

---

## 🏗️ Pipeline Architecture

```
Raw Data (7,043 customers)
        │
        ▼
┌───────────────────┐
│  Data Validation  │  Schema checks, null detection, PK validation
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Feature Engineering│  12 domain-driven features (tenure, spend, risk scores)
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  3-Way Split      │  Train 70% / Val 15% / Test 15% (stratified)
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Baseline Ladder   │  LR → RF → XGB → LGBM → CatBoost
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Optuna Tuning     │  200 trials, AP objective, SMOTE inside CV folds
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Ensembling      │  Stacking + Soft Voting + Single Best
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Calibration      │  Isotonic Regression (reliability diagrams)
└───────────────────┘
        │
        ▼
┌───────────────────┐
│Threshold Selection│  PR-curve max-F1 with business EV optimization
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Evaluation      │  ROC, PR, Lift, Gain, KS, Brier, Fairness
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ SHAP Explainability│  Global + Local + Dependence + Waterfall
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Deployment      │  Model card + Inference API + Drift Monitor
└───────────────────┘
```

---

## 🔬 Technical Highlights

### ✅ Hyperparameter Tuning — Optuna
- **200 trials** with TPE Sampler + Median Pruner
- Objective: **Average Precision** (imbalance-aware, better than ROC-AUC)
- SMOTE applied **inside CV folds only** → zero data leakage
- fANOVA hyperparameter importance analysis

### ✅ Cross-Validation Strategy
- `RepeatedStratifiedKFold` — **5 folds × 2 repeats = 10 evaluations**
- Lower variance estimates vs standard K-Fold
- Stratified splits preserve class ratio in every fold

### ✅ Imbalance Handling (73:27 ratio)
- SMOTE inside `ImbPipeline` (no leakage)
- Class weights on all estimators
- Threshold optimization via business EV

### ✅ Probability Calibration
- Isotonic regression on held-out validation set
- Reliability diagrams pre/post calibration
- Brier score improvement tracked

### ✅ SHAP Explainability
- **Global**: Feature importance bar + Beeswarm plots
- **Local**: Waterfall plots for individual predictions
- **Dependence**: Non-linear feature effects
- **Triangulation**: Built-in vs Permutation vs SHAP importance

### ✅ Fairness Audit
- Subgroup analysis across gender, senior citizen status
- Equal opportunity metrics

### ✅ Deployment Ready
- Serialized pipeline (`joblib`)
- Model card (JSON)
- Inference API
- Drift monitoring

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.9+ |
| ML Models | XGBoost, LightGBM, CatBoost, Scikit-learn |
| Tuning | Optuna (TPE Sampler + MedianPruner) |
| Imbalance | imbalanced-learn (SMOTE, ImbPipeline) |
| Explainability | SHAP |
| Calibration | Scikit-learn CalibratedClassifierCV |
| Chatbot UI | Streamlit |
| Stats | SciPy (Mann-Whitney U, Chi-square, Cramér's V) |
| Serialization | Joblib |

---

## 📁 Project Structure

```
telco-churn-prediction/
│
├── 📓 CHURN_FINAL_v5_MERGED.ipynb   # Full ML pipeline (16 sections)
├── 🤖 chatbot.py                     # Streamlit prediction chatbot
├── 📋 requirements.txt               # All dependencies
├── 📊 WA_Fn-UseC_-Telco-Customer-Churn.csv  # Dataset
├── 📄 CHURN_MODEL_.pdf               # Exported notebook with outputs
│
└── 📂 artifacts/  (generated after running notebook)
    ├── churn_model_<timestamp>.pkl   # Trained pipeline
    ├── model_card.json               # Model documentation
    ├── shap_global_bar.png           # SHAP importance plot
    ├── shap_beeswarm.png             # SHAP beeswarm plot
    ├── calibration_reliability.png   # Calibration curves
    └── ...more plots
```

---

## 🚀 How to Run

### Step 1 — Clone the Repository
```bash
git clone https://github.com/CHIRAGKUMAR1718/telco-churn-prediction.git
cd telco-churn-prediction
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Train the Model
Open and run all cells in:
```
CHURN_FINAL_v5_MERGED.ipynb
```
This generates the trained model in `artifacts/` folder.

### Step 4 — Update Model Path in chatbot.py
```python
# Line 10 in chatbot.py
MODEL_PATH = r"your\full\path\to\artifacts\churn_model_<timestamp>.pkl"
THRESHOLD  = 0.22  # Change as needed (0.0 to 1.0)
```

### Step 5 — Launch the Chatbot
```bash
streamlit run chatbot.py
```

Browser automatically opens at `http://localhost:8501` 🎉

---

## 🤖 Chatbot Features

The Streamlit chatbot provides a **conversational interface** to the trained model:

- 💬 Asks **19 questions** about a customer — one at a time
- 🔘 Provides **clickable option buttons** for easy input
- 📊 Shows **real-time progress bar**
- 🎯 Predicts **Churn Probability** with confidence
- 💡 Generates **AI explanation paragraph** — *why* the model predicted this
- 📋 Displays **customer summary table**
- 🔄 Supports **multiple predictions** in one session

---

## 📈 Model Comparison

| Model | ROC-AUC | Precision | Recall | F1 | EV/User |
|-------|---------|-----------|--------|----|---------|
| Single Best (cal) | 0.8452 | 0.5179 | **0.8250** | **0.6364** | $0.1547 |
| Soft Voting (cal) | 0.8469 | **0.5445** | 0.7643 | 0.6360 | $0.1374 |
| Stacking (cal) | **0.8503** | 0.5369 | 0.7786 | 0.6356 | $0.1413 |

> 🏆 **Winner by F1:** Single Best (Calibrated)

---

## 📐 Feature Engineering

12 domain-driven features engineered from raw data:

| Feature | Description |
|---------|-------------|
| `TenureGroup` | Bucketed tenure (0-6m, 6-12m, 12-24m, 24-48m, 48m+) |
| `IsNewCustomer` | Binary flag for tenure ≤ 6 months |
| `AvgMonthlySpend` | TotalCharges / (tenure + 1) |
| `SpendRatio` | MonthlyCharges vs historical average |
| `SpendAcceleration` | Current vs avg spend delta |
| `NumServices` | Count of active add-on services |
| `HasProtectionBundle` | OnlineSecurity AND DeviceProtection |
| `HasStreamingBundle` | StreamingTV AND StreamingMovies |
| `ContractRiskScore` | Month-to-month=3, One year=1, Two year=0 |
| `HighRiskPayment` | Electronic check = 1 |
| `FamilyStability` | Has Partner OR Dependents |
| `IsFiberCustomer` | Fiber optic internet flag |

---

## 📉 Key Business Insights

1. **Contract type** is the #1 churn driver — month-to-month customers churn at 3× the rate of 2-year contract customers
2. **New customers** (tenure ≤ 6 months) are extremely high risk
3. **Electronic check** payment method strongly correlates with churn
4. **Fiber optic** customers churn more despite paying premium prices
5. **Low service engagement** (few add-ons) = higher churn risk

---

## 👨‍💻 Author

**Chirag Kumar**
- GitHub: [@CHIRAGKUMAR1718](https://github.com/CHIRAGKUMAR1718)

<p align="center">⭐ Star this repo if you found it useful!</p>
