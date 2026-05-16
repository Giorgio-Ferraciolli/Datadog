# Datadog Node.js App

Aplicação Node.js totalmente instrumentada com **Datadog APM**, **profiling contínuo**, **runtime metrics**, **métricas customizadas via DogStatsD** e **logs estruturados em JSON com correlação de traces**.

O projeto é 100% containerizado — **o único pré-requisito é ter Docker instalado**. Você não precisa de Node.js, npm ou qualquer outra ferramenta na sua máquina.

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) (Engine 20.10+)
- [Docker Compose v2](https://docs.docker.com/compose/install/) (já vem no Docker Desktop; no Linux, instale o pacote `docker-compose-plugin`)
- Uma conta Datadog e uma API key — gere a sua em <https://app.datadoghq.com/organization-settings/api-keys>

---

## Início rápido

```bash
# 1. Copie o template de variáveis de ambiente
cp .env.example .env

# 2. Edite o .env e coloque sua DD_API_KEY real.
#    Ajuste DD_SITE se sua conta não estiver na região US1 (ex: datadoghq.eu para EU1).
$EDITOR .env

# 3. Suba os containers
docker compose up --build
```

Pronto. A aplicação fica escutando em <http://localhost:3000> e já começa a enviar dados para o Datadog.

Para rodar em background:

```bash
docker compose up --build -d
docker compose logs -f app
```

Para parar e limpar tudo:

```bash
docker compose down
```

---

## Testando os endpoints

```bash
# Health
curl http://localhost:3000/health

# Users — gera um span customizado, latência artificial e atualiza o gauge de fila
curl 'http://localhost:3000/users?user_id=u-42'

# Cria uma ordem — gera tags de negócio e incrementa um counter customizado
curl -X POST http://localhost:3000/orders \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u-42","product":"widget-001","amount":129.9}'

# Força um erro para exercitar o pipeline de tratamento de erros
curl -X POST 'http://localhost:3000/orders?fail=true' \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u-42","product":"widget-001"}'
```

Gere um pouco de tráfego para popular os dashboards:

```bash
for i in $(seq 1 50); do
  curl -s http://localhost:3000/users > /dev/null
  curl -s -X POST http://localhost:3000/orders \
    -H 'Content-Type: application/json' \
    -d '{"user_id":"u-'$i'","product":"widget-001"}' > /dev/null
  # 1 em cada 5 falha de propósito
  if [ $((i % 5)) -eq 0 ]; then
    curl -s -X POST 'http://localhost:3000/orders?fail=true' \
      -H 'Content-Type: application/json' -d '{}' > /dev/null
  fi
done
```

> Dica: o script `load.sh` (na raiz do repo, se incluído) faz isso continuamente com distribuição aleatória entre os endpoints — útil para encher os gráficos com dados realistas.

---

## Verificando no Datadog

Aguarde ~1–2 minutos após as primeiras requisições para os dados aparecerem.

### Traces no APM

1. Abra **APM → Services** no Datadog: <https://app.datadoghq.com/apm/services>
2. Filtre por `env:development` (ou o valor que você colocou em `DD_ENV`).
3. O service `datadog-node-app` deve aparecer na lista.
4. Clique nele e abra **Traces** para inspecionar requisições individuais. Cada chamada em `/users` mostra um span filho `db.query.users` e cada `/orders` mostra um `payment.process`. Requisições com erro vêm marcadas com o indicador de erro e a tag `error.message` anexada.

### Profiling contínuo

1. Abra **APM → Profiling → Profiles**: <https://app.datadoghq.com/profiling>
2. Filtre por `service:datadog-node-app`.
3. Perfis de CPU, wall-time e heap são enviados a cada minuto.

### Métricas customizadas no Metrics Explorer

1. Abra **Metrics → Explorer**: <https://app.datadoghq.com/metric/explorer>
2. A aplicação emite estas métricas customizadas (todas com prefixo `app.`):

| Métrica                          | Tipo      | Tags                                            |
|----------------------------------|-----------|-------------------------------------------------|
| `app.requests.count`             | counter   | `endpoint`, `method`, `status_code`, `service`, `env`, `version` |
| `app.requests.latency`           | histogram | mesmas tags acima                               |
| `app.queue.pending_jobs`         | gauge     | `service`, `env`, `version`                     |
| `app.orders.created`             | counter   | `product`, `user_id`, `service`, `env`, `version` |
| `app.errors.count`               | counter   | `endpoint`, `method`, `error_type`              |
| `app.process.uncaught_exception` | counter   | `error_type`                                    |
| `app.process.unhandled_rejection`| counter   | `error_type`                                    |

   Experimente: `avg:app.requests.latency{service:datadog-node-app}` agrupado por `endpoint`.

### Runtime metrics

As métricas de runtime aparecem com o prefixo `runtime.node.*` (event loop lag, GC, uso de heap, etc.). Pesquise `runtime.node` no Metrics Explorer e filtre por `service:datadog-node-app`.

### Logs

1. Abra **Logs → Live Tail**: <https://app.datadoghq.com/logs/livetail>
2. Filtre por `service:datadog-node-app`.
3. Cada linha de log é um JSON e carrega `dd.trace_id` / `dd.span_id`, então é possível clicar e ir direto para o trace correspondente no APM.

---

## Estrutura do projeto

```
.
├── Dockerfile                  # Build multi-stage (build + runtime)
├── docker-compose.yml          # Serviços: app + datadog-agent
├── .env.example                # Template das variáveis de ambiente
├── package.json
└── src/
    ├── tracer.js               # Entry point — inicializa dd-trace ANTES de tudo
    ├── app.js                  # Bootstrap do Express, middlewares e error handlers
    ├── config/
    │   └── index.js            # Leitura centralizada de variáveis de ambiente
    ├── middleware/
    │   ├── requestMetrics.js   # Counter de requisições + histograma de latência
    │   └── errorHandler.js     # Marca o span como erro, gera log e métrica
    ├── routes/
    │   ├── health.js           # GET /health
    │   ├── users.js            # GET /users — span customizado + gauge de fila
    │   └── orders.js           # POST /orders — tags de negócio, ?fail=true
    └── utils/
        ├── logger.js           # pino, JSON, correlacionado com traces
        └── metrics.js          # Wrapper do hot-shots (DogStatsD)
```

---

## Trocando de ambiente Datadog

Para apontar a aplicação para outra conta Datadog (ou outra região), edite o `.env`:

```bash
DD_API_KEY=sua_nova_chave
DD_SITE=datadoghq.com   # ou datadoghq.eu, us5.datadoghq.com etc.
```

E reinicie apenas o agent (a app não precisa reiniciar):

```bash
docker compose up -d --force-recreate datadog-agent
```

Sites comuns:

| Região | `DD_SITE`                |
|--------|--------------------------|
| US1    | `datadoghq.com`          |
| US3    | `us3.datadoghq.com`      |
| US5    | `us5.datadoghq.com`      |
| EU1    | `datadoghq.eu`           |
| AP1    | `ap1.datadoghq.com`      |

Para descobrir o site da sua conta, olhe a URL do Datadog no navegador depois de logar.

---

## Solução de problemas

**O agent encerra imediatamente com a mensagem `DD_API_KEY is required`.**
Configure a `DD_API_KEY` no `.env`. O Compose se recusa a subir sem ela.

**Nenhum trace aparece na UI do Datadog.**
- Verifique se o agent está saudável: `docker compose logs datadog-agent | grep -i "agent.*started"`
- Confirme que `DD_SITE` bate com a região da sua conta (usuários EU precisam de `datadoghq.eu`).
- Confira o status do APM no agent:
  ```bash
  docker exec datadog-agent agent status | grep -A 10 "APM Agent"
  ```
- Dentro do container da app, o agent precisa estar acessível em `datadog-agent:8126`. A rede do Compose já cuida disso automaticamente.

**Erro ao subir: `failed to bind host port 0.0.0.0:8125/udp: address already in use`.**
Significa que outro processo (talvez outro agent Datadog rodando no host) já está usando essa porta. Soluções:
- Remova o bloco `ports:` do serviço `datadog-agent` no `docker-compose.yml` (a app se comunica com o agent pela rede interna do Compose, então a porta exposta não é necessária).
- Ou remapeie para uma porta livre no host (mantenha o lado interno em 8125):
  ```yaml
  ports:
    - "28125:8125/udp"
    - "8126:8126/tcp"
  ```

**As métricas aparecem mas os logs não.**
A coleta de logs de containers no Datadog precisa de `DD_LOGS_ENABLED=true` e acesso de leitura ao `/var/run/docker.sock`. Os dois já estão configurados no `docker-compose.yml`; em hosts com SELinux ativo, talvez seja necessário adicionar a flag `:z` no volume.

**O profiler falha ao iniciar com erro de módulo nativo.**
Faça o rebuild sem cache: `docker compose build --no-cache app`. O Dockerfile já instala o toolchain necessário (python3, make, g++) no stage de build.
