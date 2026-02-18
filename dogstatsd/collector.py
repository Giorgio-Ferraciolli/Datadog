import time
import requests
from datadog import initialize, statsd

# Configuração do DogStatsD
options = {
    "statsd_host": "datadog-agent",  # nome do serviço no docker-compose
    "statsd_port": 8125,
}
initialize(**options)

# API pública: Open-Meteo (clima em São Paulo, sem chave)
API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=-23.5505&longitude=-46.6333"
    "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,apparent_temperature"
    "&wind_speed_unit=ms"
)

TAGS = ["city:sao_paulo", "source:open_meteo"]
INTERVAL = 20  # segundos


def fetch_and_send():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})

        temperature      = current.get("temperature_2m")
        humidity         = current.get("relative_humidity_2m")
        wind_speed       = current.get("wind_speed_10m")
        apparent_temp    = current.get("apparent_temperature")

        if temperature is not None:
            statsd.gauge("weather.temperature_celsius", temperature, tags=TAGS)
            print(f"[OK] temperature_celsius = {temperature}")

        if humidity is not None:
            statsd.gauge("weather.humidity_percent", humidity, tags=TAGS)
            print(f"[OK] humidity_percent = {humidity}")

        if wind_speed is not None:
            statsd.gauge("weather.wind_speed_ms", wind_speed, tags=TAGS)
            print(f"[OK] wind_speed_ms = {wind_speed}")

        if apparent_temp is not None:
            statsd.gauge("weather.apparent_temperature_celsius", apparent_temp, tags=TAGS)
            print(f"[OK] apparent_temperature_celsius = {apparent_temp}")

        # Envia um contador de coletas bem-sucedidas
        statsd.increment("weather.collection.success", tags=TAGS)

    except requests.RequestException as e:
        print(f"[ERRO] Falha na requisição: {e}")
        statsd.increment("weather.collection.error", tags=TAGS)


if __name__ == "__main__":
    print("Iniciando coleta de métricas de clima...")
    while True:
        fetch_and_send()
        print(f"Aguardando {INTERVAL}s...\n")
        time.sleep(INTERVAL)
