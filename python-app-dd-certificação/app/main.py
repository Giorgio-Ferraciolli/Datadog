
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.logging_config import setup_logging
from app.routes import simulation
from datadog import initialize, statsd


# Configura o logging no início da aplicação
setup_logging()
logger = logging.getLogger(__name__)

initialize(statsd_host="datadog", statsd_port=8125)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Aplicação iniciada")
    yield
    logger.info("Aplicação encerrada")


app = FastAPI(lifespan=lifespan)

# Monta o diretório 'static' para servir arquivos estáticos (se houver)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura o diretório de templates para Jinja2
templates = Jinja2Templates(directory="app/templates")

# Inclui as rotas de simulação
app.include_router(simulation.router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    statsd.increment(
        "app.request.count",
        tags=[f"endpoint:{request.url.path}", f"status:{response.status_code}"]
    )

    statsd.histogram(
        "app.request.duration",
        process_time,
        tags=[f"endpoint:{request.url.path}"]
    )

    if response.status_code >= 400:
        statsd.increment(
            "app.request.errors",
            tags=[f"endpoint:{request.url.path}", f"status:{response.status_code}"]
        )

    # Log estruturado para cada requisição
    logger.info(
        "Request processed",
        extra={
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "process_time_seconds": f"{process_time:.4f}",
        },
    )
    return response


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

