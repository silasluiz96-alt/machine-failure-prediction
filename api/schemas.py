from pydantic import BaseModel, Field
from typing import List, Literal


class MachineInput(BaseModel):
    temperatura_ar: float = Field(..., alias="Temperatura Ar [K]", ge=290, le=320, description="Temperatura do ar em Kelvin")
    temperatura_processo: float = Field(..., alias="Temperatura Processo [K]", ge=300, le=320, description="Temperatura do processo em Kelvin")
    velocidade_rotacao: float = Field(..., alias="Velocidade Rotacao [rpm]", ge=1000, le=3000, description="Velocidade de rotação em RPM")
    torque: float = Field(..., alias="Torque [Nm]", ge=0, le=100, description="Torque em Newton-metro")
    desgaste_ferramenta: float = Field(..., alias="Desgaste Ferramenta [min]", ge=0, le=300, description="Desgaste acumulado da ferramenta em minutos")
    tipo: Literal["L", "M", "H"] = Field(..., alias="Tipo", description="Tipo do produto: L (low), M (medium), H (high)")

    model_config = {"populate_by_name": True}


class PredictionOutput(BaseModel):
    prediction: int = Field(..., description="0 = normal, 1 = falha")
    probability_failure: float = Field(..., description="Probabilidade de falha (0 a 1)")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    message: str


class FactorItem(BaseModel):
    feature: str = Field(..., description="Nome do sensor/variável")
    importance: float = Field(..., description="Peso desse fator na decisão (0 a 1)")


class PredictionExplainOutput(BaseModel):
    prediction: int = Field(..., description="0 = normal, 1 = falha")
    probability_failure: float = Field(..., description="Probabilidade de falha (0 a 1)")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    message: str
    top_factors: List[FactorItem] = Field(..., description="Fatores que mais influenciaram a decisão")


class BatchInput(BaseModel):
    machines: List[MachineInput]


class BatchOutput(BaseModel):
    predictions: List[PredictionOutput]
    total: int
    failures_detected: int


class ModelInfo(BaseModel):
    name: str
    version: str
    accuracy: float
    features: List[str]
    description: str


class HealthCheck(BaseModel):
    status: str
    model_loaded: bool


class ConfusionMatrix(BaseModel):
    true_negative: int = Field(..., description="Máquinas normais identificadas corretamente")
    false_positive: int = Field(..., description="Máquinas normais classificadas como falha (alarme falso)")
    false_negative: int = Field(..., description="Falhas reais que o modelo não detectou (mais crítico)")
    true_positive: int = Field(..., description="Falhas reais detectadas corretamente")


class ModelMetrics(BaseModel):
    accuracy: float = Field(..., description="Percentual de acertos do modelo no conjunto de teste")
    precision: float = Field(..., description="Dos alertas emitidos, quantos eram falhas reais")
    recall: float = Field(..., description="Das falhas reais, quantas o modelo detectou")
    f1: float = Field(..., description="F1-Score — equilíbrio entre precisão e recall")
    roc_auc: float = Field(..., description="Área sob a curva ROC — capacidade discriminativa do modelo")
    model: str = Field(..., description="Algoritmo utilizado")
    trees: int = Field(..., description="Número de árvores de decisão no Random Forest")
    confusion_matrix: ConfusionMatrix = Field(..., description="Distribuição dos acertos e erros no conjunto de teste")
