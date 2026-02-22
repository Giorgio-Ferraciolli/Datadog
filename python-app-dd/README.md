# FastAPI + Datadog — Demo de Observabilidade

Aplicação mínima em **Python 3.11 + FastAPI** totalmente containerizada, com
**traces, logs estruturados e métricas customizadas** enviados ao Datadog via
`ddtrace` e `DogStatsD`.

---

## Estrutura do projeto

```
datadog-fastapi/
├── backend/
│   ├── main.py            # Aplicação FastAPI
│   ├── requirements.txt
│   └── Dockerfile
├── datadog/
│   └── conf.d/            # Configs extras para o Datadog Agent (opcional)
├── docker-compose.yml
├── .env.example           # Template de variáveis de ambiente
└── README.md
```

---

## Pré-requisitos

| Ferramenta | Versão mínima |
|---|---|
| Docker | 24+ |
| Docker Compose | v2 (plugin) |
| Conta Datadog | API Key válida |

---

## Início rápido

### 1. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite .env e preencha DATADOG_API_KEY e demais valores
```

### 2. Suba os containers

```bash
docker compose up --build
```

### 3. Faça requisições de teste

```bash
# Verifica saúde da aplicação
curl http://localhost:8000/health

# Gera trace, log e métricas customizadas
curl http://localhost:8000/test
```

---

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/health` | Health check — retorna status e metadados |
| `GET` | `/test` | Gera trace ativo, log estruturado e 3 métricas StatsD |
| `GET` | `/docs` | Swagger UI (automático do FastAPI) |

### Exemplo de resposta — `/test`

```json
{
  "status": "ok",
  "message": "Trace, log e métricas enviados ao Datadog com sucesso!",
  "trace_id": "7234103498630737845",
  "span_id":  "4512098765432100",
  "simulated_latency_ms": 87.3,
  "timestamp": "2024-06-01T12:00:00.000000"
}
```

---

## O que é enviado ao Datadog?

### Traces (APM)
- Span automático de cada requisição HTTP (via `ddtrace-run` + `patch_all()`)
- Span manual `app.test.operation` com tags customizadas no `/test`

### Logs
- Logs estruturados em JSON com **injeção automática** de `dd.trace_id` e `dd.span_id`
- Correlação automática entre logs e traces no Datadog

### Métricas (DogStatsD → porta 8125)

| Métrica | Tipo | Descrição |
|---|---|---|
| `app.request.duration_ms` | Histogram | Latência de cada endpoint |
| `app.test.requests_total` | Counter | Total de chamadas a `/test` |
| `app.test.simulated_latency_ms` | Histogram | Latência simulada no `/test` |
| `app.test.random_value` | Gauge | Valor aleatório por requisição |

---

## Variáveis de ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `DATADOG_API_KEY` | ✅ | — | API Key do Datadog |
| `DATADOG_SITE` | ✅ | `datadoghq.com` | Site do Datadog (região) |
| `DD_SERVICE` | — | `fastapi-datadog` | Nome do serviço no APM |
| `DD_ENV` | — | `development` | Ambiente (dev/staging/prod) |
| `DD_VERSION` | — | `1.0.0` | Versão do serviço |

---

## Verificar no Datadog

Após algumas requisições, acesse:

- **APM → Services** → procure por `fastapi-datadog`
- **APM → Traces** → filtre por `service:fastapi-datadog`
- **Metrics Explorer** → busque `app.test.*` ou `app.request.*`
- **Logs** → filtre por `service:fastapi-datadog`

---

## Parar os containers

```bash
docker compose down
```
