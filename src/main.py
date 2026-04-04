import os
import time
from api_handler import obtener_partidos_atp_hoy, extraer_mejores_cuotas
from utils import obtener_datos_jugador_atp
from operador_final import ejecutar_prediccion_maestra
from notificador import enviar_alerta_sniper

# CONFIGURACIÓN DE OPERACIÓN
BANKROLL_TOTAL = 1000  # Marcelo, pon aquí tu saldo real
MIN_EDGE = 0.05        # 5% de ventaja mínima para enviar alerta

def ejecutar_bypass():
    print("\n" + "="*50)
    print("🚀 BYPASS ENGINE: ESCANEANDO MERCADOS ATP...")
    print("="*50)
    
    partidos = obtener_partidos_atp_hoy()
    
    if not partidos:
        print("⏸️ Sin partidos ATP activos en este momento.")
        return

    encontrados = 0
    for p in partidos:
        p1, p2 = p['home_team'], p['away_team']
        
        # 1. Obtener Cuotas Reales (Pinnacle/Bet365)
        odds = extraer_mejores_cuotas(p)
        if not odds: continue
        
        # 2. Obtener ELO Híbrido (Superficie + General)
        elo1, rank1 = obtener_datos_jugador_atp(p1)
        elo2, rank2 = obtener_datos_jugador_atp(p2)
        
        # 3. Predicción del Modelo V3
        res = ejecutar_prediccion_maestra(
            elo_diff = elo1 - elo2,
            rank_diff = rank2 - rank1,
            cuota_p1 = odds['P1'],
            cuota_p2 = odds['P2'],
            bankroll = BANKROLL_TOTAL
        )
        
        # Limpieza de valor para la lógica
        edge_val = float(res['💰 Ventaja Detectada (Edge)'].replace('%','')) / 100
        
        if edge_val >= MIN_EDGE:
            encontrados += 1
            # FORMATO DE ALERTA PARA TELEGRAM
            mensaje = (
                f"🎾 *NUEVA OPORTUNIDAD ATP*\n\n"
                f"🏆 *Partido:* {p1} vs {p2}\n"
                f"📈 *Cuota:* {odds['P1']}\n"
                f"🔥 *Prob. Final:* {res['🔥 Probabilidad Final']}\n"
                f"💰 *VENTAJA (EDGE):* {res['💰 Ventaja Detectada (Edge)']}\n"
                f"💸 *STAKE SUGERIDO:* {res['🚀 Stake Sugerido (Kelly)']}\n\n"
                f"🚀 [BYPASS ACTIVADO]"
            )
            print(f"✅ ¡VALOR ENCONTRADO! Enviando alerta a Telegram...")
            enviar_alerta_sniper(mensaje)
    
    print(f"\nEscaneo finalizado. Oportunidades enviadas: {encontrados}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # El sistema se puede dejar corriendo o ejecutarlo manualmente cada mañana
    ejecutar_bypass()