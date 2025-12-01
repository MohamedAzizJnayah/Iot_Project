import paho.mqtt.client as mqtt
import time
import json
import random

ACCESS_TOKEN = "8OlcU7yAUdbmgsUSpdau"  # Ton token

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
