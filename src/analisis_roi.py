import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_limpio.csv")

def analizar_roi():
    if not os.path.exists(FILE_PATH):
        print("Error: No existe el archivo atp_limpio.csv")
        return

    df = pd.read_csv(FILE_PATH, low_memory=False)

    # FORZAR CONVERSIÓN NUMÉRICA: errors='coerce' convierte texto basura en NaN
    df['B365W'] = pd.to_numeric(df['B365W'], errors='coerce')
    df['B365L'] = pd.to_numeric(df['B365L'], errors='coerce')

    # Eliminar filas que quedaron como NaN tras la conversión
    df = df.dropna(subset=['B365W', 'B365L'])
    
    total_partidos = len(df)
    
    # Identificar Favorito vs Underdog
    df['FAVORITO_GANO'] = df['B365W'] < df['B365L']
    df['UNDERDOG_GANO'] = df['B365W'] > df['B365L']

    # 1. ROI Favoritos
    # Sumamos las cuotas de los partidos donde el favorito ganó y restamos la inversión total
    ganancia_fav = df[df['FAVORITO_GANO']]['B365W'].sum()
    roi_fav = ((ganancia_fav - total_partidos) / total_partidos) * 100

    # 2. ROI Underdogs
    ganancia_und = df[df['UNDERDOG_GANO']]['B365W'].sum()
    roi_und = ((ganancia_und - total_partidos) / total_partidos) * 100

    print(f"--- RESULTADOS SOBRE {total_partidos} PARTIDOS ---")
    print(f"ROI Apostando al Favorito: {roi_fav:.2f}%")
    print(f"ROI Apostando al Underdog: {roi_und:.2f}%")
    print("-" * 40)
    
    # Análisis por superficie
    print("ROI UNDERDOG POR SUPERFICIE:")
    for superficie in df['SURFACE'].dropna().unique():
        sub_df = df[df['SURFACE'] == superficie]
        n = len(sub_df)
        if n == 0: continue
        
        g_und = sub_df[sub_df['UNDERDOG_GANO']]['B365W'].sum()
        r_und = ((g_und - n) / n) * 100
        print(f"- {superficie.ljust(10)}: {r_und:6.2f}% ({n} partidos)")

if __name__ == "__main__":
    analizar_roi()