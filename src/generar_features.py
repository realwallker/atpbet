import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Cerca de la línea 8 del archivo
FILE_PATH = os.path.join(BASE_DIR, "..", "data", "raw", "atp_limpio.csv") # <-- Cambiado de processed a raw
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_features.csv")

def ejecutar_ingenieria():
    # Añadimos esto para que GitHub cree la carpeta processed si no existe
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    if not os.path.exists(FILE_PATH):
        print(f"❌ Error crítico: No se encuentra {FILE_PATH}")
        return
        
    df = pd.read_csv(FILE_PATH)
    # ... resto del código igual ...
def calcular_elo_multisuperficie(df):
    # Diccionarios de ratings iniciales
    elo_gen = {}
    elo_surf = {'Hard': {}, 'Clay': {}, 'Grass': {}, 'Carpet': {}}
    
    ratings_w = []
    ratings_l = []
    
    K = 32 # Factor de aprendizaje

    for i, row in df.iterrows():
        w, l = row['WINNER'], row['LOSER']
        surf = row['SURFACE']
        
        # 1. Obtener ratings actuales (o 1500 si es nuevo)
        r_w_gen = elo_gen.get(w, 1500)
        r_l_gen = elo_gen.get(l, 1500)
        r_w_surf = elo_surf[surf].get(w, 1500)
        r_l_surf = elo_surf[surf].get(l, 1500)
        
        # 2. Guardar el promedio (nuestra métrica híbrida)
        # El ELO de superficie pesa un 60% y el general un 40%
        w_hybrid = (r_w_gen * 0.4) + (r_w_surf * 0.6)
        l_hybrid = (r_l_gen * 0.4) + (r_l_surf * 0.6)
        
        ratings_w.append(w_hybrid)
        ratings_l.append(l_hybrid)
        
        # 3. Actualizar ELOs
        exp_w = 1 / (1 + 10 ** ((l_hybrid - w_hybrid) / 400))
        
        # Update General
        elo_gen[w] = r_w_gen + K * (1 - exp_w)
        elo_gen[l] = r_l_gen - K * (1 - exp_w)
        
        # Update Superficie
        elo_surf[surf][w] = r_w_surf + K * (1 - exp_w)
        elo_surf[surf][l] = r_l_surf - K * (1 - exp_w)
        
    df['ELO_W'] = ratings_w
    df['ELO_L'] = ratings_l
    return df

def ejecutar_ingenieria():
    df = pd.read_csv(FILE_PATH)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('DATE')
    
    print("Calculando Ratings ELO Híbridos (Superficie + General)...")
    df = calcular_elo_multisuperficie(df)
    
    df['ELO_DIFF'] = df['ELO_W'] - df['ELO_L']
    df['RANK_DIFF'] = pd.to_numeric(df['LRANK'], errors='coerce') - pd.to_numeric(df['WRANK'], errors='coerce')
    
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Features avanzadas generadas en: {OUTPUT_PATH}")

if __name__ == "__main__":
    ejecutar_ingenieria()