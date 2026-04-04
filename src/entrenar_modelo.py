import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, accuracy_score, classification_report
import pickle
import os

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_entrenamiento_ciego.csv")
MODEL_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "modelo_v2.pkl")

def entrenar():
    if not os.path.exists(FILE_PATH):
        print(f"Error: No se encuentra {FILE_PATH}. Ejecuta preparar_entrenamiento_ciego.py primero.")
        return

    # 1. Carga de datos
    df = pd.read_csv(FILE_PATH)
    
    # Definimos las variables de entrada (Features)
    # ELO_DIFF: Diferencia de fuerza real
    # RANK_DIFF: Diferencia de posición ATP
    # CUOTA_P1/P2: Probabilidad implícita de la casa
    features = ['ELO_DIFF', 'RANK_DIFF', 'CUOTA_P1', 'CUOTA_P2']
    X = df[features]
    y = df['LABEL'] # 1 si ganó P1, 0 si ganó P2
    
    # 2. División de datos (80% entrenamiento, 20% prueba)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 3. Configuración del Modelo XGBoost
    # Optimizamos para evitar el sobreajuste (overfitting)
    modelo = xgb.XGBClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='binary:logistic',
        eval_metric='logloss',
        random_state=42
    )
    
    print("--- Iniciando Entrenamiento del Cerebro V2 (Ciego) ---")
    modelo.fit(X_train, y_train)
    
    # 4. Evaluación de precisión real
    preds = modelo.predict(X_test)
    prob_preds = modelo.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, preds)
    loss = log_loss(y_test, prob_preds)
    
    print(f"Precisión Real del Modelo: {acc:.4f}")
    print(f"Log Loss (Margen de error): {loss:.4f}")
    print("\nReporte de Clasificación:")
    print(classification_report(y_test, preds))
    
    # 5. Guardado del modelo
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(modelo, f)
    
    print("-" * 30)
    print(f"Modelo V2 guardado en: {os.path.abspath(MODEL_PATH)}")

if __name__ == "__main__":
    entrenar()