FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
RUN pip install --no-cache-dir requests

# Instalar cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Criar diretórios
RUN mkdir -p /app/logs /app/data

# Copiar script
COPY api_monitor.py /app/
RUN chmod +x /app/api_monitor.py

# Configurar cron para rodar de hora em hora
RUN echo "0 * * * * python3 /app/api_monitor.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/api-monitor
RUN chmod 0644 /etc/cron.d/api-monitor
RUN crontab /etc/cron.d/api-monitor

# Iniciar cron
CMD ["cron", "-f"]
