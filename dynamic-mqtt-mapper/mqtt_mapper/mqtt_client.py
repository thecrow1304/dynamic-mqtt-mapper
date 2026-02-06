
import json
import time
import paho.mqtt.client as mqtt
from .settings import CONFIG, LOGGER
from .entity_mapper import handle_mqtt_message, ensure_device_meta
from . import discovery

_client = None

def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        LOGGER.info(f"MQTT verbunden: {CONFIG['mqtt_host']}:{CONFIG['mqtt_port']}")
        client.subscribe(CONFIG['mqtt_topic'])
        LOGGER.info(f"Subscribed auf Topic: {CONFIG['mqtt_topic']}")
    else:
        LOGGER.error(f"MQTT-Connect RC={rc}")

def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode(errors='ignore'))
    except Exception as e:
        LOGGER.warning(f"Ungültiges JSON auf {msg.topic}: {e}")
        return
    # Sicherstellen, dass Device-Metadaten existieren
    ensure_device_meta(payload)
    # Verarbeitung
    try:
        handle_mqtt_message(msg.topic, payload, mqtt_client=client)
    except Exception as e:
        LOGGER.exception(f"Fehler bei handle_mqtt_message: {e}")

def get_client():
    return _client

def start_mqtt():
    global _client
    if _client is not None:
        return _client
    client = mqtt.Client()
    user = CONFIG.get('mqtt_username') or None
    pwd = CONFIG.get('mqtt_password') or None
    if user:
        client.username_pw_set(user, pwd or '')
    client.on_connect = _on_connect
    client.on_message = _on_message

    while True:
        try:
            client.connect(CONFIG['mqtt_host'], int(CONFIG['mqtt_port']))
            break
        except Exception as e:
            LOGGER.warning(f"MQTT nicht erreichbar, neuer Versuch in 5s: {e}")
            time.sleep(5)

    client.loop_start()
    discovery.set_client(client, CONFIG.get('discovery_prefix', 'homeassistant'))
    _client = client
    return client
