# Weather Metrics Collector → Datadog

Coleta métricas de clima de São Paulo via [Open-Meteo](https://open-meteo.com/) e envia ao Datadog via DogStatsD. Roda em Docker e coleta a cada 20 segundos.

## Métricas coletadas

| Métrica | Descrição |
|---|---|
| `weather.temperature_celsius` | Temperatura atual |
| `weather.humidity_percent` | Umidade relativa |
| `weather.wind_speed_ms` | Velocidade do vento (m/s) |
| `weather.apparent_temperature_celsius` | Sensação térmica |
| `weather.collection.success` | Coletas bem-sucedidas |
| `weather.collection.error` | Falhas na coleta |

## Requisitos

- Docker e Docker Compose instalados
- API Key do Datadog

## Como rodar

```bash
# 1. Clone o projeto e entre na pasta
cd datadog-metrics

# 2. Configure sua API key
cp .env.example .env
# edite o .env e coloque sua DD_API_KEY

# 3. Suba os containers
docker compose up --build
```

## Estrutura

```
.
├── collector.py        # Script principal
├── Dockerfile          # Imagem do collector
├── docker-compose.yml  # Datadog Agent + Collector
├── requirements.txt    # Dependências Python
└── .env.example        # Template de variáveis de ambiente
```

## Onde encontrar sua API Key

Acesse o Datadog → **Organization Settings → API Keys**.
