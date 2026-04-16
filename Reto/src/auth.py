# -----------------------------------------------------------#
# 5.1 — Dependencia de autenticación por API key.
# Protejo los endpoints de ESCRITURA (POST crear agente, POST crear misión,
# POST completar misión, POST enviar mensaje) porque modifican datos.
# Los GET de consulta quedan libres para que cualquier sesión autenticada
# pueda ver la oficina y datos sin necesitar la API key por header.
# La API key se compara contra el valor cargado desde .env en config.py.
# -----------------------------------------------------------#
import logging

from fastapi import Header, HTTPException

from config.config import AGENCIA_API_KEY

logger = logging.getLogger(__name__)


def verificar_api_key(x_api_key: str = Header(default="")) -> str:
    """Dependencia FastAPI que valida el header X-API-KEY.

    Si la key no coincide con la configurada en .env, retorna 401.
    Se inyecta con Depends(verificar_api_key) en los endpoints de escritura.
    """
    if not x_api_key or x_api_key != AGENCIA_API_KEY:
        logger.warning("Intento de acceso con API key inválida")
        raise HTTPException(status_code=401, detail="API key inválida")
    return x_api_key
