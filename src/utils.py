import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FEATURES_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_features.csv")

def normalizar_nombre_api_a_csv(nombre_api):
    """Convierte 'Novak Djokovic' en 'Djokovic N.'"""
    partes = nombre_api.split()
    if len(partes) >= 2:
        apellido = partes[-1]
        inicial = partes[0][0]
        return f"{apellido} {inicial}."
    return nombre_api

def obtener_datos_jugador_atp(nombre_api):
    if not os.path.exists(FEATURES_PATH):
        return 1500, 500 # Valores base por defecto
    
    df = pd.read_csv(FEATURES_PATH)
    nombre_target = normalizar_nombre_api_a_csv(nombre_api)
    
    # Buscamos coincidencias exactas en el apellido e inicial
    mask = (df['WINNER'] == nombre_target) | (df['LOSER'] == nombre_target)
    resultados = df[mask]
    
    if resultados.empty:
        # Intento de búsqueda parcial si falla la exacta
        apellido = nombre_api.split()[-1]
        mask_parcial = (df['WINNER'].str.contains(apellido, na=False)) | \
                       (df['LOSER'].str.contains(apellido, na=False))
        resultados = df[mask_parcial]

    if resultados.empty:
        return 1500, 500
    
    # Tomamos la última fila (la más reciente en el tiempo)
    ultima_fila = resultados.iloc[-1]
    
    if ultima_fila['WINNER'] == nombre_target:
        return float(ultima_fila['ELO_W']), float(ultima_fila['WRANK'])
    else:
        return float(ultima_fila['ELO_L']), float(ultima_fila['LRANK'])