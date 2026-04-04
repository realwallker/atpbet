import os
import requests

# Forzamos la lectura directa del entorno
API_KEY = os.environ.get('THE_ODDS_API_KEY')
BASE_URL = 'https://api.the-odds-api.com/v4/sports'

# Lista oficial extraída de la documentación que proporcionaste
ATP_KEYS = [
    "tennis_atp", "tennis_atp_aus_open_singles", "tennis_atp_canadian_open",
    "tennis_atp_china_open", "tennis_atp_cincinnati_open", "tennis_atp_dubai",
    "tennis_atp_french_open", "tennis_atp_indian_wells", "tennis_atp_italian_open",
    "tennis_atp_madrid_open", "tennis_atp_miami_open", "tennis_atp_monte_carlo_masters",
    "tennis_atp_paris_masters", "tennis_atp_qatar_open", "tennis_atp_shanghai_masters",
    "tennis_atp_us_open", "tennis_atp_wimbledon"
]

def obtener_partidos_atp_hoy():
    if not API_KEY:
        print("❌ ERROR: La variable THE_ODDS_API_KEY está vacía en Python.")
        return []

    todos_los_partidos = []
    
    # Probamos primero el genérico y luego los específicos si es necesario
    print(f"📡 Iniciando escaneo de mercados ATP...")
    
    for sport_key in ATP_KEYS:
        try:
            url = f"{BASE_URL}/{sport_key}/odds"
            params = {
                'apiKey': API_KEY,
                'regions': 'eu,us',
                'markets': 'h2h',
                'oddsFormat': 'decimal'
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"✅ Partidos encontrados en: {sport_key} ({len(data)})")
                    todos_los_partidos.extend(data)
            elif response.status_code == 401:
                print("❌ Error 401: Tu API Key fue rechazada por el servidor.")
                return []
        except Exception as e:
            continue

    if not todos_los_partidos:
        print("⏸️ No hay partidos activos en los torneos oficiales en este momento.")
    
    return todos_los_partidos

def extraer_mejores_cuotas(partido):
    mejores_cuotas = {}
    if 'bookmakers' not in partido: return None
    for b in partido['bookmakers']:
        for m in b['markets']:
            if m['key'] == 'h2h':
                for o in m['outcomes']:
                    if o['name'] not in mejores_cuotas or o['price'] > mejores_cuotas[o['name']]:
                        mejores_cuotas[o['name']] = o['price']
    return mejores_cuotas