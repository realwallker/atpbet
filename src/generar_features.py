import pandas as pd
import numpy as np
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "..", "data", "raw", "atp_limpio.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_features.csv")
OUTPUT_CIEGO_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_entrenamiento_ciego.csv")


def calcular_elo_multisuperficie(df):
    """Calcula ratings ELO híbridos (60% superficie + 40% general)."""
    elo_gen = {}
    elo_surf = {'Hard': {}, 'Clay': {}, 'Grass': {}, 'Carpet': {}}

    ratings_w = []
    ratings_l = []

    K = 32  # Factor de aprendizaje

    for _, row in df.iterrows():
        w = row['WINNER']
        l = row['LOSER']
        surf = row['SURFACE'] if row['SURFACE'] in elo_surf else 'Hard'

        r_w_gen  = elo_gen.get(w, 1500)
        r_l_gen  = elo_gen.get(l, 1500)
        r_w_surf = elo_surf[surf].get(w, 1500)
        r_l_surf = elo_surf[surf].get(l, 1500)

        w_hybrid = (r_w_gen * 0.4) + (r_w_surf * 0.6)
        l_hybrid = (r_l_gen * 0.4) + (r_l_surf * 0.6)

        ratings_w.append(w_hybrid)
        ratings_l.append(l_hybrid)

        exp_w = 1 / (1 + 10 ** ((l_hybrid - w_hybrid) / 400))

        elo_gen[w]      = r_w_gen  + K * (1 - exp_w)
        elo_gen[l]      = r_l_gen  - K * (1 - exp_w)
        elo_surf[surf][w] = r_w_surf + K * (1 - exp_w)
        elo_surf[surf][l] = r_l_surf - K * (1 - exp_w)

    df['ELO_W'] = ratings_w
    df['ELO_L'] = ratings_l
    return df


def generar_dataset_ciego(df):
    """
    Genera atp_entrenamiento_ciego.csv para entrenar el modelo.

    - Aleatoriza quién es P1 y P2 para evitar sesgo posicional.
    - CUOTA_P1 / CUOTA_P2: usa columnas reales del dataset (B365W/L, PSW/L…)
      o, si no existen, las estima a partir de la probabilidad ELO.
    - LABEL: 1 si P1 ganó, 0 si P1 perdió.
    """
    os.makedirs(os.path.dirname(OUTPUT_CIEGO_PATH), exist_ok=True)

    # Columnas de cuotas históricas más habituales en datasets ATP
    candidatos_w = ['B365W', 'PSW', 'CBW', 'GBW', 'IWW', 'SJW', 'MaxW', 'AvgW']
    candidatos_l = ['B365L', 'PSL', 'CBL', 'GBL', 'IWL', 'SJL', 'MaxL', 'AvgL']

    col_cuota_w = next((c for c in candidatos_w if c in df.columns), None)
    col_cuota_l = next((c for c in candidatos_l if c in df.columns), None)

    if col_cuota_w:
        print(f"   → Cuotas reales detectadas: {col_cuota_w} / {col_cuota_l}")
    else:
        print("   → Sin cuotas históricas en el CSV. Se estimarán desde ELO.")

    registros = []
    random.seed(42)  # Reproducibilidad

    for _, row in df.iterrows():
        elo_w = row['ELO_W']
        elo_l = row['ELO_L']
        rank_w = pd.to_numeric(row.get('WRANK', np.nan), errors='coerce')
        rank_l = pd.to_numeric(row.get('LRANK', np.nan), errors='coerce')

        # --- Obtener cuotas ---
        if col_cuota_w and not pd.isna(row.get(col_cuota_w)):
            c_w = float(row[col_cuota_w])
            c_l = float(row[col_cuota_l])
        else:
            # Probabilidad ELO + margen de casa del 5%
            prob_w = 1 / (1 + 10 ** ((elo_l - elo_w) / 400))
            prob_l = 1 - prob_w
            margin = 1.05
            c_w = round((1 / prob_w) / margin, 4) if prob_w > 0 else 2.0
            c_l = round((1 / prob_l) / margin, 4) if prob_l > 0 else 2.0

        # Validar cuotas (mínimo 1.01, máximo 50)
        c_w = max(1.01, min(c_w, 50.0))
        c_l = max(1.01, min(c_l, 50.0))

        # --- Aleatorizar P1 / P2 ---
        if random.random() > 0.5:
            # P1 = Ganador del partido histórico
            elo_diff  = elo_w - elo_l
            rank_diff = (rank_l - rank_w) if not (np.isnan(rank_w) or np.isnan(rank_l)) else 0.0
            cuota_p1, cuota_p2 = c_w, c_l
            label = 1
        else:
            # P1 = Perdedor del partido histórico
            elo_diff  = elo_l - elo_w
            rank_diff = (rank_w - rank_l) if not (np.isnan(rank_w) or np.isnan(rank_l)) else 0.0
            cuota_p1, cuota_p2 = c_l, c_w
            label = 0

        registros.append({
            'ELO_DIFF':  round(elo_diff, 4),
            'RANK_DIFF': round(rank_diff, 4),
            'CUOTA_P1':  round(cuota_p1, 4),
            'CUOTA_P2':  round(cuota_p2, 4),
            'LABEL':     label
        })

    ciego_df = pd.DataFrame(registros).dropna()
    ciego_df.to_csv(OUTPUT_CIEGO_PATH, index=False)
    print(f"✅ Datos ciegos listos en: {os.path.abspath(OUTPUT_CIEGO_PATH)}")
    print(f"   → {len(ciego_df)} partidos listos para entrenamiento")


def ejecutar_ingenieria():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    if not os.path.exists(FILE_PATH):
        print(f"❌ Error crítico: No se encuentra {FILE_PATH}")
        return

    df = pd.read_csv(FILE_PATH)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('DATE').reset_index(drop=True)

    print("Calculando Ratings ELO Híbridos (Superficie + General)...")
    df = calcular_elo_multisuperficie(df)

    df['ELO_DIFF']  = df['ELO_W'] - df['ELO_L']
    df['RANK_DIFF'] = (
        pd.to_numeric(df['LRANK'], errors='coerce') -
        pd.to_numeric(df['WRANK'], errors='coerce')
    )

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Features generadas en: {os.path.abspath(OUTPUT_PATH)}")

    # Generar dataset ciego para entrenamiento del modelo
    generar_dataset_ciego(df)


if __name__ == "__main__":
    ejecutar_ingenieria()