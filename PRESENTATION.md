# Telco Customer Churn Prediction
### End-to-End Production-Grade Machine Learning Pipeline

---

## 1. Business Problem

Telecom companies lose **$500 in customer lifetime value** for every missed churner — yet a false alarm costs only **$50** in wasted retention offers.

```
Cost Asymmetry:  False Negative (missed churner) = $500
                 False Positive (wrong alarm)    =  $50
                 Ratio                           =  10 : 1
```

> **Goal:** Build a model that maximizes **Recall** — catching as many real churners as possible — while remaining profitable via Expected Value optimization.

| Business Metric | Value |
|---|---|
| Dataset size | 7,043 customers |
| Churn rate | ~26.5% |
| Avg. monthly revenue / customer | $64.76 |
| Retention success rate | 30% |

---

## 2. Pipeline Architecture

```mermaid
flowchart TD
    A[Raw CSV\n7043 customers] --> B[Data Validation\nSchema · Nulls · PK check]
    B --> C[Feature Engineering\n12 domain features]
    C --> D[Stratified 3-Way Split\nTrain 70% · Val 15% · Test 15%]
    D --> E[Baseline Ladder\nLR → RF → XGB → LGBM → CatBoost]
    E --> F[Optuna Hyperparameter Tuning\n200 trials · TPE Sampler · AP objective\nSMOTE inside CV folds only]
    F --> G[Ensembling\nStacking · Soft Voting · Single Best]
    G --> H[Probability Calibration\nIsotonic Regression · Reliability Diagrams]
    H --> I[Threshold Selection\nPR-curve max-F1 · Business EV]
    I --> J[Evaluation\nROC · PR · Lift · KS · Brier · Fairness]
    J --> K[SHAP Explainability\nGlobal · Local · Dependence · Waterfall]
    K --> L[Deployment\nJoblib · Model Card · Inference API · Drift Monitor]
    L --> M[Streamlit Chatbot\nAI-powered predictions + explanations]

    style A fill:#1a2a4a,color:#adf
    style M fill:#1a3a1a,color:#adf
    style F fill:#3a2a1a,color:#fda
    style K fill:#2a1a3a,color:#daf
```

---

## 3. Feature Engineering

12 domain-driven features engineered from raw data:

```mermaid
graph LR
    subgraph RAW["Raw Features"]
        R1[tenure]
        R2[MonthlyCharges]
        R3[TotalCharges]
        R4[Contract]
        R5[PaymentMethod]
        R6[InternetService]
        R7[Partner / Dependents]
        R8[Add-on Services x6]
    end

    subgraph ENG["Engineered Features"]
        E1[TenureGroup\n0-6m · 6-12m · 12-24m · 24-48m · 48m+]
        E2[IsNewCustomer\ntenure ≤ 6 months]
        E3[AvgMonthlySpend\nTotalCharges / tenure+1]
        E4[SpendRatio\nMonthly vs Historical]
        E5[SpendAcceleration\nCurrent - Avg spend]
        E6[NumServices\nCount of active add-ons]
        E7[HasProtectionBundle\nSecurity AND DeviceProtection]
        E8[HasStreamingBundle\nTV AND Movies]
        E9[ContractRiskScore\nM-t-M=3 · 1yr=1 · 2yr=0]
        E10[HighRiskPayment\nElectronic check = 1]
        E11[FamilyStability\nPartner OR Dependents]
        E12[IsFiberCustomer\nFiber optic = 1]
    end

    R1 --> E1 & E2 & E3 & E5
    R2 --> E4 & E5
    R3 --> E3
    R4 --> E9
    R5 --> E10
    R6 --> E12
    R7 --> E11
    R8 --> E6 & E7 & E8
```

---

## 4. Imbalance Handling Strategy

**Class ratio:** 73% No Churn : 27% Churn

