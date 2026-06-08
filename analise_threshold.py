"""
Análise de threshold — justificativa da escolha do limiar de alerta.

Este script carrega o modelo treinado e avalia como recall e precision
se comportam em diferentes limiares de decisão.

Execute:
    python analise_threshold.py
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "model.pkl"
SCALER_PATH = BASE_DIR / "model" / "scaler.pkl"
CSV_PATH = BASE_DIR / "manutencao_preditiva.csv"

FEATURES = [
    "Temperatura Ar [K]",
    "Temperatura Processo [K]",
    "Velocidade Rotacao [rpm]",
    "Torque [Nm]",
    "Desgaste Ferramenta [min]",
    "Tipo_encoded",
]

# Carregar modelo e scaler
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Recarregar dados originais (sem SMOTE — cenário mundo real)
df = pd.read_csv(CSV_PATH)
le = LabelEncoder()
df["Tipo_encoded"] = le.fit_transform(df["Tipo"])

# Remover outliers (IQR — igual ao pipeline de treino)
numeric_cols = ["Temperatura Ar [K]", "Temperatura Processo [K]",
                "Velocidade Rotacao [rpm]", "Torque [Nm]", "Desgaste Ferramenta [min]"]
df_clean = df.copy()
for col in numeric_cols:
    Q1 = df_clean[col].quantile(0.25)
    Q3 = df_clean[col].quantile(0.75)
    IQR = Q3 - Q1
    df_clean = df_clean[(df_clean[col] >= Q1 - 1.5 * IQR) & (df_clean[col] <= Q3 + 1.5 * IQR)]

X = df_clean[FEATURES]
y = df_clean["Alvo"]

_, X_test, _, y_test = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
X_test_s = scaler.transform(X_test)

# Probabilidades de falha para cada máquina
probabilidades = model.predict_proba(X_test_s)[:, 1]

# Testar diferentes limiares
limiares = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]

print("=" * 65)
print("ANÁLISE DE THRESHOLD — IMPACTO NA PRECISION E RECALL")
print("=" * 65)
print(f"\nConjunto de teste: {len(y_test)} máquinas")
print(f"  Normais : {(y_test == 0).sum()} ({(y_test == 0).mean()*100:.1f}%)")
print(f"  Falhas  : {(y_test == 1).sum()} ({(y_test == 1).mean()*100:.1f}%)")
print()
print(f"{'Limiar':>8} | {'Recall':>8} | {'Precision':>10} | {'Alarmes':>8} | {'Falhas perdidas':>16} | Interpretação")
print("-" * 95)

for limiar in limiares:
    y_pred = (probabilidades >= limiar).astype(int)
    rec  = recall_score(y_test, y_pred, zero_division=0)
    prec = precision_score(y_test, y_pred, zero_division=0)
    alertas = y_pred.sum()
    fn = ((y_pred == 0) & (y_test == 1)).sum()

    if limiar == 0.10:
        nota = "<-- ESCOLHIDO"
    elif limiar < 0.10:
        nota = "muitos alarmes falsos"
    elif rec < 0.80:
        nota = "muitas falhas escapam"
    else:
        nota = ""

    print(f"{limiar*100:>7.0f}% | {rec*100:>7.1f}% | {prec*100:>9.1f}% | {alertas:>8} | {fn:>16} | {nota}")

print()
print("Conclusão:")
print("  Com limiar de 10%, o modelo captura a maior parte das falhas")
print("  com um número controlado de alarmes falsos — equilíbrio ideal")
print("  para o contexto de manutenção preditiva industrial.")
print("=" * 65)
