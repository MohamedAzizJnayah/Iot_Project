import requests
import json
import time
import random

# Essaie d'abord en v3 ; si tu as 404, on passera en v2
DEVICE_NAME = "virtual-json-device"  
EDGEX_URL = f"http://localhost:59986/api/v3/resource/{DEVICE_NAME}/json"

print("🚀 Capteur virtuel EdgeX démarré...\n")

while True:
    temperature = round(random.uniform(20, 32), 2)
    humidity = round(random.uniform(30, 70), 2)
    air_quality = round(random.uniform(0, 200), 2)

    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "air_quality": air_quality
    }

    body = json.dumps(payload)

    r = requests.post(
        EDGEX_URL,
        data=body,
        headers={"Content-Type": "application/json"}
    )

    print("📤 Données envoyées :", payload)
    print("➡ Statut HTTP :", r.status_code, "-", r.text)

    time.sleep(5)