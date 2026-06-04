# Machine Failure Prediction — Precursor Project

> **Este projeto é o precursor direto de um artigo científico publicado.** Desenvolvido individualmente por **Silas Luiz Bom Fim** como exploração independente do tema, ele serviu de base para uma pesquisa acadêmica coletiva que resultou em publicação revisada por pares — mas os dois trabalhos têm autores, metodologias e resultados diferentes. Veja a seção [Relação com o artigo publicado](#relação-com-o-artigo-publicado) para entender as diferenças.

---

## Visão geral

Pipeline de Machine Learning para **predição de falhas em máquinas industriais** do setor metal-mecânico, desenvolvido de forma independente. O objetivo é identificar, com base em dados de sensores, se uma máquina está em risco de falha antes que ela ocorra.

---

## Pipeline implementado

```
Dataset → Análise Exploratória → Pré-processamento → Modelagem → Avaliação
```

### Etapa 1 — Análise Exploratória
- Distribuição dos tipos de falha
- Análise comparativa entre grupos (falha por calor, outras falhas, sem falha)
- Histogramas, boxplots e matrizes de correlação por tipo de falha

### Etapa 2 — Pré-processamento
- Remoção de outliers pelo método **IQR**
- Codificação de variável categórica (`Tipo` → Label Encoding)
- Seleção de features por **mRMR** (Minimum Redundancy Maximum Relevance)
- Balanceamento de classes com **SMOTE**
- Normalização com **StandardScaler**

### Etapa 3 — Modelagem
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

## Dataset

- **Fonte:** Dataset de manutenção preditiva industrial
- **Tamanho:** 10.000 registros
- **Features:** Temperatura do Ar, Temperatura do Processo, Velocidade de Rotação, Torque, Desgaste da Ferramenta, Tipo do Produto
- **Target:** Falha (0/1) e Tipo de Falha
- **Desbalanceamento original:** ~97% sem falha / ~3% com falha (corrigido via SMOTE)

---

## Tecnologias

```python
pandas · numpy · matplotlib · seaborn    # Manipulação e visualização de dados
scikit-learn                             # Modelos ML, GridSearchCV, métricas
imbalanced-learn                         # SMOTE
```

---

## Como executar

Os notebooks foram desenvolvidos no **Google Colab**:

1. Faça upload do arquivo `manutencao_preditiva.csv`
2. Execute `Projeto_predição.ipynb` para a análise exploratória
3. Execute `Relatório_Final.ipynb` para o pipeline completo de ML

```bash
# Se quiser rodar localmente:
pip install pandas numpy matplotlib seaborn scikit-learn imbalanced-learn
```

---

## Relação com o artigo publicado

Este projeto é o **ponto de partida** de uma pesquisa acadêmica que culminou em publicação científica. A exploração feita aqui — pipeline de pré-processamento, comparação de modelos, análise de falhas — foi o trabalho inicial que embasou o estudo coletivo conduzido posteriormente na **UFABC**.

O artigo resultante:

> Araujo, S. A., Bomfim, S. L., et al. *Integration of Data Analytics and Data Mining for Machine Failure Mitigation and Decision Support in Metal–Mechanical Industry.* **Logistics**, Vol. 9, n. 3, Art. 109, MDPI, 2025.
> 🔗 [doi.org/10.3390/logistics9030109](https://doi.org/10.3390/logistics9030109)

Apesar da origem comum, **este repositório não é o código do artigo**. A pesquisa formal seguiu um protocolo diferente, com mais autores e escolhas metodológicas distintas:

| | Este repositório | Artigo publicado |
|---|---|---|
| **Autoria** | Silas Luiz Bom Fim (individual) | 6 autores (coletivo) |
| **Natureza** | Exploração independente — precursor | Pesquisa acadêmica revisada por pares |
| **Melhor modelo** | Random Forest (97.54%) | Decision Tree (82.1%) |
| **Metodologia** | Iterativa, exploratória | Protocolo formal de pesquisa |

Contribuí no artigo como co-autor (implementação Python e visualizações), mas o código deste repositório foi desenvolvido de forma independente, antes e com diferenças em relação ao trabalho final publicado.

---

## Autor

**Silas Luiz Bom Fim**
- 💼 [LinkedIn](https://www.linkedin.com/in/silas-luiz-bom-fim-96a448176)
- 🐙 [GitHub](https://github.com/silasluiz96-alt)
