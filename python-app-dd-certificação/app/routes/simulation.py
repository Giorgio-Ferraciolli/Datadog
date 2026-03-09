
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/success", response_class=JSONResponse)
async def success_endpoint():
    logger.info("Endpoint /success chamado")
    return {"message": "Operação bem-sucedida!", "status_code": 200}


@router.get("/not-found", response_class=JSONResponse)
async def not_found_endpoint():
    logger.warning("Endpoint /not-found chamado")
    raise HTTPException(status_code=404, detail="Recurso não encontrado")


@router.get("/server-error", response_class=JSONResponse)
async def server_error_endpoint():
    logger.error("Endpoint /server-error chamado, simulando erro interno")
    try:
        # Simula um erro interno, por exemplo, divisão por zero
        1 / 0
    except ZeroDivisionError as e:
        logger.exception("Erro de divisão por zero simulado")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")