```mermaid
flowchart LR
    A[Imbalanced Data\n73:27] --> B{Strategy}
    B --> C[SMOTE\nSynthetic oversampling\ninside CV folds only\nno data leakage]
    B --> D[Class Weights\nApplied to all estimators]
    B --> E[Threshold Tuning\nOptimized via business EV\nnot fixed at 0.5]
    C & D & E --> F[Final Threshold = 0.22\nMaximizes Recall\nfor 10:1 cost ratio]
```

> SMOTE is applied **inside** `ImbPipeline` during cross-validation only — never on the held-out test set.

---

## 5. Hyperparameter Tuning — Optuna

```mermaid
flowchart TD
    A[Optuna Study\n200 Trials] --> B[TPE Sampler\nBayesian search]
    A --> C[Median Pruner\nEarly stopping of bad trials]
    B & C --> D[Objective: Average Precision\nimbalance-aware · better than ROC-AUC]
    D --> E[RepeatedStratifiedKFold\n5 folds × 2 repeats = 10 evals]
    E --> F[fANOVA\nHyperparameter importance ranking]
    F --> G[Best Hyperparameters\nper model]
```

---

## 6. Model Comparison

| Model | ROC-AUC | Precision | Recall | F1 | EV / User |
|---|---|---|---|---|---|
| Single Best (Calibrated) | 0.8452 | 0.5179 | **0.8250** | **0.6364** | $0.1547 |
| Soft Voting (Calibrated) | 0.8469 | **0.5445** | 0.7643 | 0.6360 | $0.1374 |
| Stacking (Calibrated) | **0.8503** | 0.5369 | 0.7786 | 0.6356 | $0.1413 |

```mermaid
xychart-beta
    title "Model Performance Comparison"
    x-axis ["ROC-AUC", "Recall", "F1 Score", "Precision"]
    y-axis "Score" 0 --> 1
    bar [0.8452, 0.8250, 0.6364, 0.5179]
    bar [0.8469, 0.7643, 0.6360, 0.5445]
    bar [0.8503, 0.7786, 0.6356, 0.5369]
```

> **Winner: Single Best (Calibrated)** — highest Recall (0.825) and F1 (0.6364), best Expected Value per user ($0.15)

---

## 7. Final Model Metrics

```
┌─────────────────────────────────────────────┐
│           PRODUCTION MODEL SCORECARD        │
├──────────────────────┬──────────────────────┤
│  ROC-AUC             │  0.8503              │
│  Average Precision   │  0.6419              │
│  Recall              │  0.825               │
│  F1 Score            │  0.636               │
│  MCC                 │  0.490               │
│  Brier Score         │  0.134               │
│  Expected Value/User │  $0.15               │
│  Total Test-Set EV   │  $164                │
│  Production Threshold│  0.22                │
│  Test Set Size       │  1,057 customers     │
└──────────────────────┴──────────────────────┘
```

---

## 8. SHAP Explainability

```mermaid
mindmap
  root((SHAP\nExplainability))
    Global
      Feature importance bar chart
      Beeswarm plot
      Permutation importance triangulation
    Local
      Waterfall plot per customer
      Force plot visualization
    Dependence
      Non-linear feature effects
      Interaction effects
    Triangulation
      Built-in importance
      Permutation importance
      SHAP importance
```

**Top churn drivers identified by SHAP:**

1. `ContractRiskScore` — month-to-month customers churn 3× more than 2-year
2. `IsNewCustomer` — tenure ≤ 6 months = extremely high risk
3. `HighRiskPayment` — electronic check strongly correlates with churn
4. `IsFiberCustomer` — fiber optic customers churn despite paying premium
5. `NumServices` — low add-on engagement = higher churn probability

---

## 9. Probability Calibration

```mermaid
flowchart LR
    A[Raw Model\nUncalibrated Probabilities] -->|Isotonic Regression\non held-out val set| B[Calibrated Model\nReliable Probabilities]
    B --> C[Reliability Diagram\npre vs post calibration]
    B --> D[Brier Score Improvement\ntracked and reported]
    B --> E[Expected Value Calculation\nbusiness-meaningful threshold]
```

