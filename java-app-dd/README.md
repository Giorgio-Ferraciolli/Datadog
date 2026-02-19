# ☕ Java Datadog App

API REST em Java (Spring Boot) com monitoramento completo via **Datadog** — métricas, APM (traces) e coleta de logs — tudo rodando com Docker Compose.

---

## 🗂️ Estrutura do Projeto

```
java-datadog-app/
├── src/
│   └── main/
│       ├── java/com/example/app/
│       │   ├── Application.java          # Entry point Spring Boot
│       │   ├── config/
│       │   │   └── MetricsConfig.java    # Tags globais para todas as métricas
│       │   ├── controller/
│       │   │   ├── ProductController.java # CRUD de produtos + @Timed
│       │   │   └── InfoController.java    # Endpoint /api/info
│       │   ├── model/
│       │   │   └── Product.java          # Entidade produto
│       │   └── service/
│       │       └── ProductService.java   # Lógica de negócio + Counters/Timers/Gauges
│       └── resources/
│           └── application.yml          # Config Spring + StatsD export
├── Dockerfile                            # Multi-stage build + dd-java-agent
├── docker-compose.yml                    # App + Datadog Agent
├── .env.example                          # Template da API Key
├── .gitignore
└── README.md
```

---

## 🚀 Como Subir

### 1. Pré-requisitos
- Docker e Docker Compose instalados
- Conta no [Datadog](https://www.datadoghq.com/) (tem trial grátis)

### 2. Configure a API Key

```bash
cp .env.example .env
# Edite .env e coloque sua DD_API_KEY
# Obtenha em: https://app.datadoghq.com/organization-settings/api-keys
```

### 3. Suba os containers

```bash
docker compose up --build
```

### 4. Teste a API

```bash
# Listar produtos
curl http://localhost:8080/api/products

# Buscar por ID
curl http://localhost:8080/api/products/1

# Criar produto
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Mouse Gamer","description":"1600 DPI","price":199.90,"stock":30}'

# Atualizar
curl -X PUT http://localhost:8080/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Notebook Pro Max","description":"Atualizado","price":5999.99,"stock":8}'

# Deletar
curl -X DELETE http://localhost:8080/api/products/2

# Info da aplicação
curl http://localhost:8080/api/info

# Health check
curl http://localhost:8080/actuator/health
```

---

## 📊 O que aparece no Datadog

### Métricas Customizadas (DogStatsD via Micrometer)
| Métrica | Tipo | Descrição |
|---|---|---|
| `app.products.created` | Counter | Produtos criados |
| `app.products.deleted` | Counter | Produtos deletados |
| `app.products.not_found` | Counter | Buscas sem resultado |
| `app.products.find.duration` | Timer | Latência da busca por ID |
| `app.products.total` | Gauge | Total de produtos em memória |
| `app.http.products.*` | Timer | Latência de cada endpoint HTTP |

### APM — Rastreamento (dd-java-agent)
- Traces automáticos de **todas as requisições HTTP**
- Flame graphs mostrando tempo em cada método
- Integração automática com Spring MVC, logs, etc.

### Tags Globais
Todas as métricas carregam as tags:
- `env`: ambiente (production/local)
- `version`: versão da aplicação
- `service`: java-datadog-app
- `team`: backend

### Logs
Os logs da aplicação são coletados automaticamente pelo Datadog Agent e aparecem em **Logs > Explorer** com correlação direta aos traces.

---

## 🔍 Onde ver no Datadog

| O que | Onde no Datadog |
|---|---|
| Métricas | Metrics > Explorer → busque por `app.*` |
| Dashboard de infra | Infrastructure > Containers |
| APM / Traces | APM > Traces |
| Logs | Logs > Explorer |
| Service Map | APM > Service Map |

---

## 🛠️ Variáveis de Ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DD_API_KEY` | — | **Obrigatória.** API Key do Datadog |
| `DD_SITE` | `datadoghq.com` | Site do Datadog (use `datadoghq.eu` para EU) |
| `DD_ENV` | `production` | Ambiente |
| `DD_SERVICE` | `java-datadog-app` | Nome do serviço no APM |
| `APP_ENV` | `local` | Passado para a aplicação Spring |
