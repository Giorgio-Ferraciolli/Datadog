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

# ── Datadog StatsD (métricas customizadas) ────────────────────────────────────
initialize(
    statsd_host=os.getenv("DD_AGENT_HOST", "datadog-agent"),
    statsd_port=int(os.getenv("DD_DOGSTATSD_PORT", 8125)),
)

# ── Logging estruturado (JSON) ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "dd.trace_id": "%(dd.trace_id)s", "dd.span_id": "%(dd.span_id)s"}',
)
logger = logging.getLogger("fastapi.app")

# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FastAPI + Datadog Demo",
    description="Aplicação de demonstração com traces, logs e métricas no Datadog.",
    version=os.getenv("DD_VERSION", "1.0.0"),
)


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

    # métrica de latência por endpoint
    statsd.histogram(
        "app.request.duration_ms",
        duration_ms,
        tags=[
            f"endpoint:{request.url.path}",
            f"method:{request.method}",
            f"status:{response.status_code}",
            f"env:{os.getenv('DD_ENV', 'local')}",
            f"service:{os.getenv('DD_SERVICE', 'fastapi-datadog')}",
        ],
    )
    return response


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Observability"])
async def health():
    """Verifica se a aplicação está no ar."""
    logger.info("Health check solicitado")
    return {
        "status": "ok",
        "service": os.getenv("DD_SERVICE", "fastapi-datadog"),
        "env": os.getenv("DD_ENV", "local"),
        "version": os.getenv("DD_VERSION", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/test", tags=["Observability"])
async def test():
    """
    Gera um trace ativo, log estruturado e métricas customizadas no Datadog.
    """
    with tracer.trace("app.test.operation", service=os.getenv("DD_SERVICE", "fastapi-datadog"), resource="GET /test") as span:

        # ── simula latência aleatória ──────────────────────────────────────
        latency = random.uniform(0.01, 0.15)
        time.sleep(latency)

        # ── enriquece o span com metadados ────────────────────────────────
        span.set_tag("custom.latency_ms", round(latency * 1000, 2))
        span.set_tag("custom.environment", os.getenv("DD_ENV", "local"))
        span.set_tag("custom.random_value", random.randint(1, 100))

        # ── log estruturado (trace_id / span_id injetados pelo ddtrace) ───
        logger.info(
            "Endpoint /test processado | "
            f"latency_ms={round(latency * 1000, 2)} "
            f"trace_id={span.trace_id} span_id={span.span_id}"
        )

        # ── métricas customizadas via StatsD ──────────────────────────────
        tags = [
            f"env:{os.getenv('DD_ENV', 'local')}",
            f"service:{os.getenv('DD_SERVICE', 'fastapi-datadog')}",
            f"version:{os.getenv('DD_VERSION', '1.0.0')}",
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
