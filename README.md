cat <<EOF > README.md

# 🎾 ATP BYPASS ENGINE V3

### _Escáner Automatizado de Valor y Arbitraje Estadístico_

**ATP Bypass Engine** es una infraestructura de software diseñada para detectar ineficiencias en las cuotas del circuito profesional de tenis (ATP). El sistema fusiona el análisis de datos históricos (ELO por superficie) con cuotas en tiempo real de múltiples casas de apuestas para identificar apuestas con un **Edge (ventaja)** superior al 5%.

---

## 🚀 Funcionalidades Clave

- **Escaneo Multitorneo:** Detección dinámica de Sport Keys (Masters 1000, 500, y Grand Slams) vía _The Odds API_.
- **Modelo Predictivo V3:** Algoritmo de **ELO Rating** calibrado específicamente por superficie (Arcilla, Hierba, Dura).
- **Automatización Nube:** Ejecución programada mediante **GitHub Actions** a las 03:00 AM (ECT) para capturar la apertura del mercado europeo.
- **Alertas de Alta Precisión:** Notificaciones instantáneas a Telegram con cálculo automático de **Stake (Criterio de Kelly)**.

---

## 🧠 ¿Cómo calculamos el valor?

El motor no predice ganadores por "intuición", sino por **desviación estadística**.

1.  **Probabilidad Real ($P_{real}$):** Basada en el diferencial de ELO histórico ajustado a la superficie del torneo.
2.  **Probabilidad de Mercado ($P_{mkt}$):** Obtenida mediante la mejor cuota disponible ($C$) en las casas de apuestas monitorizadas.
3.  **Cálculo de Edge:**
    $$Edge = (P_{real} \times C) - 1$$

> **Regla de Ejecución:** Si el **Edge es > 0.05 (5%)**, el sistema dispara una alerta de entrada obligatoria.

---

## 🛠️ Requisitos

- **Python 3.10+**
- **The Odds API Key** (Soporta plan Free y Pro).
- **Telegram Bot Token** & **Chat ID**.
- **Dataset:** Archivo \`atp_limpio.csv\` (Debe generarse con \`generar_features.py\`).

---

## 📦 Instalación y Configuración

### 1. Clonar Repositorio

\`\`\`bash
git clone https://github.com/tu-usuario/atp-bypass-engine.git
cd atp-bypass-engine
pip install -r requirements.txt
\`\`\`

### 2. Configurar Secretos en GitHub

Para la ejecución autónoma, añade estas variables en **Settings > Secrets and variables > Actions**:

| Nombre del Secreto   | Descripción                             |
| :------------------- | :-------------------------------------- |
| \`THE_ODDS_API_KEY\` | Tu API Key de The Odds API              |
| \`TELEGRAM_TOKEN\`   | Token de tu bot de Telegram             |
| \`TELEGRAM_CHAT_ID\` | ID del chat donde recibirás las órdenes |

### 3. Automatización (Cron Job)

Configurado en \`.github/workflows/main_pipeline.yml\`. Por defecto, despierta a las 03:00 AM (Ecuador):
\`\`\`yaml
schedule:

- cron: '0 8 \* \* \*' # 08:00 UTC
  \`\`\`

---

## 📊 Formato de Alerta en Telegram

\`\`\`text
🎯 ORDEN DE ENTRADA: [Nombre del Jugador]
📈 Edge Detectado: +9.7%
💰 Stake Sugerido (Kelly): \$38.00
🏛️ Mejor Cuota: 1.55 (Pinnacle/Bet365)
🎾 Torneo: ATP Monte-Carlo Masters
\`\`\`

---

## ⚖️ Descargo de Responsabilidad

Este software es una herramienta de análisis estadístico basada en datos históricos. El mercado de apuestas conlleva riesgos financieros significativos. El autor no se hace responsable de pérdidas derivadas del uso de este algoritmo. **Apuesta con responsabilidad.**

---

**Desarrollado por:** [Marcelo Ramirez](https://github.com/realwallker)
_Estudiante de Ciencias de la Computación | Especialista en Análisis de Datos Deportivos_
