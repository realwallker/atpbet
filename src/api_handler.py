import os
import requests

API_KEY = os.getenv('ad819a411d29160fddf766f7f5aade0b')
BASE_URL = 'https://api.the-odds-api.com/v4/sports'

def obtener_partidos_atp_hoy():
    """
    Escanea dinámicamente todos los torneos ATP activos para evitar el error 404.
    """
    if not API_KEY:
        print("❌ ERROR: API Key no detectada.")
        return []

    try:
        # 1. Obtener la lista de todos los deportes/torneos activos en la API
        print("🔍 Buscando torneos ATP activos...")
        res_sports = requests.get(f"{BASE_URL}?apiKey={API_KEY}")
        
        if res_sports.status_code != 200:
            print(f"❌ Error al consultar lista de deportes: {res_sports.status_code}")
            return []

        deportes = res_sports.json()
        # Filtramos solo los que son Tennis y ATP (excluimos WTA y Challengers por ahora)
        keys_atp = [d['key'] for d in deportes if 'tennis' in d['key'] and 'atp' in d['key']]

        if not keys_atp:
            print("⏸️ No hay torneos ATP con mercados abiertos en este momento.")
            return []

        # 2. Recopilar partidos de todos los torneos encontrados
        todos_los_partidos = []
        for key in keys_atp:
            print(f"📡 Escaneando: {key}...")
            url = f"{BASE_URL}/{key}/odds"
            params = {
                'apiKey': API_KEY,
                'regions': 'eu,us',
                'markets': 'h2h',
                'oddsFormat': 'decimal'
            }
            res_odds = requests.get(url, params=params)
            if res_odds.status_code == 200:
                todos_los_partidos.extend(res_odds.json())

        print(f"✅ Escaneo completo. Total partidos detectados: {len(todos_los_partidos)}")
        return todos_los_partidos

    except Exception as e:
        print(f"❌ Error en el proceso del API Handler: {e}")
        return []

def extraer_mejores_cuotas(partido):
    mejores_cuotas = {}
    if 'bookmakers' not in partido: return None
    for bookmaker in partido['bookmakers']:
        for market in bookmaker['markets']:
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    jugador = outcome['name']
                    cuota = outcome['price']
                    if jugador not in mejores_cuotas or cuota > mejores_cuotas[jugador]:
                        mejores_cuotas[jugador] = cuota
    return mejores_cuotas