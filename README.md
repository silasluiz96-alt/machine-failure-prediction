# 🔧 Machine Failure Prediction Pipeline — Metal-Mechanical Industry

> **Associated with peer-reviewed publication:**
> *Integration of Data Analytics and Data Mining for Machine Failure Mitigation and Decision Support in Metal–Mechanical Industry*
> **Logistics, Vol. 9, Issue 3, Art. 109 · MDPI · 2025 · Open Access**
> 🔗 [doi.org/10.3390/logistics9030109](https://doi.org/10.3390/logistics9030109)

---

## 📌 Overview

This project implements a complete **end-to-end machine learning pipeline** for predictive maintenance in the metal-mechanical industry. The goal is to predict machine failures before they occur, enabling proactive maintenance and reducing unplanned downtime.

The pipeline was developed as part of an applied research project at the **Federal University of ABC (UFABC)** in partnership with industrial partners, resulting in a peer-reviewed scientific publication.

---

## 🎯 Problem Statement

Unexpected machine failures in metal-mechanical production environments cause:
- High operational costs from unplanned downtime
- Delayed deliveries and compromised product quality
- Inefficient corrective and preventive maintenance strategies

This project proposes a **data-driven framework** combining Data Analytics (DA) and Data Mining (DM) to anticipate failures and support decision-making.

---

## 🏗️ Pipeline Architecture

The solution is structured in 4 stages:

```
Raw Data → Data Analytics → Preprocessing → Data Mining → Interpretation
```

### Stage 1 — Exploratory Data Analytics
- Univariate analysis of failure type distribution
- Bivariate analysis identifying failure signatures
- Correlation matrices per failure mode
- Visualization: histograms, boxplots, scatterplots

### Stage 2 — Preprocessing
- **Data cleaning**: outlier removal using IQR method
- **Categorical encoding**: Label Encoding for product type features
- **Feature selection**: Minimum Redundancy Maximum Relevance (mRMR)
- **Class balancing**: SMOTE (Synthetic Minority Over-Sampling Technique)

### Stage 3 — Data Mining & Model Training
- Decision Tree (CART algorithm) — primary model
- Random Forest
- MLP (Multilayer Perceptron Neural Network)
- SVM (Support Vector Machine)
- Hyperparameter tuning via **Grid Search with k-fold cross-validation (k=5)**

### Stage 4 — Evaluation & Interpretation
- Accuracy and **Kappa index** (corrects for class imbalance)
- Confusion matrices per model
- Composite ranking: F1 (40%), Recall (30%), Precision (20%), AUC (10%)
- Decision rules extraction for operational use

---

## 📊 Results

| Model | Accuracy | Kappa Index |
|---|---|---|
| **Decision Tree** | **82.1%** | **0.785** |
| Random Forest | — | — |
| MLP | — | — |
| SVM | — | — |

The Decision Tree was selected as the primary model for its balance between **performance and interpretability** — enabling maintenance managers to understand and apply the generated decision rules directly on the shop floor.

**Example decision rule generated:**
> IF `Process Temperature > 309.80 K` AND `Tool Wear ≤ 186.50` AND `Rotation Speed ≤ 1378.50` THEN → **Heat Dissipation Failure**

---

## 📂 Dataset

- **Source:** AI4I 2020 Predictive Maintenance Dataset — [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)
- **Size:** 10,000 records with 6 failure types
- **Features:** Air Temperature, Process Temperature, Rotation Speed, Torque, Tool Wear, Product Type
- **Target:** Failure Type (multiclass)
- **Class imbalance:** 96.52% no failure / 3.48% failure events

---

## 🛠️ Tech Stack

```python
pandas · numpy · matplotlib · seaborn          # Data handling & visualization
scikit-learn                                    # ML models, GridSearchCV, SMOTE
imblearn (imbalanced-learn)                     # SMOTE for class balancing
```

---

## 🚀 How to Run

1. Open the notebook in **Google Colab** (recommended) or Jupyter
2. Download the dataset from [UCI Repository](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)
3. Upload the CSV file when prompted
4. Run all cells in order — the pipeline is fully sequential

```bash
# If running locally
pip install pandas numpy matplotlib seaborn scikit-learn imbalanced-learn
```

---

## 📄 Citation

If you use this code or reference this work, please cite:

```bibtex
@article{araujo2025integration,
  title={Integration of Data Analytics and Data Mining for Machine Failure
         Mitigation and Decision Support in Metal–Mechanical Industry},
  author={Araujo, Sidnei A. and Bomfim, Silas L. and Boukouvalas, Dimitria T.
          and Lourenço, Sergio R. and Ibusuki, Ugo and Oliveira Neto, Geraldo C.},
  journal={Logistics},
  volume={9},
  number={3},
  pages={109},
  year={2025},
  publisher={MDPI},
  doi={10.3390/logistics9030109}
}
```

---

## 👤 Author Contribution

**Silas Luiz Bom Fim** — Software implementation and Data Visualization
- Full Python pipeline development (preprocessing, SMOTE, mRMR, CART via scikit-learn)
- Data visualization (Matplotlib/Seaborn): histograms, boxplots, correlation matrices, confusion matrices

---

## 🔗 Links

- 📄 [Full Paper (Open Access)](https://doi.org/10.3390/logistics9030109)
- 💼 [LinkedIn](https://www.linkedin.com/in/silas-luiz-bom-fim-96a448176)
- 🐙 [GitHub Profile](https://github.com/silasluiz96-alt)
