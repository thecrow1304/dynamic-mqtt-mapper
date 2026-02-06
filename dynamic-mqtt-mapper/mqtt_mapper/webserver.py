
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from .device_manager import devices
from .mqtt_client import start_mqtt
from .settings import LOGGER

app = FastAPI(title="Dynamic MQTT Mapper API")

@app.get('/api/health')
def health():
    return {'status': 'ok'}

@app.get('/api/devices')
def get_devices():
    # Rückgabe aller Geräte
    return devices

# WICHTIG: API zuerst registrieren, dann static mounten, damit /api nicht überschrieben wird
web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'webui'))
if os.path.isdir(web_dir):
    app.mount('/', StaticFiles(directory=web_dir, html=True), name='web')

if __name__ == '__main__':
    # MQTT starten und Webserver starten
    start_mqtt()
    port = int(os.environ.get('PORT', 8080))
    LOGGER.info(f"Starte Webserver auf 0.0.0.0:{port}")
    uvicorn.run(app, host='0.0.0.0', port=port)
