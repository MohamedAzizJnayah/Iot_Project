# dashboard_edgex.py

import json
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh   # pip install streamlit-autorefresh

# ⚙️ Paramètres EdgeX
EDGEX_BASE = "http://localhost:59880"
DEVICE_NAME = "virtual-json-device"  # adapte si besoin
API_VERSION = "v3"                    # si 404, essaie "v2"

EVENT_URL = f"{EDGEX_BASE}/api/{API_VERSION}/event/device/name/{DEVICE_NAME}?limit=50"


def fetch_events():
    """
    Récupère les derniers events EdgeX pour le device.
    Retourne un DataFrame avec time, temperature, humidity, air_quality.
    """
    try:
        r = requests.get(EVENT_URL, timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        st.error(f"Erreur lors de l'appel EdgeX : {e}")
        return pd.DataFrame(columns=["time", "temperature", "humidity", "air_quality"])

    events = data.get("events", [])
    rows = []

    for ev in events:
        origin_ns = ev.get("origin")
        if origin_ns is None:
            origin_ns = ev.get("readings", [{}])[0].get("origin")

        if origin_ns:
            ts = datetime.fromtimestamp(origin_ns / 1e9)
        else:
            ts = None

        for reading in ev.get("readings", []):
            if reading.get("resourceName") != "json":
                continue

            raw_value = reading.get("value", "")

            try:
                payload = json.loads(raw_value)
            except Exception:
                continue

            rows.append(
                {
                    "time": ts,
                    "temperature": payload.get("temperature"),
                    "humidity": payload.get("humidity"),
                    "air_quality": payload.get("air_quality"),
                }
            )

    if not rows:
        return pd.DataFrame(columns=["time", "temperature", "humidity", "air_quality"])

    df = pd.DataFrame(rows).dropna(subset=["time"]).sort_values("time")
    return df


# 🎨 Mise en page Streamlit
st.set_page_config(
    page_title="EdgeX Virtual Sensor Dashboard",
    layout="wide",
)

# 👉 Texte en blanc sur fond sombre
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 🔁 Auto-refresh toutes les 3 secondes (temps réel)
st_autorefresh(interval=3000, key="edge-refresh")

st.title("📊 EdgeX Virtual Sensor Dashboard")
st.caption(f"Device : {DEVICE_NAME} – Source : EdgeX Core Data ({API_VERSION})")

# Afficher l'heure de la dernière mise à jour pour vérifier que ça tourne
st.write("🕒 Dernière mise à jour :", datetime.now().strftime("%H:%M:%S"))

# Récupération des données
df = fetch_events()

if df.empty:
    st.warning("Aucune donnée récupérée. Vérifie que le script capteur tourne et que les events arrivent dans EdgeX.")
    st.stop()

# 🔹 On prend seulement la DERNIÈRE mesure (la plus récente)
latest = df.sort_values("time").iloc[-1]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🌡️ Température (°C)",
        value=f"{latest['temperature']:.2f}" if latest["temperature"] is not None else "N/A",
    )

with col2:
    st.metric(
        label="💧 Humidité (%)",
        value=f"{latest['humidity']:.2f}" if latest["humidity"] is not None else "N/A",
    )

with col3:
    st.metric(
        label="🌫️ Qualité de l’air (index)",
        value=f"{latest['air_quality']:.2f}" if latest["air_quality"] is not None else "N/A",
    )

st.markdown("---")

# 📊 Graphiques + tableau
tab1, tab2 = st.tabs(["📈 Évolution des mesures", "📃 Données brutes"])

with tab1:
    st.subheader("Évolution dans le temps")
    df_plot = df.set_index("time")
    st.line_chart(df_plot[["temperature", "humidity", "air_quality"]])

with tab2:
    st.subheader("Dernières mesures")
    st.dataframe(df.sort_values("time", ascending=False).reset_index(drop=True))

st.caption("Mise à jour automatique toutes les 3 secondes (si de nouvelles mesures sont publiées).")