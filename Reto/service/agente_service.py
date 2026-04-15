import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from repository.db import (
    listar_agentes,
    registrar_agente,
    despertar_agente,
    enviar_mensaje,
    leer_mensajes,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Agentes"])


class CrearAgenteBody(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    rol: str = Field(..., min_length=1)
    energia: int = Field(default=100, ge=1, le=200)


class EnviarMensajeBody(BaseModel):
    remitente: str = Field(..., min_length=1)
    destinatario: str = Field(..., min_length=1)
    contenido: str = Field(..., min_length=1, max_length=500)


@router.get("/agentes")
def api_listar_agentes():
    return listar_agentes()


@router.get("/agentes/{nombre}")
def api_obtener_agente(nombre: str):
    agente = despertar_agente(nombre)
    if agente is None:
        raise HTTPException(404, f"Agente '{nombre}' no encontrado")
    return agente


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
