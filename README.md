🌐 IoT Demo – Virtual Sensor + ThingsBoard Cloud

Simulation d’un flux IoT complet : télémétrie → dashboard → RPC → comportement dynamique

📌 Résumé du projet

Cette démonstration illustre un mini-flux IoT complet basé sur ThingsBoard Cloud et un capteur virtuel écrit en Python.
Le capteur envoie régulièrement des mesures simulées (température, humidité, AQI, mode), qui sont affichées dans un tableau de bord ThingsBoard.
Le dashboard peut également envoyer une commande descendante (RPC) au capteur afin de modifier son comportement.

Cycle complet obtenu :

Capteur virtuel → Cloud (MQTT) → Dashboard → Commande RPC → Capteur mis à jour

📁 Contenu de la démo

✔ Script Python simulant un capteur IoT (télémétrie + réception RPC)

✔ Dashboard ThingsBoard avec :

Time-series chart (humidité)

Jauge température

Carte AQI

Carte du mode actuel

Bouton RPC “Send” (eco/normal)

✔ Schéma d’architecture

✔ Captures d’écran du dashboard

✔ Instructions pas-à-pas pour reproduire la démo

🏗️ Architecture globale

          ┌──────────────────────────┐
          │   Script Python (MQTT)   │
          │  ✔ Télémétrie            │
          │  ✔ Réception RPC         │
          └──────────────┬───────────┘
                         MQTT
                           ↓
            ┌────────────────────────┐
            │  ThingsBoard Cloud     │
            │  ✔ Device + Token      │
            │  ✔ Dashboard           │
            │  ✔ RPC (downlink)      │
            └──────────────┬─────────┘
                           ↓
                Visualisation + Actions

🚀 1. Pré-requis
✔ Python 3.8+
✔ Installer les dépendances :
pip install paho-mqtt

✔ Un compte ThingsBoard Cloud

👉 https://thingsboard.cloud

(création gratuite)

🔧 2. Configuration côté ThingsBoard Cloud
2.1. Créer un nouvel appareil (Device)

Devices → Add new device

Nom : virtual-env-sensor

Type : default

2.2. Récupérer l’access token

Device → Tab "Credentials" → copier le token.

Tu dois remplacer dans le script :

ACCESS_TOKEN = "TON_TOKEN_ICI"

2.3. Créer un Dashboard

Tu peux importer ou créer un dashboard contenant :

Time Series Chart (humidity)

Gauge (temperature)

Entity value card (air_quality)

Text card (mode)

Bouton RPC :

Type : Send RPC

Méthode : setState

Params : "eco" ou "normal"

🖥 3. Script Python du capteur virtuel

📌 Ce script :

génère température, humidité, AQI

publie la télémétrie toutes les 5 secondes

écoute les commandes RPC (setState)

modifie le mode si demandé

import paho.mqtt.client as mqtt
import time
import json
import random

ACCESS_TOKEN = " ................"  # Ton token

broker = "mqtt.thingsboard.cloud"
port = 1883

client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

# Variable globale pour le mode
mode = "normal"

# ---- Réception RPC ----
def on_message(client, userdata, msg):
    global mode
    
    data = json.loads(msg.payload.decode())
    method = data.get("method")
    params = data.get("params")

    print("\n🔽 RPC reçu !")
    print("➡ Méthode :", method)
    print("➡ Paramètre :", params)

    # Si la commande RPC demande de changer l'état
    if method == "setState":
        mode = params
        print("⚙️ Nouveau mode :", mode)

        # Réponse RPC (optionnelle)
        response = {"updatedMode": mode}
        client.publish(msg.topic.replace("request", "response"), json.dumps(response))
        print("📤 RPC réponse envoyée :", response)


client.on_message = on_message

client.connect(broker, port, keepalive=60)

# Abonnement RPC
client.subscribe("v1/devices/me/rpc/request/+")
client.loop_start()

print("🚀 Capteur virtuel démarré...\n")

# Boucle d'envoi de données
while True:
    temperature = round(random.uniform(20, 32), 2)
    humidity = round(random.uniform(30, 70), 2)
    air_quality = round(random.uniform(0, 200), 2)

    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "air_quality": air_quality,
        "mode": mode
    }

    client.publish("v1/devices/me/telemetry", json.dumps(payload))
    print("📤 Données envoyées :", payload)

    time.sleep(5)

▶️ 4. Exécution de la simulation

Dans le terminal :

python virtual_sensor.py


Tu verras :

📤 Données envoyées : {'temperature': 25.3, 'humidity': 65.1, 'air_quality': 88, 'mode': 'normal'}


Et lorsqu'un RPC est envoyé :

🔽 RPC reçu !
➡ Méthode : setState
➡ Paramètre : eco
⚙️ Nouveau mode : eco
📤 RPC réponse envoyée : {'updatedMode': 'eco'}

📊 5. Résultat côté dashboard
✔ Mise à jour en temps réel

Humidité → graphe temporel

Température → jauge

AQI → card numérique

Mode → card texte

✔ Interaction via RPC

En cliquant sur Send → le capteur change son mode immédiatement.

📷 6. Captures d’écran

Ajoute ici tes photos :
/images/dashboard.jpeg
/images/rpc_button.png

🧪 7. Tests réalisés

✔ Connexion MQTT → OK

✔ Télémétrie envoyée toutes les 5s

✔ Dashboard reçoit en live

✔ RPC bidirectionnel fonctionnel

✔ Mode mis à jour dynamiquement

📦 8. Structure du repository
📁 project-root
│── README.md
│── virtual_sensor.py
│── images/
│     ├── dashboard.jpeg
│     └── rpc_button.png

📝 9. Conclusion

Cette démonstration fournit une implémentation complète d’un flux IoT moderne basé sur ThingsBoard Cloud, incluant :

✓ génération de données
✓ transmission MQTT
✓ visualisation temps réel
✓ RPC descendant
✓ modification dynamique du comportement du device
