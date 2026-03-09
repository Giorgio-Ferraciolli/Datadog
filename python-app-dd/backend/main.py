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

# ── ddtrace auto-instrumentation ──────────────────────────────────────────────
patch_all()

# ── Configurações de ambiente ────────────────────────────────────────────────
DD_ENV = os.getenv("DD_ENV", "local")
DD_SERVICE = os.getenv("DD_SERVICE", "fastapi-datadog")
DD_VERSION = os.getenv("DD_VERSION", "1.0.0")

# ── Datadog StatsD ────────────────────────────────────────────────────────────
initialize(
    statsd_host=os.getenv("DD_AGENT_HOST", "datadog-agent"),
    statsd_port=int(os.getenv("DD_DOGSTATSD_PORT", 8125)),
)

# ── Logging estruturado ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", '
           '"message": "%(message)s", "dd.trace_id": "%(dd.trace_id)s", '
           '"dd.span_id": "%(dd.span_id)s"}',
)
logger = logging.getLogger("fastapi.app")

# ── Controle de workers ───────────────────────────────────────────────────────
_workers_started = False


# ── Lógica reutilizável do /test ──────────────────────────────────────────────
def run_test_operation(source="http"):
    with tracer.trace(
        "app.test.operation",
        service=DD_SERVICE,
        resource=f"{source} /test"
    ) as span:

        latency = random.uniform(0.01, 0.15)
        time.sleep(latency)

        latency_ms = round(latency * 1000, 2)
        random_value = random.randint(1, 100)

        span.set_tag("custom.latency_ms", latency_ms)
        span.set_tag("custom.environment", DD_ENV)
        span.set_tag("custom.execution_source", source)
        span.set_tag("custom.random_value", random_value)

        tags = [
            f"env:{DD_ENV}",
            f"service:{DD_SERVICE}",
            f"version:{DD_VERSION}",
            f"source:{source}",
        ]

        statsd.increment("app.test.requests_total", tags=tags)
        statsd.histogram("app.test.simulated_latency_ms", latency_ms, tags=tags)
        statsd.gauge("app.test.random_value", random_value, tags=tags)

        logger.info(
            f"/test executado | source={source} latency_ms={latency_ms} trace_id={span.trace_id}"
        )

        return span.trace_id, span.span_id, latency_ms


# ── Worker de métricas periódicas ─────────────────────────────────────────────
def metrics_worker():

    logger.info("Metrics worker iniciado")
    start_time = time.time()

    while True:
        try:
            uptime_seconds = int(time.time() - start_time)

            tags = [
                f"env:{DD_ENV}",
                f"service:{DD_SERVICE}",
                f"version:{DD_VERSION}",
            ]

            statsd.gauge(
                "app.worker.random_value",
                random.uniform(0, 100),
                tags=tags,
            )

            statsd.increment(
                "app.worker.heartbeat",
                tags=tags,
            )

            statsd.histogram(
                "app.worker.fake_duration_ms",
                random.uniform(10, 500),
                tags=tags,
            )

            statsd.gauge(
                "app.worker.uptime_seconds",
                uptime_seconds,
                tags=tags,
            )

            logger.info(f"Metrics worker enviado | uptime={uptime_seconds}s")

        except Exception as e:
            logger.error(f"Erro no metrics worker: {e}")

        time.sleep(15)



def test_worker():

    logger.info("Test worker iniciado")

    while True:
        try:
            run_test_operation(source="worker")

        except Exception as e:
            logger.error(f"Erro no test worker: {e}")

        time.sleep(15)


# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FastAPI + Datadog Demo",
    description="Aplicação com APM, métricas e logs automáticos",
    version=DD_VERSION,
)


@app.on_event("startup")
def start_workers():

    global _workers_started

    if not _workers_started:

        threading.Thread(
            target=metrics_worker,
            daemon=True
        ).start()

        threading.Thread(
            target=test_worker,
            daemon=True
        ).start()

        _workers_started = True

        logger.info("Workers iniciados com sucesso")


# ── Middleware ────────────────────────────────────────────────────────────────
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
        ],
    )

    return response


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():

    logger.info("Health check solicitado")

    return {
        "status": "ok",
        "service": DD_SERVICE,
        "env": DD_ENV,
        "version": DD_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/test")
async def test():

    trace_id, span_id, latency_ms = run_test_operation(source="http")

    return {
        "status": "ok",
        "message": "Executado com sucesso",
        "trace_id": str(trace_id),
        "span_id": str(span_id),
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )