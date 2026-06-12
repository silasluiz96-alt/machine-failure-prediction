# Guia de Uso — Machine Failure Prediction API

Este guia explica como utilizar a API de predição de falhas em máquinas industriais. Não é necessário conhecimento técnico para seguir os passos — basta acesso ao navegador.

**Link da API:** https://machine-failure-prediction-production-22fe.up.railway.app/docs

---

## O que essa API faz

Ela recebe dados dos sensores de uma máquina industrial e responde se essa máquina está em risco de falhar — antes que a falha aconteça. Isso é chamado de **manutenção preditiva**: agir antes do problema, não depois.

---

## Como acessar

1. Abra o link acima no navegador
2. Você verá a interface do Swagger — a documentação interativa da API
3. Cada bloco colorido é um endpoint (uma funcionalidade diferente)

---

## Entendendo os endpoints

### `GET /` — Ficha técnica
Mostra as informações do modelo: nome, versão, precisão e quais sensores ele usa para tomar decisões. Não precisa preencher nada.

### `GET /health` — Verificação de status
Confirma que a API está no ar e o modelo está pronto para uso. Responde `"status": "ok"` quando tudo está funcionando.

### `GET /metrics` — Desempenho do modelo
Exibe as métricas reais calculadas durante o treinamento:
- **accuracy**: percentual de acertos (97,52%)
- **f1**: equilíbrio entre não errar falhas e não dar alarme falso (97,54%)
- **roc_auc**: capacidade de distinguir máquina saudável de máquina em risco (99,8%)

---

## Como fazer uma predição

### Passo 1 — Predição simples (`POST /predict`)

Clique em `POST /predict` → **Try it out** → preencha os dados da máquina → **Execute**.

**Dados de uma máquina saudável:**
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
Resposta esperada:
```json
{
  "prediction": 0,
  "probability_failure": 0.0,
  "risk_level": "LOW",
  "message": "Máquina operando normalmente"
}
```

**Dados de uma máquina em risco:**
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
Resposta esperada:
```json
{
  "prediction": 0,
  "probability_failure": 0.37,
  "risk_level": "HIGH",
  "message": "Agendar manutenção preventiva imediatamente"
}
```

---

### Passo 2 — Analisar várias máquinas (`POST /predict/batch`)

Use quando quiser verificar várias máquinas de uma vez. Todas entram dentro de `"machines": [...]`:

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

No final da resposta você recebe:
- `"total"`: quantas máquinas foram analisadas
- `"failures_detected"`: quantas estão com probabilidade de falha ≥ 10%

---

### Passo 3 — Entender o motivo (`POST /predict/explain`)

Quando uma máquina aparecer em alerta no batch, use o `/predict/explain` para descobrir **por que** o modelo tomou aquela decisão. Informe apenas essa máquina específica (sem o `"machines": [...]`):

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

O `top_factors` diz à equipe de manutenção: *"o torque elevado e o desgaste da ferramenta foram os principais fatores de risco — é por aí que devem começar a inspeção."*

---

## Fluxo recomendado de uso

```
1. Roda o /predict/batch com todas as máquinas do turno
        ↓
2. Verifica o "failures_detected" no resultado
        ↓
3. Para cada máquina em alerta, usa o /predict/explain
        ↓
4. Encaminha os top_factors para a equipe de manutenção
```

---

## Escala de risco

| Probabilidade | Nível | O que fazer |
|---|---|---|
| < 10% | LOW | Nenhuma ação necessária |
| 10% – 30% | MEDIUM | Aumentar frequência de monitoramento |
| 30% – 60% | HIGH | Agendar manutenção preventiva |
| > 60% | CRITICAL | Parar a máquina imediatamente |

---

## Campos de entrada — referência rápida

| Campo | O que é | Exemplo |
|---|---|---|
| Temperatura Ar [K] | Temperatura do ambiente em Kelvin | 298.1 |
| Temperatura Processo [K] | Temperatura da operação em Kelvin | 308.6 |
| Velocidade Rotacao [rpm] | Rotações por minuto | 1551 |
| Torque [Nm] | Força de rotação em Newton-metro | 42.8 |
| Desgaste Ferramenta [min] | Minutos acumulados de uso da ferramenta | 120 |
| Tipo | Categoria do produto: L, M ou H | M |

> **Dica:** Kelvin = Celsius + 273.15. Temperatura ambiente de 25°C = 298.15 K.
