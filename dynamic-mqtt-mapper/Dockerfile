
FROM python:3.11-slim

WORKDIR /app

# Copy backend
COPY mqtt_mapper ./mqtt_mapper

# Copy web UI (static, no build step required)
COPY webui ./webui

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.sh .
RUN chmod +x /app/run.sh

EXPOSE 8080
CMD ["/app/run.sh"]
