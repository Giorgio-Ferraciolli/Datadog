# Datadog Node.js App

Node.js application fully instrumented with **Datadog APM**, **continuous profiling**, **runtime metrics**, **custom DogStatsD metrics** and **structured JSON logs with trace correlation**.

The project is 100% containerized — **the only prerequisite is Docker**. You do not need Node.js, npm, or any other tool installed locally.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (Engine 20.10+)
- [Docker Compose v2](https://docs.docker.com/compose/install/) (ships with Docker Desktop; on Linux install `docker-compose-plugin`)
- A Datadog account and an API key — get one at <https://app.datadoghq.com/organization-settings/api-keys>

---

## Quick start

```bash
# 1. Copy the env template
cp .env.example .env

# 2. Edit .env and set DD_API_KEY to your real key.
#    Optionally adjust DD_SITE (e.g. datadoghq.eu for EU1).
$EDITOR .env

# 3. Build and run
docker compose up --build
```

That's it. The app is now listening on <http://localhost:3000> and shipping data to Datadog.

To run detached:

```bash
docker compose up --build -d
docker compose logs -f app
```

To stop and clean up:

```bash
docker compose down
```

---

## Exercising the endpoints

```bash
# Health
curl http://localhost:3000/health

# Users — emits a custom span, an artificial DB latency and a queue gauge
curl 'http://localhost:3000/users?user_id=u-42'

# Create an order — emits business tags and a custom counter
curl -X POST http://localhost:3000/orders \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u-42","product":"widget-001","amount":129.9}'

# Force an error to exercise the error pipeline
curl -X POST 'http://localhost:3000/orders?fail=true' \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u-42","product":"widget-001"}'
```

Generate a bit of traffic so dashboards have data to show:

```bash
for i in $(seq 1 50); do
  curl -s http://localhost:3000/users > /dev/null
  curl -s -X POST http://localhost:3000/orders \
    -H 'Content-Type: application/json' \
    -d '{"user_id":"u-'$i'","product":"widget-001"}' > /dev/null
  # one in five fails on purpose
  if [ $((i % 5)) -eq 0 ]; then
    curl -s -X POST 'http://localhost:3000/orders?fail=true' \
      -H 'Content-Type: application/json' -d '{}' > /dev/null
  fi
done
```

---

## Verifying in Datadog

Allow ~1–2 minutes after the first request for data to appear.

### Traces in APM

1. Open **APM → Services** in the Datadog UI: <https://app.datadoghq.com/apm/services>
2. Filter by `env:development` (or whatever you set `DD_ENV` to).
3. You should see the service `datadog-node-app` listed.
4. Click it, then open **Traces** to inspect individual requests. Each `/users` request will show a child `db.query.users` span and each `/orders` a `payment.process` span. Failed requests appear with the **error** indicator and the `error.message` tag attached.

### Continuous profiling

1. Open **APM → Profiling → Profiles**: <https://app.datadoghq.com/profiling>
2. Filter by `service:datadog-node-app`.
3. CPU, wall-time and heap profiles are uploaded every minute.

### Custom metrics in Metrics Explorer

1. Open **Metrics → Explorer**: <https://app.datadoghq.com/metric/explorer>
2. The application emits these custom metrics (all prefixed with `app.`):

| Metric                          | Type      | Tags                                            |
|---------------------------------|-----------|-------------------------------------------------|
| `app.requests.count`            | counter   | `endpoint`, `method`, `status_code`, `service`, `env`, `version` |
| `app.requests.latency`          | histogram | same as above                                   |
| `app.queue.pending_jobs`        | gauge     | `service`, `env`, `version`                     |
| `app.orders.created`            | counter   | `product`, `user_id`, `service`, `env`, `version` |
| `app.errors.count`              | counter   | `endpoint`, `method`, `error_type`              |
| `app.process.uncaught_exception`| counter   | `error_type`                                    |
| `app.process.unhandled_rejection`| counter  | `error_type`                                    |

   Try `avg:app.requests.latency{service:datadog-node-app}` grouped by `endpoint`.

### Runtime metrics

Runtime metrics appear under `runtime.node.*` (event loop lag, GC, heap usage, etc.). Search the Metrics Explorer for `runtime.node` and filter by `service:datadog-node-app`.

### Logs

1. Open **Logs → Live Tail**: <https://app.datadoghq.com/logs/livetail>
2. Filter by `service:datadog-node-app`.
3. Each log line is JSON and carries `dd.trace_id` / `dd.span_id`, so you can click through directly to the matching trace in APM.

---

## Project layout

```
.
├── Dockerfile                  # Multi-stage build (build + runtime)
├── docker-compose.yml          # app + datadog-agent services
├── .env.example                # Template for environment variables
├── package.json
└── src/
    ├── tracer.js               # Entry point — initializes dd-trace BEFORE anything else
    ├── app.js                  # Express bootstrap, middlewares, error handlers
    ├── config/
    │   └── index.js            # Centralized env-var reading
    ├── middleware/
    │   ├── requestMetrics.js   # Per-request counter + latency histogram
    │   └── errorHandler.js     # Marks span as errored + logs + metric
    ├── routes/
    │   ├── health.js           # GET /health
    │   ├── users.js            # GET /users — custom span + queue gauge
    │   └── orders.js           # POST /orders — business tags, ?fail=true
    └── utils/
        ├── logger.js           # pino, JSON, trace-correlated
        └── metrics.js          # hot-shots (DogStatsD) wrapper
```

---

## Troubleshooting

**The agent exits immediately with `DD_API_KEY is required`.**
Set `DD_API_KEY` in `.env`. Compose refuses to start without it.

**No traces show up in the Datadog UI.**
- Check the agent is healthy: `docker compose logs datadog-agent | grep -i "agent.*started"`
- Make sure `DD_SITE` matches your account region (EU users need `datadoghq.eu`).
- Inside the app container, the agent must be reachable at `datadog-agent:8126`. This is handled automatically by the compose network.

**Metrics show up but logs don't.**
Datadog log collection from containers requires `DD_LOGS_ENABLED=true` and read access to `/var/run/docker.sock`. Both are already configured in `docker-compose.yml`; on SELinux-enabled hosts you may need to add the `:z` flag to that volume mount.

**Profiler fails to start with a native module error.**
Rebuild without cache: `docker compose build --no-cache app`. The Dockerfile installs the required toolchain (python3, make, g++) in the build stage.
