import os
import requests

# Forzamos la lectura directa del entorno
API_KEY = os.environ.get('THE_ODDS_API_KEY')
BASE_URL = 'https://api.the-odds-api.com/v4/sports'

# Lista oficial extraída de la documentación de The Odds API
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
    print("📡 Iniciando escaneo de mercados ATP...")

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
        except Exception:
            continue

    if not todos_los_partidos:
        print("⏸️ No hay partidos activos en los torneos oficiales en este momento.")

    return todos_los_partidos


def extraer_mejores_cuotas(partido):
    """
    Extrae las mejores cuotas disponibles para un partido.

    FIX: Antes devolvía {nombre_jugador: cuota}, pero main.py espera {'P1': cuota, 'P2': cuota}.
    Ahora mapea home_team → P1 y away_team → P2 para mantener consistencia con el resto del código.

    Returns:
        {'P1': float, 'P2': float} o None si no hay datos.
    """
    if 'bookmakers' not in partido or not partido['bookmakers']:
        return None

    p1_name = partido.get('home_team')
    p2_name = partido.get('away_team')

    if not p1_name or not p2_name:
        return None

    # Acumular mejores cuotas (máximo entre todas las casas)
    mejores = {p1_name: None, p2_name: None}

    for bookmaker in partido['bookmakers']:
        for market in bookmaker['markets']:
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    name = outcome['name']
                    price = outcome['price']
                    if name in mejores:
                        if mejores[name] is None or price > mejores[name]:
                            mejores[name] = price

    cuota_p1 = mejores.get(p1_name)
    cuota_p2 = mejores.get(p2_name)

    if cuota_p1 is None or cuota_p2 is None:
        return None

    return {'P1': cuota_p1, 'P2': cuota_p2}