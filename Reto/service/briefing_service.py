# -----------------------------------------------------------#
# 5.2 — Endpoint GET /briefing/{nombre}.
# Elegí la API de Useless Facts (https://uselessfacts.jsph.pl) porque encaja
# con la narrativa: un agente recibe "inteligencia" aleatoria del mundo exterior
# como parte de su briefing — datos curiosos que podrían ser pistas encubiertas.
# Si la API falla o tarda más de 3 segundos, el briefing se entrega igual con
# un mensaje de fallback indicando que la fuente externa no está disponible.
# -----------------------------------------------------------#
import logging

import requests as http_client
from fastapi import APIRouter, Depends, HTTPException

from config.config import EXTERNAL_API_URL, TIMEOUT_EXTERNO
from src.auth import verificar_api_key
from repository.db import buscar_misiones_agente, despertar_agente

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Briefing"])


@router.get("/briefing/{nombre}")
def api_briefing(nombre: str, _key: str = Depends(verificar_api_key)):
    """Combina datos locales del agente con inteligencia de una API pública externa."""
    datos = despertar_agente(nombre)
    if datos is None:
        raise HTTPException(404, f"Agente '{nombre}' no encontrado")

    misiones = buscar_misiones_agente(nombre)
    pendientes = [m for m in misiones if m["estado"] == "pendiente"]
    completadas = [m for m in misiones if m["estado"] == "completada"]

    # Inteligencia externa con manejo de fallos
    inteligencia_externa = None
    fuente_externa = EXTERNAL_API_URL
    try:
        resp = http_client.get(EXTERNAL_API_URL, timeout=TIMEOUT_EXTERNO)
        resp.raise_for_status()
        body = resp.json()
        # Useless Facts devuelve {"id": "...", "text": "...", "source": "..."}
        inteligencia_externa = body.get("text", str(body))
    except http_client.Timeout:
        logger.warning("Briefing %s — API externa timeout (%s)", nombre, EXTERNAL_API_URL)
        inteligencia_externa = "[Fallback] La fuente de inteligencia no respondió a tiempo."
        fuente_externa += " (timeout)"
    except http_client.RequestException as exc:
        logger.warning("Briefing %s — API externa error: %s", nombre, exc)
        inteligencia_externa = "[Fallback] La fuente de inteligencia no está disponible."
        fuente_externa += " (error)"

    logger.info("Briefing generado | agente=%s", nombre)

    return {
        "agente": {
            "nombre": datos["nombre"],
            "rol": datos["rol"],
            "energia": datos["energia"],
        },
        "resumen_misiones": {
            "total": len(misiones),
            "pendientes": len(pendientes),
            "completadas": len(completadas),
        },
        "inteligencia_externa": inteligencia_externa,
        "fuente_externa": fuente_externa,
    }
