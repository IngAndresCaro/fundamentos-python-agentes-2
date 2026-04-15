import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from repository.db import (
    buscar_misiones_agente,
    completar_mision,
    crear_mision,
    obtener_mision,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Misiones"])


class CrearMisionBody(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=100)
    descripcion: str = Field(default="")
    agente_asignado: str = Field(..., min_length=1)
    energia_requerida: int = Field(default=20, ge=1)
    prioridad: str = Field(default="media")


@router.post("/misiones", status_code=201)
def api_crear_mision(body: CrearMisionBody):
    mision_id = crear_mision(
        body.titulo,
        body.descripcion,
        body.agente_asignado,
        body.energia_requerida,
        body.prioridad,
    )
    if mision_id is None:
        raise HTTPException(404, f"Agente '{body.agente_asignado}' no encontrado")
    logger.info("Misión creada | id=%d agente=%s", mision_id, body.agente_asignado)
    return {"id": mision_id, "mensaje": "Misión creada"}


@router.get("/misiones/{nombre_agente}")
def api_misiones_agente(nombre_agente: str):
    return buscar_misiones_agente(nombre_agente)


@router.get("/misiones/detalle/{mision_id}")
def api_obtener_mision(mision_id: int):
    mision = obtener_mision(mision_id)
    if mision is None:
        raise HTTPException(404, f"Misión #{mision_id} no encontrada")
    return mision


@router.put("/misiones/{mision_id}/completar")
def api_completar_mision(mision_id: int):
    ok = completar_mision(mision_id)
    if not ok:
        raise HTTPException(404, "Misión no encontrada o ya completada")
    logger.info("Misión completada | id=%d", mision_id)
    return {"mensaje": f"Misión #{mision_id} completada"}
