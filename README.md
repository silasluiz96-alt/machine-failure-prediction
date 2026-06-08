# Machine Failure Prediction — Precursor Project

[![API Status](https://img.shields.io/badge/API-Online-green)](https://machine-failure-prediction-production.up.railway.app)

**Live API:** https://machine-failure-prediction-production.up.railway.app/docs


> **Este projeto é o precursor direto de um artigo científico publicado.** Desenvolvido individualmente por **Silas Luiz Bom Fim** como exploração independente do tema, ele serviu de base para uma pesquisa acadêmica coletiva que resultou em publicação revisada por pares — mas os dois trabalhos têm autores, metodologias e resultados diferentes. Veja a seção [Relação com o artigo publicado](#relação-com-o-artigo-publicado) para entender as diferenças.

---

## Visão geral

Pipeline de Machine Learning para **predição de falhas em máquinas industriais** do setor metal-mecânico, desenvolvido de forma independente. O objetivo é identificar, com base em dados de sensores, se uma máquina está em risco de falha antes que ela ocorra.

O projeto tem duas partes complementares: os **notebooks de análise e modelagem** e uma **API REST em produção** que serve o modelo treinado.

---

## Pipeline implementado

```
Dataset → Análise Exploratória → Pré-processamento → Modelagem → Avaliação → API
```

### Etapa 1 — Análise Exploratória (`analise_exploratoria.ipynb`)
- Distribuição dos tipos de falha
- Análise comparativa entre grupos (falha por calor, outras falhas, sem falha)
- Histogramas, boxplots e matrizes de correlação por tipo de falha

### Etapa 2 — Pré-processamento
- Remoção de outliers pelo método **IQR**
- Codificação de variável categórica (`Tipo` → Label Encoding)
- Seleção de features por **mRMR** (Minimum Redundancy Maximum Relevance)
- Balanceamento de classes com **SMOTE**
- Normalização com **StandardScaler**

### Etapa 3 — Modelagem (`pipeline_ml.ipynb`)
Quatro modelos treinados com **Grid Search + validação cruzada estratificada (3-fold)**:
- Decision Tree
- Random Forest
- MLP (Rede Neural)
- SVM

### Etapa 4 — Avaliação
- Accuracy, F1-Score, Precision, Recall, ROC-AUC, Kappa
- Matrizes de confusão
- Ranking composto: F1 (40%) + Recall (30%) + Precision (20%) + AUC (10%)

---

## Resultados

| Modelo | Accuracy | F1-Score | Kappa | ROC-AUC |
|---|---|---|---|---|
| **Random Forest** | **97.54%** | **0.9754** | **0.9508** | **0.9972** |
| Decision Tree | ~95% | ~0.94 | ~0.90 | — |
| SVM | ~94% | ~0.94 | ~0.88 | — |
| MLP | ~92% | ~0.92 | ~0.84 | — |

**Melhor modelo: Random Forest** — 100 árvores, hiperparâmetros otimizados via Grid Search.

---

## API REST

O modelo treinado está servido via **FastAPI**, com deploy público no Railway.

**Base URL:** `https://machine-failure-prediction-production.up.railway.app`
**Documentação interativa:** [`/docs`](https://machine-failure-prediction-production.up.railway.app/docs)

### Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Informações e métricas do modelo |
| `GET` | `/health` | Status da API |
| `POST` | `/predict` | Predição individual |
| `POST` | `/predict/batch` | Predição em lote |

### Parâmetros de entrada

| Campo | Tipo | Intervalo | Descrição |
|---|---|---|---|
| `Temperatura Ar [K]` | float | 290 – 320 | Temperatura do ar em Kelvin |
| `Temperatura Processo [K]` | float | 300 – 320 | Temperatura do processo em Kelvin |
| `Velocidade Rotacao [rpm]` | float | 1000 – 3000 | Rotações por minuto |
| `Torque [Nm]` | float | 0 – 100 | Torque em Newton-metro |
| `Desgaste Ferramenta [min]` | float | 0 – 300 | Desgaste acumulado da ferramenta |
| `Tipo` | string | L, M ou H | Categoria do produto |

### Níveis de risco retornados

| `probability_failure` | `risk_level` | Significado |
|---|---|---|
| < 10% | `LOW` | Máquina operando normalmente |
| 10% – 30% | `MEDIUM` | Monitorar: probabilidade de falha em crescimento |
| 30% – 60% | `HIGH` | Agendar manutenção preventiva imediatamente |
| > 60% | `CRITICAL` | Parar a máquina — alto risco de falha iminente |

---

## Dataset

- **Fonte:** Dataset de manutenção preditiva industrial
- **Tamanho:** 10.000 registros
- **Features:** Temperatura do Ar, Temperatura do Processo, Velocidade de Rotação, Torque, Desgaste da Ferramenta, Tipo do Produto
- **Target:** Falha (0/1) e Tipo de Falha
- **Desbalanceamento original:** ~97% sem falha / ~3% com falha (corrigido via SMOTE)

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
├── analise_exploratoria.ipynb   ← EDA e análise dos padrões de falha
├── pipeline_ml.ipynb            ← pré-processamento, modelagem e avaliação
├── manutencao_preditiva.csv
└── requirements_api.txt
```

---

## Como executar

### Notebooks (Google Colab — recomendado)

1. Faça upload do arquivo `manutencao_preditiva.csv`
2. Execute `analise_exploratoria.ipynb` para explorar os padrões de falha
3. Execute `pipeline_ml.ipynb` para o pipeline completo de ML

```bash
# Se preferir rodar localmente:
pip install pandas numpy matplotlib seaborn scikit-learn imbalanced-learn
```

### API localmente

```bash
# 1. Instalar dependências
pip install -r requirements_api.txt

# 2. Treinar o modelo (gera os arquivos em model/)
python api/model.py

# 3. Subir a API
uvicorn api.main:app --reload
```

A API fica disponível em `http://127.0.0.1:8000` — acesse `/docs` para a documentação interativa.

---

## Fluxo de contribuição

Este repositório segue um acordo de boas práticas baseado na trilha [GitHub Copilot & Agentic AI in the SDLC](https://learn.microsoft.com/en-us/training/) da Microsoft. Toda mudança entra via **Pull Request**, revisada e aprovada antes do merge no `main`. A branch principal está protegida — push direto não é permitido.

---

## Tecnologias

```
notebooks   pandas · numpy · matplotlib · seaborn · scikit-learn · imbalanced-learn
api         FastAPI · Pydantic · Uvicorn · Docker · Railway
```

---

## API em produção

O projeto evoluiu além dos notebooks — o modelo Random Forest foi servido como uma **API REST em produção**, deployada no Railway.

| Endpoint | Descrição |
|---|---|
| `GET /metrics` | Accuracy 97,52% · F1 97,54% · ROC-AUC 99,8% |
| `POST /predict` | Predição individual com nível de risco |
| `POST /predict/batch` | Análise de múltiplas máquinas de uma vez |
| `POST /predict/explain` | Predição + explicação dos fatores decisivos |

A escala de risco segue critérios industriais reais — alerta a partir de **10% de probabilidade de falha**, com quatro níveis: LOW, MEDIUM, HIGH e CRITICAL.

Documentação completa: [README_API.md](README_API.md) · Guia de uso: [GUIA_USO.md](GUIA_USO.md)

---

## Relação com o artigo publicado

Este projeto é o **ponto de partida** de uma pesquisa acadêmica que culminou em publicação científica. A exploração feita aqui — pipeline de pré-processamento, comparação de modelos, análise de falhas — foi o trabalho inicial que embasou o estudo coletivo conduzido posteriormente na **UFABC**.

O artigo resultante:

> Araujo, S. A., Bomfim, S. L., et al. *Integration of Data Analytics and Data Mining for Machine Failure Mitigation and Decision Support in Metal–Mechanical Industry.* **Logistics**, Vol. 9, n. 3, Art. 109, MDPI, 2025.
> [doi.org/10.3390/logistics9030109](https://doi.org/10.3390/logistics9030109)

Apesar da origem comum, **este repositório não é o código do artigo**. A pesquisa formal seguiu um protocolo diferente, com mais autores e escolhas metodológicas distintas:

| | Este repositório | Artigo publicado |
|---|---|---|
| **Autoria** | Silas Luiz Bom Fim (individual) | 6 autores (coletivo) |
| **Natureza** | Exploração independente — precursor | Pesquisa acadêmica revisada por pares |
| **Melhor modelo** | Random Forest (97.54%) | Decision Tree (82.1%) |
| **Metodologia** | Iterativa, exploratória | Protocolo formal de pesquisa |

Contribuí no artigo como co-autor nas partes de implementação Python e visualizações, mas o código deste repositório foi desenvolvido de forma independente, com diferenças em relação ao trabalho final publicado.

---

## Autor

**Silas Luiz Bom Fim**
- [LinkedIn](https://www.linkedin.com/in/silas-luiz-bom-fim-96a448176)
- [GitHub](https://github.com/silasluiz96-alt)
