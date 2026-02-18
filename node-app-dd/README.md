# DD Node Monitor App

Aplicação Node.js simples para você monitorar com o Datadog (APM, métricas e logs).

## Requisitos

- Node.js 18+
- Datadog Agent rodando localmente (APM + DogStatsD)

## Como rodar

```bash
cd node-monitor-app
npm install

# variáveis sugeridas
export DD_SERVICE=dd-node-monitor-app
export DD_ENV=dev
export DD_VERSION=1.0.0
export DD_AGENT_HOST=localhost
export DD_DOGSTATSD_PORT=8125

npm start
```

Acesse:
- `http://localhost:3000/` (endpoint principal)
- `http://localhost:3000/slow?delay=1200` (simula lentidão)
- `http://localhost:3000/error` (simula erro)
- `http://localhost:3000/work?units=10` (simula CPU)

## Rodando com Docker

1. Defina sua API key do Datadog:

```bash
export DD_API_KEY="<sua_api_key>"
```

2. Suba os containers:

```bash
docker compose up --build
```

O app estará disponível em `http://localhost:3000` e enviará traces, métricas e logs para o Agent no container `datadog-agent`.

## Observabilidade no Datadog

- **APM**: o `dd-trace` instrumenta automaticamente o Express.
- **Métricas**: enviadas via DogStatsD (prefixo `dd_node_monitor_app.*`).
- **Logs**: `pino` emite logs estruturados (com `logInjection`).

## Dica

Se quiser rodar tudo via Docker, basta apontar `DD_AGENT_HOST` para o host do Agent.