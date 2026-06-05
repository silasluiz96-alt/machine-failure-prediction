# Machine Failure Prediction API

[![API Status](https://img.shields.io/badge/API-Online-green)](https://machine-failure-prediction-production.up.railway.app)

**Live API:** https://machine-failure-prediction-production.up.railway.app/docs

API REST para predição de falhas em máquinas industriais, construída com **FastAPI** e **Random Forest**.

---

## Estrutura do projeto

```
MachineFailure/
├── api/
│   ├── main.py          ← endpoints FastAPI
│   ├── model.py         ← treino e serialização do modelo
│   └── schemas.py       ← validação de entrada/saída (Pydantic)
├── model/
│   ├── model.pkl        ← Random Forest treinado
│   ├── scaler.pkl       ← StandardScaler
│   └── metadata.pkl     ← métricas e configurações
├── manutencao_preditiva.csv
├── requirements_api.txt
└── README_API.md
```

---

## Instalação

```bash
# 1. Criar e ativar ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 2. Instalar dependências
pip install -r requirements_api.txt
```

---

## Uso

### Passo 1 — Treinar o modelo

Execute **uma única vez** para gerar os arquivos em `model/`:

```bash
# A partir da pasta MachineFailure/
python api/model.py
```

Saída esperada:
```
[1/6] Carregando dados...
[2/6] Codificando variável 'Tipo'...
[3/6] Removendo outliers (IQR)...
[4/6] Balanceando classes com SMOTE...
[5/6] Dividindo treino/teste e normalizando...
[6/6] Treinando Random Forest...
      Accuracy : 0.9754
      F1-Score : 0.9754
      ROC-AUC  : 0.9972
✓ Modelo salvo em: model/model.pkl
```

### Passo 2 — Iniciar a API

```bash
# A partir da pasta MachineFailure/
uvicorn api.main:app --reload
```

A API fica disponível em: **http://127.0.0.1:8000**

Documentação interativa: **http://127.0.0.1:8000/docs**

---

## Endpoints

### `GET /` — Informações do modelo

```bash
curl http://127.0.0.1:8000/
```

```json
{
  "name": "Random Forest — Predição de Falhas",
  "version": "1.0.0",
  "accuracy": 0.9754,
  "features": ["Temperatura Ar [K]", "..."],
  "description": "..."
}
```

---

### `GET /health` — Status da API

```bash
curl http://127.0.0.1:8000/health
```

```json
{
  "status": "ok",
  "model_loaded": true
}
```

---

### `POST /predict` — Predição individual

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Temperatura Ar [K]": 298.1,
    "Temperatura Processo [K]": 308.6,
    "Velocidade Rotacao [rpm]": 1551,
    "Torque [Nm]": 42.8,
    "Desgaste Ferramenta [min]": 0,
    "Tipo": "M"
  }'
```

```json
{
  "prediction": 0,
  "probability_failure": 0.04,
  "risk_level": "LOW",
  "message": "Máquina operando normalmente"
}
```

---

### `POST /predict/batch` — Predição em lote

```bash
curl -X POST http://127.0.0.1:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "machines": [
      {
        "Temperatura Ar [K]": 298.1,
        "Temperatura Processo [K]": 308.6,
        "Velocidade Rotacao [rpm]": 1551,
        "Torque [Nm]": 42.8,
        "Desgaste Ferramenta [min]": 0,
        "Tipo": "M"
      },
      {
        "Temperatura Ar [K]": 310.0,
        "Temperatura Processo [K]": 315.0,
        "Velocidade Rotacao [rpm]": 2800,
        "Torque [Nm]": 70.0,
        "Desgaste Ferramenta [min]": 250,
        "Tipo": "L"
      }
    ]
  }'
```

```json
{
  "predictions": [
    {
      "prediction": 0,
      "probability_failure": 0.04,
      "risk_level": "LOW",
      "message": "Máquina operando normalmente"
    },
    {
      "prediction": 1,
      "probability_failure": 0.87,
      "risk_level": "HIGH",
      "message": "Alerta: alto risco de falha — manutenção recomendada"
    }
  ],
  "total": 2,
  "failures_detected": 1
}
```

---

## Níveis de risco

| probability_failure | risk_level | Mensagem |
|---|---|---|
| < 0.30 | LOW | Máquina operando normalmente |
| 0.30 – 0.60 | MEDIUM | Atenção: risco moderado de falha |
| > 0.60 | HIGH | Alerta: alto risco de falha — manutenção recomendada |

---

## Parâmetros de entrada

| Campo | Tipo | Intervalo válido | Descrição |
|---|---|---|---|
| Temperatura Ar [K] | float | 290 – 320 | Temperatura do ar em Kelvin |
| Temperatura Processo [K] | float | 300 – 320 | Temperatura do processo em Kelvin |
| Velocidade Rotacao [rpm] | float | 1000 – 3000 | Rotações por minuto |
| Torque [Nm] | float | 0 – 100 | Torque em Newton-metro |
| Desgaste Ferramenta [min] | float | 0 – 300 | Desgaste acumulado da ferramenta |
| Tipo | string | L, M ou H | Categoria do produto |

---

## Pipeline do modelo

1. Remoção de outliers usando o método IQR (intervalo interquartil)
2. Balanceamento de classes com **SMOTE** (de 2.8% → 50% de falhas)
3. Divisão treino/teste: **70% / 30%**
4. Normalização com **StandardScaler**
5. **Random Forest** com 100 árvores e hiperparâmetros otimizados por Grid Search
