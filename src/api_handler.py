import os
import requests

API_KEY  = os.environ.get('THE_ODDS_API_KEY')
BASE_URL = 'https://api.the-odds-api.com/v4'


def obtener_sport_keys_atp_activos():
    """
    Consulta /sports para obtener en tiempo real todos los sport keys
    de tenis ATP activos. Así no dependemos de una lista hardcodeada.
    """
    url = f"{BASE_URL}/sports"
    try:
        response = requests.get(url, params={'apiKey': API_KEY}, timeout=10)
        if response.status_code != 200:
            print(f"⚠️  No se pudo obtener lista de deportes ({response.status_code}). Usando respaldo.")
            return _fallback_keys()

        todos = response.json()
        atp_activos = [
            s['key'] for s in todos
            if s.get('active', False) and 'tennis_atp' in s['key']
        ]

        if not atp_activos:
            print("⚠️  Sin torneos ATP activos en la API. Usando lista de respaldo.")
            return _fallback_keys()

        print(f"🔍 Torneos ATP activos: {atp_activos}")
        return atp_activos

    except Exception as e:
        print(f"⚠️  Error al consultar /sports: {e}. Usando respaldo.")
        return _fallback_keys()


def _fallback_keys():
    """Lista de respaldo por si /sports falla."""
    return [
        "tennis_atp",
        "tennis_atp_monte_carlo_masters",
        "tennis_atp_french_open",
        "tennis_atp_madrid_open",
        "tennis_atp_italian_open",
        "tennis_atp_wimbledon",
        "tennis_atp_us_open",
        "tennis_atp_aus_open_singles",
        "tennis_atp_indian_wells",
        "tennis_atp_miami_open",
        "tennis_atp_canadian_open",
        "tennis_atp_cincinnati_open",
        "tennis_atp_shanghai_masters",
        "tennis_atp_paris_masters",
    ]


def obtener_partidos_atp_hoy():
    if not API_KEY:
        print("❌ ERROR: THE_ODDS_API_KEY está vacía.")
        return []

    sport_keys = obtener_sport_keys_atp_activos()
    todos_los_partidos = []
    ids_vistos = set()  # evitar duplicados entre torneos

    print(f"📡 Escaneando {len(sport_keys)} torneo(s) ATP activo(s)...")

    for sport_key in sport_keys:
        try:
            url = f"{BASE_URL}/sports/{sport_key}/odds"
            params = {
                'apiKey':     API_KEY,
                'regions':    'eu,us',
                'markets':    'h2h',
                'oddsFormat': 'decimal',
            }
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                nuevos = [p for p in data if p['id'] not in ids_vistos]
                if nuevos:
                    print(f"   ✅ {sport_key}: {len(nuevos)} partido(s) con cuotas")
                    for p in nuevos:
                        ids_vistos.add(p['id'])
                    todos_los_partidos.extend(nuevos)

            elif response.status_code == 401:
                print("❌ Error 401: API Key rechazada.")
                return []

            elif response.status_code == 422:
                pass  # Torneo fuera de temporada — normal, ignorar

        except Exception:
            continue

    if not todos_los_partidos:
        print("⏸️  No hay partidos activos en los torneos oficiales en este momento.")

    return todos_los_partidos


def extraer_mejores_cuotas(partido):
    """
    Devuelve {'P1': float, 'P2': float} con las mejores cuotas disponibles.
    P1 = home_team, P2 = away_team.
    """
    if 'bookmakers' not in partido or not partido['bookmakers']:
        return None

    p1_name = partido.get('home_team')
    p2_name = partido.get('away_team')
    if not p1_name or not p2_name:
        return None

    mejores = {p1_name: None, p2_name: None}

    for bookmaker in partido['bookmakers']:
        for market in bookmaker.get('markets', []):
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    name  = outcome['name']
                    price = outcome['price']
                    if name in mejores:
                        if mejores[name] is None or price > mejores[name]:
                            mejores[name] = price

    cuota_p1 = mejores.get(p1_name)
    cuota_p2 = mejores.get(p2_name)

    if cuota_p1 is None or cuota_p2 is None:
        return None

    return {'P1': cuota_p1, 'P2': cuota_p2}