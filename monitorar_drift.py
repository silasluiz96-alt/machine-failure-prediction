"""
Simulação de detecção de drift nos dados de entrada da API.

Compara a distribuição de "novos dados" com a distribuição usada no treinamento.
Em produção, os "novos dados" seriam as requisições reais recebidas pela API
nos últimos 30 dias.

Execute:
    python monitorar_drift.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "manutencao_preditiva.csv"

FEATURES_NUMERICAS = [
    "Temperatura Ar [K]",
    "Temperatura Processo [K]",
    "Velocidade Rotacao [rpm]",
    "Torque [Nm]",
    "Desgaste Ferramenta [min]",
]

LIMITE_DESVIO = 0.15  # 15% de desvio dispara alerta

# ------------------------------------------------------------------ #
# Distribuição de treinamento (dados reais do dataset)
# ------------------------------------------------------------------ #
df = pd.read_csv(CSV_PATH)
distribuicao_treino = df[FEATURES_NUMERICAS].agg(["mean", "std"])

# ------------------------------------------------------------------ #
# Simulação de "novos dados" recebidos pela API
# Cenário 1: dados normais — sem drift
# Cenário 2: drift simulado — torque e temperatura mais altos
# ------------------------------------------------------------------ #
np.random.seed(99)
n = 500  # simulando 500 requisições dos últimos 30 dias

dados_normais = pd.DataFrame({
    "Temperatura Ar [K]":       np.random.normal(300.0, 2.0, n),
    "Temperatura Processo [K]": np.random.normal(310.2, 1.5, n),
    "Velocidade Rotacao [rpm]": np.random.normal(1538.8, 179.0, n),
    "Torque [Nm]":              np.random.normal(39.9, 10.0, n),
    "Desgaste Ferramenta [min]":np.random.normal(107.9, 63.7, n),
})

dados_com_drift = pd.DataFrame({
    "Temperatura Ar [K]":       np.random.normal(310.0, 2.0, n),   # +10 K — novo ambiente
    "Temperatura Processo [K]": np.random.normal(325.0, 1.5, n),   # +15 K — processo mais quente
    "Velocidade Rotacao [rpm]": np.random.normal(1538.8, 179.0, n),
    "Torque [Nm]":              np.random.normal(65.0, 10.0, n),    # +25 Nm — novo equipamento
    "Desgaste Ferramenta [min]":np.random.normal(107.9, 63.7, n),
})


def verificar_drift(novos_dados: pd.DataFrame, nome_cenario: str):
    print(f"\n{'='*60}")
    print(f"CENÁRIO: {nome_cenario}")
    print(f"{'='*60}")
    print(f"{'Feature':<30} {'Treino':>10} {'Atual':>10} {'Desvio':>10} {'Status':>10}")
    print("-" * 65)

    alertas = []
    for feature in FEATURES_NUMERICAS:
        media_treino = distribuicao_treino.loc["mean", feature]
        media_atual  = novos_dados[feature].mean()
        desvio       = abs(media_atual - media_treino) / media_treino

        status = "✓ OK" if desvio <= LIMITE_DESVIO else "⚠ ALERTA"
        if desvio > LIMITE_DESVIO:
            alertas.append(feature)

        print(f"{feature:<30} {media_treino:>10.2f} {media_atual:>10.2f} {desvio*100:>9.1f}% {status:>10}")

    print()
    if alertas:
        print(f"⚠  DRIFT DETECTADO em {len(alertas)} feature(s):")
        for f in alertas:
            print(f"   → {f}")
        print("\n   Ação recomendada: avaliar retreinamento do modelo.")
        print("   Consulte DRIFT_MONITORING.md para o plano completo.")
    else:
        print("✓  Nenhum drift detectado. Modelo dentro da faixa esperada.")


# Rodar os dois cenários
verificar_drift(dados_normais, "Dados normais — sem drift")
verificar_drift(dados_com_drift, "Dados com drift — novo equipamento simulado")

print(f"\n{'='*60}")
print("Limite de alerta configurado: desvio > 15% da média de treinamento")
print("Documentação: DRIFT_MONITORING.md")
print(f"{'='*60}\n")
