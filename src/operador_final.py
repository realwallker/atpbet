import pickle
import pandas as pd
import numpy as np
import os
from textblob import TextBlob

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "modelo_v2.pkl")

# --- MÓDULO 1: ANÁLISIS DE SENTIMIENTO (NLP) ---
def analizar_sentimiento_noticias(lista_noticias):
    """
    Analiza una lista de titulares y devuelve un ajuste de probabilidad neto.
    Rango de ajuste por noticia: -0.05 a +0.05 (5%)
    """
    if not lista_noticias:
        return 0
    
    puntuaciones = []
    for noticia in lista_noticias:
        analisis = TextBlob(noticia)
        # La polaridad va de -1 a 1. La escalamos a un ajuste de 5% máximo.
        puntuaciones.append(analisis.sentiment.polarity * 0.05)
    
    return sum(puntuaciones) / len(puntuaciones)

# --- MÓDULO 2: GESTIÓN DE RIESGO (KELLY) ---
def calcular_stake_kelly(prob_final, cuota_casa, bankroll_total, fraccion=0.5):
    """
    Calcula cuánto dinero apostar basándose en la ventaja detectada.
    Se usa Kelly Fraccional (0.5) para mayor seguridad.
    """
    b = cuota_casa - 1  # Cuota neta
    p = prob_final      # Nuestra probabilidad
    q = 1 - p           # Probabilidad de perder
    
    # Fórmula de Kelly: f* = (bp - q) / b
    f_star = ((b * p) - q) / b
    
    if f_star <= 0:
        return 0
    
    # Aplicar el criterio fraccional para proteger el bankroll
    monto_sugerido = bankroll_total * f_star * fraccion
    return round(monto_sugerido, 2)

# --- MÓDULO 3: EL MOTOR DE PREDICCIÓN ---
def ejecutar_prediccion_maestra(elo_diff, rank_diff, cuota_p1, cuota_p2, 
                                noticias_p1=[], noticias_p2=[], bankroll=1000):
    # 1. Cargar el cerebro (Modelo V2)
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("El modelo V2 no existe. Entrénalo primero.")
        
    with open(MODEL_PATH, 'rb') as f:
        modelo = pickle.load(f)
    
    # 2. Obtener Probabilidad Base (Estadística)
    input_data = pd.DataFrame([[elo_diff, rank_diff, cuota_p1, cuota_p2]], 
                             columns=['ELO_DIFF', 'RANK_DIFF', 'CUOTA_P1', 'CUOTA_P2'])
    
    prob_base = modelo.predict_proba(input_data)[0][1] # Probabilidad de que P1 gane
    
    # 3. Aplicar Inyección de Contexto (Bypass)
    ajuste_p1 = analizar_sentimiento_noticias(noticias_p1)
    ajuste_p2 = analizar_sentimiento_noticias(noticias_p2)
    
    # El ajuste de P2 es inverso: si P2 tiene malas noticias, P1 sube probabilidad.
    prob_final = prob_base + ajuste_p1 - ajuste_p2
    
    # Limitar probabilidad entre 0.01 y 0.99 para evitar errores matemáticos
    prob_final = max(0.01, min(0.99, prob_final))
    
    # 4. Cálculo de Ventaja (Edge)
    prob_implícita_casa = 1 / cuota_p1
    edge = prob_final - prob_implícita_casa
    
    # 5. Cálculo de Inversión
    stake = calcular_stake_kelly(prob_final, cuota_p1, bankroll)
    
    return {
        "📊 Probabilidad Estadística": f"{prob_base:.2%}",
        "🧠 Ajuste por Contexto": f"{(ajuste_p1 - ajuste_p2):+.2%}",
        "🔥 Probabilidad Final": f"{prob_final:.2%}",
        "💰 Ventaja Detectada (Edge)": f"{edge:.2%}",
        "🚀 Stake Sugerido (Kelly)": f"${stake} (de ${bankroll})",
        "📢 Decisión": "APOSTAR" if edge > 0.05 and stake > 0 else "PASAR (Sin valor suficiente)"
    }

# --- EJECUCIÓN DE PRUEBA ---
if __name__ == "__main__":
    print("\n" + "="*40)
    print("      ANALIZADOR DE PROBABILIDADES ATP")
    print("="*40)
    
    # Ejemplo: Alcaraz vs Sinner
    resultado = ejecutar_prediccion_maestra(
        elo_diff=45,          # Alcaraz tiene 45 pts más de ELO
        rank_diff=2,          # Diferencia de ranking
        cuota_p1=1.95,        # Cuota en Bet365 para P1
        cuota_p2=1.85,
        noticias_p1=["Alcaraz feels fully recovered from ankle injury", "Great form in training"],
        noticias_p2=["Sinner mentions minor fatigue after long flight"],
        bankroll=500          # Capital actual en la casa de apuestas
    )
    
    for k, v in resultado.items():
        print(f"{k}: {v}")
    print("="*40 + "\n")