from ddtrace import patch_all
from app import app

# Aplica o patch em todas as bibliotecas suportadas pelo ddtrace
# Isso habilita o tracing automático para Flask, requests, etc.
patch_all()

# O Gunicorn usará este arquivo para iniciar a aplicação
if __name__ == "__main__":
    app.run()
