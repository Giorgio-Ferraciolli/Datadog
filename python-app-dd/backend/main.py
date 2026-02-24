import threading
import logging
import os
import time
import random
from datetime import datetime

from ddtrace import tracer, patch_all
from datadog import initialize, statsd

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ── ddtrace auto-instrumentation ──────────────────────────────────────────────
patch_all()

# ── Configurações de ambiente ────────────────────────────────────────────────
DD_ENV = os.getenv("DD_ENV", "local")
DD_SERVICE = os.getenv("DD_SERVICE", "fastapi-datadog")
DD_VERSION = os.getenv("DD_VERSION", "1.0.0")

# ── Datadog StatsD (métricas customizadas) ────────────────────────────────────
initialize(
    statsd_host=os.getenv("DD_AGENT_HOST", "datadog-agent"),
    statsd_port=int(os.getenv("DD_DOGSTATSD_PORT", 8125)),
)

# ── Logging estruturado (JSON) ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", '
           '"message": "%(message)s", "dd.trace_id": "%(dd.trace_id)s", '
           '"dd.span_id": "%(dd.span_id)s"}',
)
logger = logging.getLogger("fastapi.app")

# ── Worker de métricas periódicas ─────────────────────────────────────────────
_worker_started = False


def metrics_worker():
    """
    Envia métricas para o Datadog a cada 15 segundos.
    Funciona como heartbeat contínuo da aplicação.
    """
    logger.info("Metrics worker iniciado")

    start_time = time.time()

    while True:
        try:
            uptime_seconds = int(time.time() - start_time)

            base_tags = [
                f"env:{DD_ENV}",
                f"service:{DD_SERVICE}",
                f"version:{DD_VERSION}",
            ]

            # Gauge: valor atual aleatório
            statsd.gauge(
                "app.worker.random_value",
                random.uniform(0, 100),
                tags=base_tags,
            )

            # Counter: heartbeat contínuo
            statsd.increment(
                "app.worker.heartbeat",
                tags=base_tags,
            )

            # Histogram: duração simulada
            statsd.histogram(
                "app.worker.fake_duration_ms",
                random.uniform(10, 500),
                tags=base_tags,
            )

            # Gauge: uptime do worker
            statsd.gauge(
                "app.worker.uptime_seconds",
                uptime_seconds,
                tags=base_tags,
            )

            logger.info(f"Metrics enviadas com sucesso | uptime={uptime_seconds}s")

        except Exception as e:
            logger.error(f"Erro enviando métricas periódicas: {e}")

        time.sleep(15)


# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FastAPI + Datadog Demo",
    description="Aplicação de demonstração com traces, logs e métricas no Datadog.",
    version=DD_VERSION,
)


@app.on_event("startup")
def start_metrics_worker():
    global _worker_started
    if not _worker_started:
        thread = threading.Thread(target=metrics_worker, daemon=True)
        thread.start()
        _worker_started = True


# ── Middleware: loga todas as requisições ─────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    logger.info(
        f"method={request.method} path={request.url.path} "
        f"status={response.status_code} duration_ms={duration_ms}"
    )

    statsd.histogram(
        "app.request.duration_ms",
        duration_ms,
        tags=[
            f"endpoint:{request.url.path}",
            f"method:{request.method}",
            f"status:{response.status_code}",
            f"env:{DD_ENV}",
            f"service:{DD_SERVICE}",
            f"version:{DD_VERSION}",
        ],
    )
    return response


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Observability"])
async def health():
    logger.info("Health check solicitado")
    return {
        "status": "ok",
        "service": DD_SERVICE,
        "env": DD_ENV,
        "version": DD_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/test", tags=["Observability"])
async def test():
    with tracer.trace(
        "app.test.operation",
        service=DD_SERVICE,
        resource="GET /test"
    ) as span:

        latency = random.uniform(0.01, 0.15)
        time.sleep(latency)

        span.set_tag("custom.latency_ms", round(latency * 1000, 2))
        span.set_tag("custom.environment", DD_ENV)
        span.set_tag("custom.random_value", random.randint(1, 100))

        logger.info(
            "Endpoint /test processado | "
            f"latency_ms={round(latency * 1000, 2)} "
            f"trace_id={span.trace_id} span_id={span.span_id}"
        )

        tags = [
            f"env:{DD_ENV}",
            f"service:{DD_SERVICE}",
            f"version:{DD_VERSION}",
        ]

        statsd.increment("app.test.requests_total", tags=tags)
        statsd.histogram("app.test.simulated_latency_ms", round(latency * 1000, 2), tags=tags)
        statsd.gauge("app.test.random_value", random.randint(1, 100), tags=tags)

        return {
            "status": "ok",
            "message": "Trace, log e métricas enviados ao Datadog com sucesso!",
            "trace_id": str(span.trace_id),
            "span_id": str(span.span_id),
            "simulated_latency_ms": round(latency * 1000, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)