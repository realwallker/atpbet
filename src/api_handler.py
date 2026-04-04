import os
import requests

def detectar_llave_maestra():
    # Intento 1: Nombre exacto
    key = os.getenv('THE_ODDS_API_KEY')
    
    if key:
        print(f"✅ Llave detectada directamente: {key[:3]}***")
        return key

    # Intento 2: Buscar variaciones (por si hubo error de dedo al crear el Secret)
    print("🔍 Buscando variaciones de la llave en el sistema...")
    for nombre, valor in os.environ.items():
        if "ODDS" in nombre.upper() or "API" in nombre.upper():
            if valor and valor != "***": # GitHub oculta el valor, pero el nombre no
                print(f"📡 ¡Encontré una posible llave! Se llama: '{nombre}'")
                return valor
    return None

API_KEY = detectar_llave_maestra()
BASE_URL = 'https://api.the-odds-api.com/v4/sports'

def obtener_partidos_atp_hoy():
    if not API_KEY:
        print("❌ ERROR CRÍTICO: La API Key no fue detectada por el sistema.")
        # Imprime todos los nombres de variables disponibles para debug (sin los valores)
        print(f"Variables disponibles: {list(os.environ.keys())}")
        return []

    params = {
        'apiKey': API_KEY,
        'regions': 'eu',
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }

    try:
        url = f"{BASE_URL}/tennis_atp/odds"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error API ({response.status_code}): {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return []

def extraer_mejores_cuotas(partido):
    # (Mantener igual que el anterior)
    pass