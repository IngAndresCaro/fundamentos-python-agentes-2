import logging

from fastapi import APIRouter, HTTPException

from agentes.agente import AgenteAdmin, PseudoAgente
from models.agente import CrearAgenteBody, EnviarMensajeBody
from repository.db import (
    listar_agentes,
    registrar_agente,
    despertar_agente,
    enviar_mensaje,
    leer_mensajes,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Agentes"])


# -----------------------------------------------------------#
# R2 — Al consultar un agente, se reconstruye como instancia
# de dominio para verificar con isinstance.
# -----------------------------------------------------------#
def reconstruir_agente(nombre: str) -> PseudoAgente | None:
    """Lee la DB y devuelve la instancia de dominio correcta según el rol."""
    datos = despertar_agente(nombre)
    if datos is None:
        return None
    if datos["rol"] == "admin":
        return AgenteAdmin(nombre=datos["nombre"], energia=datos["energia"])
    return PseudoAgente(nombre=datos["nombre"], energia=datos["energia"])


@router.get("/agentes")
def api_listar_agentes():
    return listar_agentes()


@router.get("/agentes/{nombre}")
def api_obtener_agente(nombre: str):
    agente = reconstruir_agente(nombre)
    if agente is None:
        raise HTTPException(404, f"Agente '{nombre}' no encontrado")
    datos = despertar_agente(nombre)
    datos["tipo_agente"] = type(agente).__name__
    datos["es_admin"] = isinstance(agente, AgenteAdmin)
    return datos


@router.post("/agentes", status_code=201)
def api_crear_agente(body: CrearAgenteBody):
    resultado = registrar_agente(body.nombre, body.rol, body.energia)
    if "Error" in resultado:
        raise HTTPException(409, resultado)
    logger.info("Agente creado | nombre=%s rol=%s", body.nombre, body.rol)
    return {"mensaje": resultado}


@router.post("/mensajes", status_code=201)
def api_enviar_mensaje(body: EnviarMensajeBody):
    resultado = enviar_mensaje(body.remitente, body.destinatario, body.contenido)
    if "Error" in resultado:
        raise HTTPException(404, resultado)
    logger.info("Mensaje enviado | %s → %s", body.remitente, body.destinatario)
    return {"mensaje": resultado}


@router.get("/mensajes/{nombre_agente}")
def api_leer_mensajes(nombre_agente: str):
    return leer_mensajes(nombre_agente)
