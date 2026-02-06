
from datetime import datetime
from .device_manager import devices
from .settings import LOGGER
from .discovery import publish_discovery, publish_state

def ensure_device_meta(payload: dict):
    sensor = payload.get('sensor', {})
    device_id = sensor.get('deviceId')
    if not device_id:
        return
    if device_id not in devices:
        devices[device_id] = {
            'meta': {
                'type': sensor.get('type'),
                'alias': sensor.get('alias'),
                'tenant': sensor.get('tenant'),
                'address': sensor.get('address'),
            },
            'entities': {}
        }
    else:
        meta = devices[device_id].get('meta', {})
        for k in ('type','alias','tenant','address'):
            v = sensor.get(k)
            if v:
                meta[k] = v
        devices[device_id]['meta'] = meta

def handle_mqtt_message(topic: str, payload: dict, mqtt_client=None):
    sensor = payload.get('sensor', {})
    message = payload.get('message', {})
    device_id = sensor.get('deviceId')
    if not device_id:
        return

    if device_id not in devices:
        ensure_device_meta(payload)

    device = devices[device_id]
    meta = device.get('meta', {})

    for key, val in message.items():
        entity_rec = device['entities'].get(key, {})
        entity_rec['raw'] = val
        entity_rec['updated'] = datetime.utcnow().isoformat() + 'Z'

        if 'valueBoolean' in val:
            entity_rec['type'] = 'binary_sensor'
            entity_rec['last_value'] = bool(val.get('valueBoolean'))
        elif 'valueNumber' in val:
            entity_rec['type'] = 'sensor'
            entity_rec['last_value'] = val.get('valueNumber')
            if val.get('unit'):
                entity_rec['unit'] = val.get('unit')
        elif 'valueDate' in val:
            entity_rec['type'] = 'sensor(timestamp)'
            entity_rec['last_value'] = val.get('value') or val.get('valueDate')
        elif 'valueString' in val:
            entity_rec['type'] = 'sensor'
            entity_rec['last_value'] = val.get('valueString')
        else:
            entity_rec['type'] = 'sensor'
            entity_rec['last_value'] = val.get('value')

        device['entities'][key] = entity_rec

        try:
            publish_discovery(device_id, key, val, meta)
            publish_state(device_id, key, val)
        except Exception as e:
            LOGGER.warning(f"Fehler beim Publish Discovery/State: {e}")
