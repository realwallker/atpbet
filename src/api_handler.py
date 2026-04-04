import os
import requests

API_KEY = os.getenv('ad819a411d29160fddf766f7f5aade0b')

# Esto nos dirá si la llave tiene la longitud correcta (una clave de The Odds suele tener 32 caracteres)
if API_KEY:
    print(f"DEBUG: Longitud de la clave recibida: {len(API_KEY)}")
else:
    print("DEBUG: No se recibió ninguna clave.")

API_KEY = os.getenv('ad819a411d29160fddf766f7f5aade0b') 
BASE_URL = 'https://api.the-odds-api.com/v4/sports'

def obtener_partidos_atp_hoy():
    # Solo buscamos la llave de tenis masculino
    sport_key = 'tennis_atp'
    url = f"{BASE_URL}/{sport_key}/odds"
    
    params = {
        'apiKey': API_KEY,
        'regions': 'eu',
        'markets': 'h2h',
        'bookmakers': 'pinnacle,bet365',
        'oddsFormat': 'decimal'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 404:
        print("⏸️ No hay torneos ATP activos en este momento.")
        return []
        
    if response.status_code != 200:
        print(f"❌ Error API: {response.status_code}")
        return []
    
    return response.json()

def extraer_mejores_cuotas(partido):
    home_team = partido['home_team']
    cuotas = {}
    
    # Prioridad absoluta a Pinnacle por su exactitud
    bookmakers = {bm['key']: bm for bm in partido['bookmakers']}
    
    selected_bm = None
    if 'pinnacle' in bookmakers:
        selected_bm = bookmakers['pinnacle']
    elif 'bet365' in bookmakers:
        selected_bm = bookmakers['bet365']
        
    if selected_bm:
        outcomes = selected_bm['markets'][0]['outcomes']
        for opt in outcomes:
            if opt['name'] == home_team:
                cuotas['P1'] = opt['price']
            else:
                cuotas['P2'] = opt['price']
    
    return cuotas