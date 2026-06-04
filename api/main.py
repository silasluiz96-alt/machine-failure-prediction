"""
API de predição de falhas em máquinas industriais.

Iniciar:
    uvicorn api.main:app --reload
    (execute a partir da pasta MachineFailure/)

Antes de iniciar, treine o modelo:
    python api/model.py
"""

from contextlib import asynccontextmanager
from typing import Tuple

import numpy as np
from fastapi import FastAPI, HTTPException

from api.schemas import (
    BatchInput,
    BatchOutput,
    HealthCheck,
    MachineInput,
    ModelInfo,
    PredictionOutput,
)
from api.model import load_artifacts, prepare_input, FEATURES

# Estado global da aplicação
_model = None
_scaler = None
_meta = None


def _get_artifacts():
    return _model, _scaler, _meta


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _scaler, _meta
    try:
        _model, _scaler, _meta = load_artifacts()
        print("✓ Modelo carregado com sucesso.")
    except FileNotFoundError as e:
        print(f"⚠️  {e}")
        print("    Execute 'python api/model.py' para treinar o modelo antes de iniciar a API.")
    yield


app = FastAPI(
    title="Machine Failure Prediction API",
    description="API para predição de falhas em máquinas industriais usando Random Forest.",
    version="1.0.0",
    lifespan=lifespan,
)


def _classify_risk(probability: float) -> Tuple[str, str]:
    if probability < 0.3:
        return "LOW", "Máquina operando normalmente"
    elif probability <= 0.6:
        return "MEDIUM", "Atenção: risco moderado de falha"
    else:
        return "HIGH", "Alerta: alto risco de falha — manutenção recomendada"


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
    failures = sum(1 for p in predictions if p.prediction == 1)

    return BatchOutput(
        predictions=predictions,
        total=len(predictions),
        failures_detected=failures,
    )
