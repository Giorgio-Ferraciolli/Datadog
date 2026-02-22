FROM python:3.11-slim

LABEL maintainer="dev@example.com"
LABEL description="FastAPI + Datadog monitoring demo"

WORKDIR /app

# instala dependências do sistema necessárias para extensões nativas (wrapt, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl \
    && rm -rf /var/lib/apt/lists/*

# instala dependências Python — camada separada para cache eficiente
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copia código-fonte
COPY . .

# expõe porta da aplicação
EXPOSE 8000

# inicia com ddtrace-run para instrumentação automática de APM
CMD ["ddtrace-run", "uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--log-level", "info"]