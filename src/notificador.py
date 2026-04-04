import os
import requests

# El sistema busca primero en las variables de entorno (GitHub Secrets)
# Si no las encuentra (local), puedes poner un valor por defecto para pruebas rápidas
TOKEN = os.getenv('TELEGRAM_TOKEN', '8693720055:AAGQ-wmyJGJSoOmAcqPQzQqMRL3DZRl4YB8')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') 

def enviar_alerta_sniper(mensaje):
    """
    Envía una notificación formateada a Telegram.
    Soporta Markdown para negritas y emojis.
    """
    if not TOKEN or not CHAT_ID:
        print("❌ Error: No se encontraron las credenciales de Telegram (TOKEN o CHAT_ID).")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Alerta enviada a Telegram con éxito.")
        else:
            print(f"⚠️ Fallo al enviar mensaje. Código: {response.status_code}")
            print(f"Respuesta de Telegram: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión al intentar contactar con Telegram: {e}")

if __name__ == "__main__":
    # Prueba rápida de funcionamiento
    test_msg = "🚀 *Bypass ATP Activo*\nSistema de notificaciones operando correctamente."
    enviar_alerta_sniper(test_msg)