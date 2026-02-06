FROM python:3.11-slim

WORKDIR /app

# kopiert den Ordner mqtt_mapper (mit __init__.py) in /app/mqtt_mapper
COPY mqtt_mapper ./mqtt_mapper

# statische Web-UI
COPY webui ./webui

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.sh .
RUN sed -i 's/\r$//' /app/run.sh && chmod +x /app/run.sh

EXPOSE 8080

# Fallback: starte immer im Paketkontext
CMD ["python3", "-m", "mqtt_mapper.webserver"]
