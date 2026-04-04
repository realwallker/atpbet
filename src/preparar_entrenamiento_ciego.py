import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_features.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_entrenamiento_ciego.csv")

def preparar_datos_ciegos():
    df = pd.read_csv(INPUT_PATH)
    
    # Solo tomamos lo que sabemos ANTES del partido
    # Vamos a crear dos filas por cada partido para que el modelo no sepa quién es quién
    
    # Caso A: Jugador 1 es el ganador original
    df_a = pd.DataFrame()
    df_a['ELO_DIFF'] = df['ELO_W'] - df['ELO_L']
    df_a['RANK_DIFF'] = pd.to_numeric(df['LRANK'], errors='coerce') - pd.to_numeric(df['WRANK'], errors='coerce')
    df_a['CUOTA_P1'] = df['B365W']
    df_a['CUOTA_P2'] = df['B365L']
    df_a['LABEL'] = 1 # Ganó el Jugador 1
    
    # Caso B: Jugador 1 es el perdedor original
    df_b = pd.DataFrame()
    df_b['ELO_DIFF'] = df['ELO_L'] - df['ELO_W']
    df_b['RANK_DIFF'] = pd.to_numeric(df['WRANK'], errors='coerce') - pd.to_numeric(df['LRANK'], errors='coerce')
    df_b['CUOTA_P1'] = df['B365L']
    df_b['CUOTA_P2'] = df['B365W']
    df_b['LABEL'] = 0 # Ganó el Jugador 2 (perdió P1)
    
    df_final = pd.concat([df_a, df_b], axis=0).dropna()
    df_final.to_csv(OUTPUT_PATH, index=False)
    print(f"Dataset ciego generado con {len(df_final)} filas.")

if __name__ == "__main__":
    preparar_datos_ciegos()