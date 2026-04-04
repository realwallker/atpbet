import os
from api_handler import obtener_partidos_atp_hoy, extraer_mejores_cuotas
from utils import obtener_datos_jugador_atp
from operador_final import ejecutar_prediccion_maestra
from notificador import enviar_alerta_sniper

# CONFIGURACIÓN DE OPERACIÓN
BANKROLL_TOTAL = 1000  # Pon aquí tu saldo real
MIN_EDGE = 0.05        # 5% de ventaja mínima para enviar alerta
ELO_DEFAULT = 1500     # Valor que devuelve utils.py cuando no encuentra al jugador


def ejecutar_bypass():
    print("\n" + "=" * 50)
    print("🚀 BYPASS ENGINE: ESCANEANDO MERCADOS ATP...")
    print("=" * 50)

    # Verificar que los archivos necesarios existen antes de empezar
    model_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "modelo_v2.pkl")
    features_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "atp_features.csv")

    if not os.path.exists(model_path):
        print("❌ ERROR CRÍTICO: modelo_v2.pkl no encontrado.")
        print("   Ejecuta primero el paso de entrenamiento o descarga el artifact.")
        return

    if not os.path.exists(features_path):
        print("⚠️  ADVERTENCIA: atp_features.csv no encontrado.")
        print("   Los ELOs de los jugadores usarán valores por defecto (1500).")
        print("   Esto reducirá significativamente la precisión del scanner.")

    partidos = obtener_partidos_atp_hoy()

    if not partidos:
        print("⏸️  Sin partidos ATP activos en este momento.")
        return

    print(f"\n📋 Analizando {len(partidos)} partidos encontrados...\n")

    encontrados = 0
    sin_cuotas = 0
    elo_default = 0
    errores = 0

    for p in partidos:
        p1 = p['home_team']
        p2 = p['away_team']

        # 1. Obtener cuotas
        odds = extraer_mejores_cuotas(p)
        if not odds:
            sin_cuotas += 1
            continue

        # 2. Obtener ELO de cada jugador
        elo1, rank1 = obtener_datos_jugador_atp(p1)
        elo2, rank2 = obtener_datos_jugador_atp(p2)

        # Si ambos jugadores tienen ELO por defecto, el modelo no tiene info útil
        # y producirá predicciones sin valor real → saltamos el partido
        if elo1 == ELO_DEFAULT and elo2 == ELO_DEFAULT:
            elo_default += 1
            print(f"   ⏭️  {p1} vs {p2} — jugadores no encontrados en dataset, se omite")
            continue

        # 3. Calcular predicción
        try:
            res = ejecutar_prediccion_maestra(
                elo_diff=elo1 - elo2,
                rank_diff=rank2 - rank1,
                cuota_p1=odds['P1'],
                cuota_p2=odds['P2'],
                bankroll=BANKROLL_TOTAL
            )
        except Exception as e:
            errores += 1
            print(f"   ❌ Error procesando {p1} vs {p2}: {e}")
            continue

        # 4. Evaluar edge
        edge_str = res['💰 Ventaja Detectada (Edge)']           # ej: "9.70%"
        edge_val = float(edge_str.replace('%', '')) / 100       # → 0.097

        prob_str  = res['🔥 Probabilidad Final']
        stake_str = res['🚀 Stake Sugerido (Kelly)']

        print(f"   📊 {p1} vs {p2}")
        print(f"       ELO diff: {elo1 - elo2:+.0f} | Cuota P1: {odds['P1']} | Prob: {prob_str} | Edge: {edge_str}")

        if edge_val >= MIN_EDGE:
            encontrados += 1
            mensaje = (
                f"🎾 *NUEVA OPORTUNIDAD ATP*\n\n"
                f"🏆 *Partido:* {p1} vs {p2}\n"
                f"📈 *Cuota:* {odds['P1']}\n"
                f"🔥 *Prob. Final:* {prob_str}\n"
                f"💰 *VENTAJA (EDGE):* {edge_str}\n"
                f"💸 *STAKE SUGERIDO:* {stake_str}\n\n"
                f"🚀 [BYPASS ACTIVADO]"
            )
            print(f"   ✅ ¡VALOR ENCONTRADO! Enviando alerta a Telegram...")
            enviar_alerta_sniper(mensaje)

    # Resumen final
    print("\n" + "=" * 50)
    print(f"✅ Oportunidades enviadas : {encontrados}")
    print(f"⏭️  Omitidos (ELO default) : {elo_default}")
    print(f"⚠️  Sin cuotas disponibles : {sin_cuotas}")
    print(f"❌ Errores de predicción   : {errores}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    ejecutar_bypass()