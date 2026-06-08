"""
Testes automatizados da Machine Failure Prediction API.

Como rodar:
    pytest tests/ -v

O TestClient simula requisições HTTP sem precisar subir um servidor real.
O modelo é carregado automaticamente pelo lifespan da aplicação.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture(scope="module")
def client():
    """Sobe a API uma vez para todos os testes do módulo, carregando o modelo."""
    with TestClient(app) as c:
        yield c

# ------------------------------------------------------------------ #
# Dados de exemplo reutilizados nos testes
# ------------------------------------------------------------------ #

MAQUINA_SAUDAVEL = {
    "Temperatura Ar [K]": 298.1,
    "Temperatura Processo [K]": 308.6,
    "Velocidade Rotacao [rpm]": 1551,
    "Torque [Nm]": 42.8,
    "Desgaste Ferramenta [min]": 0,
    "Tipo": "M",
}

MAQUINA_EM_RISCO = {
    "Temperatura Ar [K]": 310,
    "Temperatura Processo [K]": 315,
    "Velocidade Rotacao [rpm]": 1200,
    "Torque [Nm]": 90,
    "Desgaste Ferramenta [min]": 280,
    "Tipo": "L",
}

MAQUINA_INVALIDA = {
    "Temperatura Ar [K]": 999,   # fora do intervalo válido (máx 320)
    "Temperatura Processo [K]": 308.6,
    "Velocidade Rotacao [rpm]": 1551,
    "Torque [Nm]": 42.8,
    "Desgaste Ferramenta [min]": 0,
    "Tipo": "M",
}


# ------------------------------------------------------------------ #
# 1. GET /health
# ------------------------------------------------------------------ #

def test_health_retorna_ok(client):
    """A API deve estar no ar e o modelo carregado."""
    resposta = client.get("/health")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["status"] == "ok"
    assert dados["model_loaded"] is True


# ------------------------------------------------------------------ #
# 2. GET /
# ------------------------------------------------------------------ #

def test_model_info_retorna_campos_esperados(client):
    """A ficha técnica do modelo deve conter nome, versão e features."""
    resposta = client.get("/")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "name" in dados
    assert "accuracy" in dados
    assert "features" in dados
    assert len(dados["features"]) == 6  # 6 sensores


# ------------------------------------------------------------------ #
# 3. GET /metrics
# ------------------------------------------------------------------ #

def test_metrics_contem_dois_cenarios(client):
    """O endpoint de métricas deve retornar cenário laboratório e mundo real."""
    resposta = client.get("/metrics")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "laboratorio" in dados
    assert "mundo_real" in dados


def test_metrics_contem_matriz_de_confusao(client):
    """Cada cenário deve incluir a matriz de confusão."""
    resposta = client.get("/metrics")
    dados = resposta.json()
    for cenario in ["laboratorio", "mundo_real"]:
        cm = dados[cenario]["confusion_matrix"]
        assert "true_negative" in cm
        assert "false_positive" in cm
        assert "false_negative" in cm
        assert "true_positive" in cm


def test_recall_laboratorio_acima_de_95_porcento(client):
    """O recall no cenário laboratório deve ser maior que 95%."""
    resposta = client.get("/metrics")
    dados = resposta.json()
    assert dados["laboratorio"]["recall"] > 0.95


# ------------------------------------------------------------------ #
# 4. POST /predict — máquina saudável
# ------------------------------------------------------------------ #

def test_predict_maquina_saudavel_retorna_low(client):
    """Máquina com parâmetros normais deve retornar risco LOW."""
    resposta = client.post("/predict", json=MAQUINA_SAUDAVEL)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["risk_level"] == "LOW"
    assert dados["probability_failure"] < 0.10


# ------------------------------------------------------------------ #
# 5. POST /predict — máquina em risco
# ------------------------------------------------------------------ #

def test_predict_maquina_em_risco_nao_retorna_low(client):
    """Máquina com parâmetros críticos não deve retornar risco LOW."""
    resposta = client.post("/predict", json=MAQUINA_EM_RISCO)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["risk_level"] != "LOW"
    assert dados["probability_failure"] >= 0.10


# ------------------------------------------------------------------ #
# 6. POST /predict — dado inválido
# ------------------------------------------------------------------ #

def test_predict_dado_invalido_retorna_422(client):
    """Temperatura fora do intervalo válido deve retornar erro de validação."""
    resposta = client.post("/predict", json=MAQUINA_INVALIDA)
    assert resposta.status_code == 422


# ------------------------------------------------------------------ #
# 7. POST /predict/batch
# ------------------------------------------------------------------ #

def test_predict_batch_retorna_total_correto(client):
    """O batch deve retornar uma predição para cada máquina enviada."""
    payload = {"machines": [MAQUINA_SAUDAVEL, MAQUINA_EM_RISCO]}
    resposta = client.post("/predict/batch", json=payload)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["total"] == 2
    assert len(dados["predictions"]) == 2


def test_predict_batch_detecta_falha(client):
    """O batch deve contar a máquina em risco em failures_detected."""
    payload = {"machines": [MAQUINA_SAUDAVEL, MAQUINA_EM_RISCO]}
    resposta = client.post("/predict/batch", json=payload)
    dados = resposta.json()
    assert dados["failures_detected"] >= 1


# ------------------------------------------------------------------ #
# 8. POST /predict/explain
# ------------------------------------------------------------------ #

def test_predict_explain_retorna_top_factors(client):
    """O explain deve retornar os 3 fatores que mais influenciaram a decisão."""
    resposta = client.post("/predict/explain", json=MAQUINA_EM_RISCO)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "top_factors" in dados
    assert len(dados["top_factors"]) == 3


def test_predict_explain_fatores_tem_importancia(client):
    """Cada fator deve ter nome e importância entre 0 e 1."""
    resposta = client.post("/predict/explain", json=MAQUINA_EM_RISCO)
    dados = resposta.json()
    for fator in dados["top_factors"]:
        assert "feature" in fator
        assert "importance" in fator
        assert 0 <= fator["importance"] <= 1
