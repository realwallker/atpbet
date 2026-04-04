import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, accuracy_score, classification_report
import pickle
import os
import random

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Lee directamente atp_features.csv (generado por generar_features.py)
# Este archivo SÍ existe y tiene ELO_W, ELO_L, ELO_DIFF, RANK_DIFF
FILE_PATH  = os.path.join(BASE_DIR, "..", "data", "processed", "atp_features.csv")
MODEL_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "modelo_v2.pkl")

MARGEN_CASA = 1.05  # Margen típico del 5% para estimar cuotas desde ELO


def preparar_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    A partir de atp_features.csv construye el dataset de entrenamiento con:
      - ELO_DIFF  : diferencia de ELO híbrido (ya viene en el CSV)
      - RANK_DIFF : diferencia de ranking ATP (ya viene en el CSV)
      - CUOTA_P1  : cuota real del CSV histórico o estimada desde ELO
      - CUOTA_P2  : ídem para el oponente
      - LABEL     : 1 si P1 ganó, 0 si P1 perdió

    Se aleatoriza quién es P1 y quién es P2 para evitar sesgo posicional
    (en el CSV histórico el ganador SIEMPRE aparece primero).
    """
    # --- Detectar columnas de cuotas reales en el dataset histórico ---
    candidatos_w = ['B365W', 'PSW', 'CBW', 'GBW', 'IWW', 'SJW', 'MaxW', 'AvgW']
    candidatos_l = ['B365L', 'PSL', 'CBL', 'GBL', 'IWL', 'SJL', 'MaxL', 'AvgL']
    col_w = next((c for c in candidatos_w if c in df.columns), None)
    col_l = next((c for c in candidatos_l if c in df.columns), None)

    if col_w:
        print(f"   → Cuotas históricas detectadas: {col_w} / {col_l}")
    else:
        print("   → Sin cuotas históricas. Se estimarán desde ELO.")

    random.seed(42)
    registros = []

    for _, row in df.iterrows():
        elo_w = row.get('ELO_W', np.nan)
        elo_l = row.get('ELO_L', np.nan)

        # Saltar filas con ELO inválido
        if pd.isna(elo_w) or pd.isna(elo_l):
            continue

        rank_w = pd.to_numeric(row.get('WRANK', np.nan), errors='coerce')
        rank_l = pd.to_numeric(row.get('LRANK', np.nan), errors='coerce')

        # --- Cuotas ---
        try:
            if col_w and not pd.isna(row.get(col_w)):
                c_w = float(row[col_w])
                c_l = float(row[col_l])
            else:
                # Estimación desde probabilidad ELO
                prob_w = 1.0 / (1.0 + 10.0 ** ((elo_l - elo_w) / 400.0))
                prob_l = 1.0 - prob_w
                c_w = (1.0 / prob_w) / MARGEN_CASA
                c_l = (1.0 / prob_l) / MARGEN_CASA

            # Sanear cuotas (límites razonables)
            c_w = float(np.clip(c_w, 1.01, 50.0))
            c_l = float(np.clip(c_l, 1.01, 50.0))
        except Exception:
            continue

        # --- Rank diff (0 si falta alguno) ---
        if pd.isna(rank_w) or pd.isna(rank_l):
            rd = 0.0
        else:
            rd = float(rank_l - rank_w)

        elo_diff = float(elo_w - elo_l)

        # --- Aleatorizar P1 / P2 ---
        if random.random() > 0.5:
            # P1 = Ganador histórico
            registros.append({
                'ELO_DIFF':  round(elo_diff, 4),
                'RANK_DIFF': round(rd, 4),
                'CUOTA_P1':  round(c_w, 4),
                'CUOTA_P2':  round(c_l, 4),
                'LABEL':     1,
            })
        else:
            # P1 = Perdedor histórico
            registros.append({
                'ELO_DIFF':  round(-elo_diff, 4),
                'RANK_DIFF': round(-rd, 4),
                'CUOTA_P1':  round(c_l, 4),
                'CUOTA_P2':  round(c_w, 4),
                'LABEL':     0,
            })

    resultado = pd.DataFrame(registros)
    print(f"   → Dataset listo: {len(resultado)} partidos, columnas: {list(resultado.columns)}")
    return resultado


def entrenar():
    # --- 1. Verificar archivo fuente ---
    if not os.path.exists(FILE_PATH):
        print(f"❌ Error: No se encuentra {FILE_PATH}")
        print("   Asegúrate de ejecutar generar_features.py antes.")
        return

    # --- 2. Cargar y preparar datos ---
    print(f"📂 Cargando datos desde: {os.path.abspath(FILE_PATH)}")
    df_raw = pd.read_csv(FILE_PATH)
    print(f"   → {len(df_raw)} filas cargadas. Columnas disponibles: {list(df_raw.columns)}")

    df = preparar_dataset(df_raw)

    if df.empty:
        print("❌ Error: El dataset preparado está vacío. Revisa atp_features.csv.")
        return

    features = ['ELO_DIFF', 'RANK_DIFF', 'CUOTA_P1', 'CUOTA_P2']
    X = df[features]
    y = df['LABEL']

    # --- 3. División train / test ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # --- 4. Modelo XGBoost ---
    modelo = xgb.XGBClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='binary:logistic',
        eval_metric='logloss',
        random_state=42,
        use_label_encoder=False,
    )

    print("\n--- Iniciando Entrenamiento del Cerebro V2 (Ciego) ---")
    modelo.fit(X_train, y_train)

    # --- 5. Evaluación ---
    preds      = modelo.predict(X_test)
    prob_preds = modelo.predict_proba(X_test)[:, 1]

    acc  = accuracy_score(y_test, preds)
    loss = log_loss(y_test, prob_preds)

    print(f"Precisión Real del Modelo: {acc:.4f}")
    print(f"Log Loss (Margen de error): {loss:.4f}")
    print("\nReporte de Clasificación:")
    print(classification_report(y_test, preds))

    # --- 6. Guardar modelo ---
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(modelo, f)

    print("-" * 30)
    print(f"✅ Modelo V2 guardado en: {os.path.abspath(MODEL_PATH)}")


if __name__ == "__main__":
    entrenar()