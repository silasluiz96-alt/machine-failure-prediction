# Machine Failure Prediction API

[![API Status](https://img.shields.io/badge/API-Online-green)](https://machine-failure-prediction-production-22fe.up.railway.app)

**Live API:** https://machine-failure-prediction-production-22fe.up.railway.app/docs

API REST para predição de falhas em máquinas industriais, construída com **FastAPI** e **Random Forest**. Deployada em produção no Railway.

---

## Endpoints disponíveis

| Método | Endpoint | O que faz |
|---|---|---|
| GET | `/` | Ficha técnica do modelo: nome, versão, accuracy, features |
| GET | `/health` | Verifica se a API está no ar e o modelo carregado |
| GET | `/metrics` | Métricas de desempenho do modelo treinado |
| POST | `/predict` | Predição individual de uma máquina |
| POST | `/predict/batch` | Predição de várias máquinas de uma vez |
| POST | `/predict/explain` | Predição com explicação dos fatores que influenciaram a decisão |

---

## Parâmetros de entrada

Todos os endpoints de predição recebem os mesmos 6 campos:

| Campo | Tipo | Intervalo válido | Descrição |
|---|---|---|---|
| Temperatura Ar [K] | float | 290 – 320 | Temperatura do ambiente em Kelvin |
| Temperatura Processo [K] | float | 300 – 320 | Temperatura da operação em Kelvin |
| Velocidade Rotacao [rpm] | float | 1000 – 3000 | Rotações por minuto |
| Torque [Nm] | float | 0 – 100 | Força de rotação em Newton-metro |
| Desgaste Ferramenta [min] | float | 0 – 300 | Tempo acumulado de uso da ferramenta |
| Tipo | string | L, M ou H | Categoria do produto (Low, Medium, High) |

---

## Escala de risco industrial

A escala foi definida com base em critérios de manutenção preditiva para indústria metal-mecânica. Qualquer probabilidade acima de 10% já é considerada um sinal de atenção.

| Probabilidade de falha | Risk Level | Ação recomendada |
|---|---|---|
| < 10% | `LOW` | Máquina operando normalmente |
| 10% – 30% | `MEDIUM` | Monitorar: probabilidade de falha em crescimento |
| 30% – 60% | `HIGH` | Agendar manutenção preventiva imediatamente |
| > 60% | `CRITICAL` | Parar a máquina — alto risco de falha iminente |

---

## Exemplos reais

### `GET /` — Ficha técnica do modelo

```json
{
  "name": "Random Forest — Predição de Falhas",
  "version": "1.0.0",
  "accuracy": 0.9752,
  "features": [
    "Temperatura Ar [K]",
    "Temperatura Processo [K]",
    "Velocidade Rotacao [rpm]",
    "Torque [Nm]",
    "Desgaste Ferramenta [min]",
    "Tipo_encoded"
  ],
  "description": "Modelo treinado com Random Forest (100 árvores) sobre dados de sensores industriais."
}
```

---

### `GET /health` — Status da API

```json
{
  "status": "ok",
  "model_loaded": true
}
```

---

### `GET /metrics` — Métricas do modelo

```json
{
  "accuracy": 0.9752,
  "f1": 0.9754,
  "roc_auc": 0.998,
  "model": "Random Forest",
  "trees": 100
}
```

---

### `POST /predict` — Predição individual

**Máquina saudável:**
```json
{
  "Temperatura Ar [K]": 298.1,
  "Temperatura Processo [K]": 308.6,
  "Velocidade Rotacao [rpm]": 1551,
  "Torque [Nm]": 42.8,
  "Desgaste Ferramenta [min]": 0,
  "Tipo": "M"
}
```
Resposta:
```json
{
  "prediction": 0,
  "probability_failure": 0.0,
  "risk_level": "LOW",
  "message": "Máquina operando normalmente"
}
```

**Máquina em risco:**
```json
{
  "Temperatura Ar [K]": 310,
  "Temperatura Processo [K]": 315,
  "Velocidade Rotacao [rpm]": 1200,
  "Torque [Nm]": 90,
  "Desgaste Ferramenta [min]": 280,
  "Tipo": "L"
}
```
Resposta:
```json
{
  "prediction": 0,
  "probability_failure": 0.37,
  "risk_level": "HIGH",
  "message": "Agendar manutenção preventiva imediatamente"
}
```

---

### `POST /predict/batch` — Predição em lote

```json
{
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
      "Temperatura Ar [K]": 310,
      "Temperatura Processo [K]": 315,
      "Velocidade Rotacao [rpm]": 1200,
      "Torque [Nm]": 90,
      "Desgaste Ferramenta [min]": 280,
      "Tipo": "L"
    }
  ]
}
```
Resposta:
```json
{
  "predictions": [
    {
      "prediction": 0,
      "probability_failure": 0.0,
      "risk_level": "LOW",
      "message": "Máquina operando normalmente"
    },
    {
      "prediction": 0,
      "probability_failure": 0.37,
      "risk_level": "HIGH",
      "message": "Agendar manutenção preventiva imediatamente"
    }
  ],
  "total": 2,
  "failures_detected": 1
}
```

> `failures_detected` conta todas as máquinas com probabilidade ≥ 10%, não apenas as com `prediction: 1`.

---

### `POST /predict/explain` — Predição com explicação

```json
{
  "Temperatura Ar [K]": 310,
  "Temperatura Processo [K]": 315,
  "Velocidade Rotacao [rpm]": 1200,
  "Torque [Nm]": 90,
  "Desgaste Ferramenta [min]": 280,
  "Tipo": "L"
}
```
Resposta:
```json
{
  "prediction": 0,
  "probability_failure": 0.37,
  "risk_level": "HIGH",
  "message": "Agendar manutenção preventiva imediatamente",
  "top_factors": [
    { "feature": "Torque [Nm]", "importance": 0.2593 },
    { "feature": "Desgaste Ferramenta [min]", "importance": 0.2577 },
    { "feature": "Velocidade Rotacao [rpm]", "importance": 0.2499 }
  ]
}
```

> `top_factors` mostra os 3 sensores que mais pesaram na decisão. Útil para a equipe de manutenção saber exatamente onde intervir.

---

## Por que o limiar de alerta é 10%?

A escolha de 10% como ponto de entrada para o nível MEDIUM não foi arbitrária. Foi testada contra outros limiares no conjunto de teste real (2.861 máquinas, proporção 97/3):

| Limiar | Recall | Precision | Alertas emitidos | Falhas perdidas |
|---|---|---|---|---|
| 5% | 100,0% | 12,1% | 655 | 0 |
| **10%** | **100,0%** | **16,6%** | **476** | **0** ← escolhido |
| 20% | 100,0% | 25,3% | 312 | 0 |
| 30% | 100,0% | 32,0% | 247 | 0 |
| 40% | 98,7% | 38,4% | 203 | 1 |
| 50% | 97,5% | 44,5% | 173 | 2 |

**Leitura da tabela:**
- **Recall** = de todas as falhas reais, quantas o modelo detectou
- **Precision** = de todos os alertas emitidos, quantos eram falhas de verdade
- **Falhas perdidas** = o número mais crítico — falhas que passaram sem alerta

**Por que 10% e não 30% ou 50%?**

No contexto de manutenção industrial, o custo de **perder uma falha real** (parada não planejada, dano ao equipamento, risco à segurança) é muito maior do que o custo de um **alarme falso** (inspeção desnecessária). Por isso o limiar foi definido no ponto mais sensível que ainda mantém recall de 100% — garantindo que **nenhuma falha real escapa sem alerta**.

O limiar de 10% não é o ponto de "provável falha" — é o ponto de "atenção, monitorar mais de perto". A escala LOW → MEDIUM → HIGH → CRITICAL traduz isso em ações graduais.

---

## Pipeline do modelo

1. Remoção de outliers pelo método **IQR**
2. Balanceamento de classes com **SMOTE** (2.8% → 50% de falhas)
3. Divisão treino/teste: **70% / 30%**
4. Normalização com **StandardScaler**
5. **Random Forest** com 100 árvores — hiperparâmetros otimizados por Grid Search

---

## Exemplos de uso

### Terminal (curl)

```bash
# Predição individual
curl -X POST https://machine-failure-prediction-production-22fe.up.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Temperatura Ar [K]": 310,
    "Temperatura Processo [K]": 315,
    "Velocidade Rotacao [rpm]": 1200,
    "Torque [Nm]": 90,
    "Desgaste Ferramenta [min]": 280,
    "Tipo": "L"
  }'

# Verificar status
curl https://machine-failure-prediction-production-22fe.up.railway.app/health

# Ver métricas do modelo
curl https://machine-failure-prediction-production-22fe.up.railway.app/metrics
```

---

### Python

```python
import requests

BASE_URL = "https://machine-failure-prediction-production-22fe.up.railway.app"

# Dados da máquina a ser avaliada
maquina = {
    "Temperatura Ar [K]": 310,
    "Temperatura Processo [K]": 315,
    "Velocidade Rotacao [rpm]": 1200,
    "Torque [Nm]": 90,
    "Desgaste Ferramenta [min]": 280,
    "Tipo": "L"
}

# Predição simples
resposta = requests.post(f"{BASE_URL}/predict", json=maquina)
resultado = resposta.json()
print(f"Risco: {resultado['risk_level']} ({resultado['probability_failure']*100:.1f}%)")
print(f"Mensagem: {resultado['message']}")

# Predição com explicação
resposta = requests.post(f"{BASE_URL}/predict/explain", json=maquina)
resultado = resposta.json()
print("\nFatores que mais influenciaram:")
for fator in resultado["top_factors"]:
    print(f"  {fator['feature']}: {fator['importance']:.4f}")
```

Saída esperada:
```
Risco: HIGH (37.0%)
Mensagem: Agendar manutenção preventiva imediatamente

Fatores que mais influenciaram:
  Torque [Nm]: 0.2593
  Desgaste Ferramenta [min]: 0.2577
  Velocidade Rotacao [rpm]: 0.2499
```

---

### Rodar os testes automatizados

```bash
pip install -r requirements_test.txt
pytest tests/ -v
```

---

## Monitoramento de drift

Modelos em produção degradam com o tempo à medida que o mundo real muda. Este projeto inclui um plano de monitoramento e um script de detecção:

- **Plano completo:** [`DRIFT_MONITORING.md`](DRIFT_MONITORING.md) — o que monitorar, quando retreinar, como agir
- **Script de detecção:** `monitorar_drift.py` — compara a distribuição de novos dados com o treinamento e sinaliza desvios acima de 15%

```bash
python monitorar_drift.py
```

---

## Como rodar localmente

```bash
# 1. Instalar dependências
pip install -r requirements_api.txt

# 2. Treinar o modelo
python api/model.py

# 3. Iniciar a API
uvicorn api.main:app --reload
```

API local disponível em: **http://127.0.0.1:8000/docs**
