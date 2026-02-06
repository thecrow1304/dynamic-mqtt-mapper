
import json, os, logging

DEFAULTS = {
    "mqtt_host": "core-mqtt",
    "mqtt_port": 1883,
    "mqtt_username": "",
    "mqtt_password": "",
    "mqtt_topic": "physec/#",
    "discovery_prefix": "homeassistant",
    "log_level": "INFO"
}

def load_options():
    path = "/data/options.json"
    opts = {}
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                opts = json.load(f)
    except Exception:
        opts = {}
    cfg = {k: opts.get(k, DEFAULTS[k]) for k in DEFAULTS}
    return cfg

CONFIG = load_options()

level = CONFIG.get("log_level", "INFO").upper()
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=getattr(logging, level, logging.INFO))
LOGGER = logging.getLogger("mqtt_mapper")
