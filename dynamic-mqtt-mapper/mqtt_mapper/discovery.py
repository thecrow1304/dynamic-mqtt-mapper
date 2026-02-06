
import json
import re
from datetime import datetime

_client = None
_prefix = 'homeassistant'

def set_client(client, discovery_prefix='homeassistant'):
    global _client, _prefix
    _client = client
    _prefix = discovery_prefix

def slugify(text: str) -> str:
    text = text or ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9_]+', '_', text)
    text = re.sub(r'__+', '_', text).strip('_')
    return text or 'entity'

def detect_component_and_config(key: str, val: dict):
    if 'valueBoolean' in val:
        comp = 'binary_sensor'
        cfg = {'payload_on': 'ON', 'payload_off': 'OFF'}
        k = key.lower()
        if 'battery' in k:
            cfg['device_class'] = 'battery'
        elif 'leak' in k or 'dry' in k:
            cfg['device_class'] = 'moisture'
        elif 'tamper' in k:
            cfg['device_class'] = 'tamper'
        elif 'temperature' in k:
            cfg['device_class'] = 'heat'
        elif 'reverseflow' in k or 'burst' in k or 'absenceofflow' in k:
            cfg['device_class'] = 'problem'
        return comp, cfg
    if 'valueDate' in val:
        return 'sensor', {'device_class': 'timestamp'}
    if 'valueNumber' in val:
        cfg = {'state_class': 'measurement'}
        unit = (val.get('unit') or '').strip()
        if unit:
            cfg['unit_of_measurement'] = unit
        k = key.lower()
        if 'temperature' in k:
            cfg['device_class'] = 'temperature'
        return 'sensor', cfg
    return 'sensor', {}

def publish_discovery(device_id: str, key: str, val: dict, meta: dict):
    if _client is None:
        return
    comp, extra = detect_component_and_config(key, val)
    config_topic = f"{_prefix}/{comp}/{slugify(device_id)}/{slugify(key)}/config"
    state_topic = f"{_prefix}/{comp}/{slugify(device_id)}/{slugify(key)}/state"

    device = {
        'identifiers': [device_id],
        'name': meta.get('alias') or device_id,
        'manufacturer': meta.get('tenant') or 'Unknown',
        'model': meta.get('type') or 'sensor',
    }

    payload = {
        'name': key,
        'unique_id': f"{slugify(device_id)}_{slugify(key)}",
        'state_topic': state_topic,
        'device': device,
    }
    payload.update(extra)

    _client.publish(config_topic, json.dumps(payload), retain=True)

def publish_state(device_id: str, key: str, val: dict):
    if _client is None:
        return
    comp, _ = detect_component_and_config(key, val)
    state_topic = f"{_prefix}/{comp}/{slugify(device_id)}/{slugify(key)}/state"

    if 'valueBoolean' in val:
        v = val.get('valueBoolean')
        state = 'ON' if bool(v) else 'OFF'
    elif 'valueNumber' in val:
        state = str(val.get('valueNumber'))
    elif 'valueDate' in val:
        iso = val.get('value')
        if isinstance(iso, (int, float)):
            state = datetime.utcfromtimestamp(iso).isoformat() + 'Z'
        else:
            state = str(iso or val.get('valueDate'))
    elif 'valueString' in val:
        state = str(val.get('valueString'))
    else:
        state = str(val.get('value'))

    _client.publish(state_topic, state)
