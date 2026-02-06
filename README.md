
# Dynamic MQTT Entity Mapper (Home Assistant Add-on)

Erstellt automatisch **Geräte** und **Entitäten** in Home Assistant aus eingehenden MQTT-Payloads
(z. B. von `physec/.../sensor/<type>/<device>`) und liefert eine **komfortable Web‑UI**.

**Stand:** 2026-02-06T11:18:10.933699Z

## Funktionen

- Automatische Erkennung von Geräten (aus `sensor.deviceId`, `sensor.type`, `sensor.alias` …)
- Automatisches Anlegen von Entitäten via **MQTT Discovery** (`homeassistant/<component>/.../config`)
- Typ‑Erkennung: `valueBoolean` → `binary_sensor`, `valueNumber` → `sensor`, `valueDate` → `sensor (timestamp)`, `valueString` → `sensor`
- Komfortable Web‑UI mit Suche, Filter und Live‑Werten (alle 5 s)
- Konfigurierbares MQTT (Host, Port, Topic, Credentials) und Discovery‑Prefix

## Repository‑Struktur

```
dynamic-mqtt-mapper/
├── dynamic-mqtt-mapper/          # Add-on Ordner (so von HA erkannt)
│   ├── config.json               # Add-on Manifest + Optionen/Schema
│   ├── Dockerfile                # Container-Build
│   ├── requirements.txt          # Python-Abhängigkeiten
│   ├── run.sh                    # Startskript
│   ├── mqtt_mapper/              # Backend
│   │   ├── __init__.py
│   │   ├── settings.py           # Lädt /data/options.json
│   │   ├── mqtt_client.py        # Subscribt MQTT, verteilt Messages
│   │   ├── discovery.py          # MQTT Discovery + States
│   │   ├── device_manager.py     # In-Memory DB
│   │   └── entity_mapper.py      # Mapping-Logik
│   └── webui/                    # Statisches Web-UI (ohne Build)
│       ├── index.html
│       └── assets/{styles.css, app.js}
└── README.md
```

## Installation (Home Assistant OS)

1. Dieses Repo nach GitHub pushen (z. B. `https://github.com/<dein-user>/dynamic-mqtt-mapper`).
2. In Home Assistant: **Einstellungen → Add-ons → Add-on Store → Repositories** und die GitHub‑URL hinzufügen.
3. Das Add‑on **Dynamic MQTT Entity Mapper** auswählen und installieren.
4. In den **Konfigurationen** des Add-ons ggf. anpassen:
   - `mqtt_host` (Standard: `core-mqtt`)
   - `mqtt_port` (1883)
   - `mqtt_username` / `mqtt_password` (falls Broker Auth nutzt)
   - `mqtt_topic` (z. B. `physec/#`)
   - `discovery_prefix` (Standard: `homeassistant`)
5. **Starten** und über die Schaltfläche **Öffnen** (Ingress) die Web‑UI aufrufen.

## Hinweise

- Discovery‑Konfigurationen werden mit `retain=true` veröffentlicht; bei Schema‑Änderungen ggf. HA neu starten oder retained Topics bereinigen.
- Binary‑Sensoren nutzen `ON`/`OFF`. Numerische Sensoren veröffentlichen einfache Strings.
- Zeitstempel erhalten `device_class: timestamp`.

## Troubleshooting

- Keine Geräte sichtbar? Prüfe, ob MQTT‑Pakete das Feld `sensor.deviceId` enthalten.
- Kein Connect zum Broker? Passe `mqtt_host`, `mqtt_port`, `mqtt_username`, `mqtt_password` an.
- Ingress lädt nicht? Alternativ Port 8080 im Netzwerk öffnen und direkt aufrufen.

---

© 2026 Dynamic MQTT Mapper.
