import os
import requests

# Configuración de Identidad y Endpoints
API_KEY = os.getenv('ad819a411d29160fddf766f7f5aade0b')
BASE_URL = 'https://api.the-odds-api.com/v4/sports'

def obtener_partidos_atp_hoy():
    """
    Obtiene la cartelera de partidos ATP del día actual usando The Odds API.
    """
    if not API_KEY:
        print("❌ ERROR CRÍTICO: La API Key no fue detectada por el sistema.")
        return []

    # Parámetros para filtrar solo tenis ATP (Pre-match)
    params = {
        'apiKey': API_KEY,
        'regions': 'eu,us',
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }

    try:
        # Petición a la API para el mercado de Tenis ATP
        url = f"{BASE_URL}/tennis_atp/odds"
        response = requests.get(url, params=params)

        if response.status_code == 200:
            partidos = response.json()
            print(f"✅ Conexión exitosa. Partidos detectados: {len(partidos)}")
            return partidos
        
        elif response.status_code == 401:
            print("❌ ERROR 401: Llave de API inválida o no autorizada.")
            return []
        
        else:
            print(f"⚠️ Error inesperado de la API: {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return []

def extraer_mejores_cuotas(partido):
    """
    Extrae la cuota más alta disponible entre todas las casas de apuestas para un partido.
    """
    mejores_cuotas = {}
    
    if 'bookmakers' not in partido:
        return None

    for bookmaker in partido['bookmakers']:
        for market in bookmaker['markets']:
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    jugador = outcome['name']
                    cuota = outcome['price']
                    
                    if jugador not in mejores_cuotas or cuota > mejores_cuotas[jugador]:
                        mejores_cuotas[jugador] = cuota
                        
    return mejores_cuotas

if __name__ == "__main__":
    # Test de diagnóstico rápido
    print(f"DEBUG: Buscando llave... {'Detectada' if API_KEY else 'Vacía'}")
    test = obtener_partidos_atp_hoy()