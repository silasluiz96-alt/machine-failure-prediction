"""
API de predição de falhas em máquinas industriais.

Iniciar localmente:
    uvicorn api.main:app --reload
    (execute a partir da pasta MachineFailure/)

O modelo é treinado automaticamente na primeira inicialização se os
arquivos .pkl não existirem — basta o CSV estar presente.
"""

from contextlib import asynccontextmanager
from typing import Tuple

import numpy as np
from fastapi import FastAPI, HTTPException

from api.schemas import (
    BatchInput,
    BatchOutput,
    ConfusionMatrix,
    FactorItem,
    HealthCheck,
    MachineInput,
    ModelInfo,
    ModelMetrics,
    PredictionExplainOutput,
    PredictionOutput,
)
from api.model import load_artifacts, prepare_input, train_and_save, MODEL_PATH, FEATURES

# Estado global da aplicação
_model = None
_scaler = None
_meta = None


def _get_artifacts():
    return _model, _scaler, _meta


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _scaler, _meta
    if not MODEL_PATH.exists():
        print("⚙️  Modelo não encontrado — iniciando treinamento automático...")
        train_and_save()
    _model, _scaler, _meta = load_artifacts()
    print("✓ Modelo carregado com sucesso.")
    yield


app = FastAPI(
    title="Machine Failure Prediction API",
    description="API para predição de falhas em máquinas industriais usando Random Forest.",
    version="1.0.0",
    lifespan=lifespan,
)


def _classify_risk(probability: float) -> Tuple[str, str]:
    if probability < 0.10:
        return "LOW", "Máquina operando normalmente"
    elif probability < 0.30:
        return "MEDIUM", "Monitorar: probabilidade de falha em crescimento"
    elif probability < 0.60:
        return "HIGH", "Agendar manutenção preventiva imediatamente"
    else:
        return "CRITICAL", "Parar a máquina — alto risco de falha iminente"


def _predict_single(machine: MachineInput) -> PredictionOutput:
    model, scaler, _ = _get_artifacts()
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo não carregado. Execute 'python api/model.py' primeiro.",
        )

    data = {
        "temperatura_ar": machine.temperatura_ar,
        "temperatura_processo": machine.temperatura_processo,
        "velocidade_rotacao": machine.velocidade_rotacao,
        "torque": machine.torque,
        "desgaste_ferramenta": machine.desgaste_ferramenta,
        "tipo": machine.tipo,
    }

    X = prepare_input(data)
    X_scaled = scaler.transform(X)

    prediction = int(model.predict(X_scaled)[0])
    probability = float(model.predict_proba(X_scaled)[0][1])
    risk_level, message = _classify_risk(probability)

    return PredictionOutput(
        prediction=prediction,
        probability_failure=round(probability, 4),
        risk_level=risk_level,
        message=message,
    )


def _predict_explain(machine: MachineInput) -> PredictionExplainOutput:
    model, scaler, _ = _get_artifacts()
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo não carregado. Execute 'python api/model.py' primeiro.",
        )

    data = {
        "temperatura_ar": machine.temperatura_ar,
        "temperatura_processo": machine.temperatura_processo,
        "velocidade_rotacao": machine.velocidade_rotacao,
        "torque": machine.torque,
        "desgaste_ferramenta": machine.desgaste_ferramenta,
        "tipo": machine.tipo,
    }

    X = prepare_input(data)
    X_scaled = scaler.transform(X)

    prediction = int(model.predict(X_scaled)[0])
    probability = float(model.predict_proba(X_scaled)[0][1])
    risk_level, message = _classify_risk(probability)

    # Pega o peso de cada sensor dentro do Random Forest e ordena do maior pro menor
    importances = model.feature_importances_
    factors = sorted(
        [FactorItem(feature=f, importance=round(float(i), 4)) for f, i in zip(FEATURES, importances)],
        key=lambda x: x.importance,
        reverse=True,
    )

    return PredictionExplainOutput(
        prediction=prediction,
        probability_failure=round(probability, 4),
        risk_level=risk_level,
        message=message,
        top_factors=factors[:3],
    )


@app.get("/", response_model=ModelInfo, tags=["Info"])
def get_model_info():
    """Retorna informações sobre o modelo treinado."""
    if _meta is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo não carregado. Execute 'python api/model.py' primeiro.",
        )
    return ModelInfo(
        name="Random Forest — Predição de Falhas",
        version=_meta["version"],
        accuracy=_meta["accuracy"],
        features=FEATURES,
        description=(
            "Modelo treinado com Random Forest (100 árvores) sobre dados de sensores "
            "industriais. Pipeline: remoção de outliers (IQR) + balanceamento SMOTE + "
            "normalização StandardScaler."
        ),
    )


@app.get("/health", response_model=HealthCheck, tags=["Info"])
def health_check():
    """Verifica se a API está no ar e se o modelo está carregado."""
    return HealthCheck(
        status="ok",
        model_loaded=_model is not None,
    )


@app.post("/predict", response_model=PredictionOutput, tags=["Predição"])
def predict(machine: MachineInput):
    """
    Recebe os dados de uma máquina e retorna a predição de falha.

    - **prediction**: 0 = normal, 1 = falha
    - **probability_failure**: probabilidade de falha (0 a 1)
    - **risk_level**: LOW / MEDIUM / HIGH
    - **message**: mensagem explicativa
    """
    return _predict_single(machine)


@app.post("/predict/batch", response_model=BatchOutput, tags=["Predição"])
def predict_batch(batch: BatchInput):
    """
    Recebe uma lista de máquinas e retorna uma predição para cada uma.
    """
    if not batch.machines:
        raise HTTPException(status_code=422, detail="A lista de máquinas não pode ser vazia.")

    predictions = [_predict_single(m) for m in batch.machines]
    failures = sum(1 for p in predictions if p.probability_failure >= 0.10)

    return BatchOutput(
        predictions=predictions,
        total=len(predictions),
        failures_detected=failures,
    )


@app.post("/predict/explain", response_model=PredictionExplainOutput, tags=["Predição"])
def predict_explain(machine: MachineInput):
    """
    Retorna a predição de falha com explicação dos fatores que mais influenciaram a decisão.

    - **top_factors**: os 3 sensores que mais pesaram na decisão do modelo
    - **importance**: valor entre 0 e 1 — quanto maior, mais esse sensor influenciou
    """
    return _predict_explain(machine)


@app.get("/metrics", response_model=ModelMetrics, tags=["Info"])
def get_metrics():
    """
    Retorna as métricas de desempenho do modelo treinado.

    - **accuracy**: percentual de acertos no conjunto de teste
    - **f1**: equilíbrio entre precisão e recall
    - **roc_auc**: capacidade do modelo de separar falha de não-falha
    - **model**: algoritmo utilizado
    - **trees**: número de árvores de decisão
    """
    if _meta is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo não carregado.",
        )
    cm_raw = _meta.get("confusion_matrix", [[0, 0], [0, 0]])
    return ModelMetrics(
        accuracy=_meta["accuracy"],
        precision=_meta.get("precision", 0.0),
        recall=_meta.get("recall", 0.0),
        f1=_meta["f1"],
        roc_auc=_meta["roc_auc"],
        model="Random Forest",
        trees=100,
        confusion_matrix=ConfusionMatrix(
            true_negative=cm_raw[0][0],
            false_positive=cm_raw[0][1],
            false_negative=cm_raw[1][0],
            true_positive=cm_raw[1][1],
        ),
    )
