"""
Treina o Random Forest seguindo o pipeline do Relatório_Final.ipynb e serializa
o modelo em model/model.pkl e o scaler em model/scaler.pkl.

Execute diretamente:
    python api/model.py
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, precision_score, recall_score, confusion_matrix
from imblearn.over_sampling import SMOTE

# Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "manutencao_preditiva.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
META_PATH = MODEL_DIR / "metadata.pkl"

FEATURES = [
    "Temperatura Ar [K]",
    "Temperatura Processo [K]",
    "Velocidade Rotacao [rpm]",
    "Torque [Nm]",
    "Desgaste Ferramenta [min]",
    "Tipo_encoded",
]
TARGET = "Alvo"

TIPO_MAP = {"L": 0, "M": 1, "H": 2}


def remove_outliers_iqr(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    df_clean = df.copy()
    for col in columns:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df_clean = df_clean[(df_clean[col] >= lower) & (df_clean[col] <= upper)]
    return df_clean


def train_and_save():
    print("=" * 60)
    print("TREINANDO MODELO DE PREDIÇÃO DE FALHAS")
    print("=" * 60)

    # 1. Carregar dados
    print(f"\n[1/6] Carregando dados de {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"      {df.shape[0]} registros, {df.shape[1]} colunas")

    # 2. Codificar variável categórica 'Tipo'
    print("\n[2/6] Codificando variável 'Tipo'...")
    le = LabelEncoder()
    df["Tipo_encoded"] = le.fit_transform(df["Tipo"])

    # 3. Remover outliers (IQR)
    print("\n[3/6] Removendo outliers (método IQR)...")
    numeric_cols = [
        "Temperatura Ar [K]",
        "Temperatura Processo [K]",
        "Velocidade Rotacao [rpm]",
        "Torque [Nm]",
        "Desgaste Ferramenta [min]",
    ]
    df_clean = remove_outliers_iqr(df, numeric_cols)
    removed = df.shape[0] - df_clean.shape[0]
    print(f"      {removed} registros removidos → {df_clean.shape[0]} restantes")

    # 4. Separar X e y, balancear com SMOTE
    print("\n[4/6] Balanceando classes com SMOTE...")
    X = df_clean[FEATURES]
    y = df_clean[TARGET]
    print(f"      Antes: {(y == 0).sum()} normais | {(y == 1).sum()} falhas")

    smote = SMOTE(random_state=42)
    X_bal, y_bal = smote.fit_resample(X, y)
    print(f"      Depois: {(y_bal == 0).sum()} normais | {(y_bal == 1).sum()} falhas")

    # 5. Dividir treino/teste (70/30) e normalizar
    print("\n[5/6] Dividindo treino/teste e normalizando...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_bal, y_bal, test_size=0.30, random_state=42, stratify=y_bal
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # 6. Treinar Random Forest com melhores hiperparâmetros do notebook
    print("\n[6/6] Treinando Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        max_features="sqrt",
        min_samples_leaf=1,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train_s, y_train)

    # Avaliação — cenário laboratório (dados balanceados 50/50)
    y_pred = rf.predict(X_test_s)
    y_proba = rf.predict_proba(X_test_s)[:, 1]
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred).tolist()

    print(f"\n  [Cenario: laboratorio — balanceado 50/50]")
    print(f"      Accuracy  : {acc:.4f}")
    print(f"      Precision : {prec:.4f}")
    print(f"      Recall    : {rec:.4f}")
    print(f"      F1-Score  : {f1:.4f}")
    print(f"      ROC-AUC   : {auc:.4f}")
    print(f"      Matriz: TN={cm[0][0]} | FP={cm[0][1]} | FN={cm[1][0]} | TP={cm[1][1]}")

    # Avaliação — cenário mundo real (dados originais sem SMOTE, proporção 97/3)
    print(f"\n  [Cenario: mundo real — proporcao original 97/3]")
    X_real = df_clean[FEATURES]
    y_real = df_clean[TARGET]
    _, X_test_real, _, y_test_real = train_test_split(
        X_real, y_real, test_size=0.30, random_state=42, stratify=y_real
    )
    X_test_real_s = scaler.transform(X_test_real)
    y_pred_real = rf.predict(X_test_real_s)
    y_proba_real = rf.predict_proba(X_test_real_s)[:, 1]

    acc_r  = accuracy_score(y_test_real, y_pred_real)
    prec_r = precision_score(y_test_real, y_pred_real, zero_division=0)
    rec_r  = recall_score(y_test_real, y_pred_real, zero_division=0)
    f1_r   = f1_score(y_test_real, y_pred_real, zero_division=0)
    auc_r  = roc_auc_score(y_test_real, y_proba_real)
    cm_r   = confusion_matrix(y_test_real, y_pred_real).tolist()

    print(f"      Accuracy  : {acc_r:.4f}")
    print(f"      Precision : {prec_r:.4f}")
    print(f"      Recall    : {rec_r:.4f}")
    print(f"      F1-Score  : {f1_r:.4f}")
    print(f"      ROC-AUC   : {auc_r:.4f}")
    print(f"      Matriz: TN={cm_r[0][0]} | FP={cm_r[0][1]} | FN={cm_r[1][0]} | TP={cm_r[1][1]}")

    # Salvar
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(rf, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(
        {
            # Cenário laboratório (dados balanceados com SMOTE)
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm,
            # Cenário mundo real (proporção original 97/3, sem SMOTE)
            "real_accuracy": round(acc_r, 4),
            "real_precision": round(prec_r, 4),
            "real_recall": round(rec_r, 4),
            "real_f1": round(f1_r, 4),
            "real_roc_auc": round(auc_r, 4),
            "real_confusion_matrix": cm_r,
            # Configuração
            "features": FEATURES,
            "tipo_map": TIPO_MAP,
            "version": "1.0.0",
        },
        META_PATH,
    )

    print(f"\n✓ Modelo salvo em:  {MODEL_PATH}")
    print(f"✓ Scaler salvo em:  {SCALER_PATH}")
    print(f"✓ Metadata salvo em: {META_PATH}")
    print("\n" + "=" * 60)
    print("TREINAMENTO CONCLUÍDO!")
    print("=" * 60)


def load_artifacts():
    """Carrega e retorna (model, scaler, metadata). Levanta FileNotFoundError se não treinado."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em {MODEL_PATH}. "
            "Execute: python api/model.py"
        )
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    meta = joblib.load(META_PATH)
    return model, scaler, meta


def prepare_input(data: dict, tipo_map: dict = None) -> np.ndarray:
    """Converte o dict de entrada da API em array pronto para predição."""
    if tipo_map is None:
        _, _, meta = load_artifacts()
        tipo_map = meta["tipo_map"]
    row = [
        data["temperatura_ar"],
        data["temperatura_processo"],
        data["velocidade_rotacao"],
        data["torque"],
        data["desgaste_ferramenta"],
        tipo_map[data["tipo"]],
    ]
    return np.array(row).reshape(1, -1)


if __name__ == "__main__":
    train_and_save()