> Calibration ensures that a predicted 70% probability truly means the customer churns 70% of the time — critical for business decision-making.

---

## 10. Fairness Audit

```mermaid
flowchart TD
    A[Trained Model] --> B[Subgroup Analysis]
    B --> C[Gender\nMale vs Female]
    B --> D[Age\nSenior Citizens vs Non-Senior]
    C & D --> E[Equal Opportunity Metrics\nRecall parity across groups]
    E --> F[Fairness Report\nno significant bias detected]
```

---

## 11. Deployment Architecture

```mermaid
flowchart TD
    A[Trained Pipeline\nchurn_model.pkl via joblib] --> B[Inference API\npredict_proba]
    A --> C[Model Card JSON\ndocumentation + metadata]
    A --> D[Drift Monitor\nfeature distribution tracking]
    B --> E[Streamlit Chatbot\nchatbot.py]
    E --> F[19-Question Conversation\none question at a time]
    F --> G[Feature Engineering\nengineer_features]
    G --> B
    B --> H[Churn Probability\nvs threshold 0.22]
    H --> I[Claude API\nAI explanation paragraph]
    H & I --> J[Business Output\nPredict · Explain · Act]

    style E fill:#1a2a4a,color:#adf
    style J fill:#1a3a1a,color:#adf
```

---

## 12. Chatbot Interface

The Streamlit chatbot provides a **conversational prediction interface**:

```
┌──────────────────────────────────────────────────┐
│          Churn Prediction Chatbot                │
│                                                  │
│  Bot: What is the customer's Contract type?      │
│       ┌─────────────┐ ┌──────────┐ ┌──────────┐ │
│       │Month-to-month│ │ One year │ │ Two year │ │
│       └─────────────┘ └──────────┘ └──────────┘ │
│                                                  │
│  ████████████████░░░░  Question 15/19            │
│                                                  │
│  ⚠️ PREDICTION: HIGH CHURN RISK                 │
│           73.4% Churn Probability                │
│                                                  │
│  💡 This customer has a 73.4% probability of     │
│  churning, driven primarily by their             │
│  month-to-month contract and short tenure...     │
└──────────────────────────────────────────────────┘
```

**Features:**
- 19 guided questions with clickable option buttons
- Real-time progress bar
- Churn probability with color-coded result card
- AI-generated explanation paragraph (Claude API)
- Customer summary table
- Supports multiple predictions per session

---

## 13. Tech Stack

```mermaid
graph TD
    subgraph DATA["Data & ML"]
        D1[pandas · numpy]
        D2[scikit-learn]
        D3[XGBoost · LightGBM · CatBoost]
        D4[imbalanced-learn\nSMOTE · ImbPipeline]
        D5[Optuna\nTPE · MedianPruner]
        D6[SHAP]
        D7[SciPy\nMann-Whitney · Chi-square · Cramér's V]
    end
    subgraph DEPLOY["Deployment & UI"]
        P1[Streamlit]
        P2[Joblib serialization]
        P3[Claude API\nsonnet-4-20250514]
    end
    subgraph INFRA["Infrastructure"]
        I1[Python 3.9+]
        I2[Jupyter Notebook]
        I3[Git]
    end
```

---

## 14. Key Takeaways

| Aspect | Decision | Reason |
|---|---|---|
| Metric optimized | Average Precision | Better than ROC-AUC for imbalanced data |
| SMOTE placement | Inside CV folds only | Prevents data leakage |
| CV strategy | RepeatedStratifiedKFold (5×2) | Lower variance, preserves class ratio |
| Calibration method | Isotonic Regression | Better than Platt scaling for larger datasets |
| Threshold | 0.22 (not 0.5) | 10:1 cost asymmetry demands high Recall |
| Winner model | Single Best Calibrated | Highest Recall + F1 + EV per user |
| Explainability | SHAP (global + local) | Actionable business insights per customer |

---

*Dataset: IBM Telco Customer Churn · Model trained 2026-04-18 · Threshold: 0.22 · Test set: 1,057 customers*
