import logging

from fastapi import APIRouter, Depends, HTTPException

from agentes.agente import AgenteAdmin, PseudoAgente
from models.agente import CrearMisionBody
from repository.db import (
    actualizar_energia_agente,
    buscar_misiones_agente,
    completar_mision,
    crear_mision,
    despertar_agente,
    obtener_mision,
    sumar_experiencia_agente,
)
from src.auth import verificar_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Misiones"])


# -----------------------------------------------------------#
# R2 — Reconstrucción de clase de dominio.
# Si el rol es "admin" devuelve AgenteAdmin (consume mitad de energía);
# cualquier otro rol devuelve PseudoAgente.  Así el polimorfismo de
# consumir_energia() decide el costo real sin lógica en el endpoint.
# -----------------------------------------------------------#
def reconstruir_agente(nombre: str) -> PseudoAgente | None:
    """Lee la DB y devuelve la instancia de dominio correcta según el rol."""
    datos = despertar_agente(nombre)
    if datos is None:
        return None
    if datos["rol"] == "admin":
        return AgenteAdmin(nombre=datos["nombre"], energia=datos["energia"])
    return PseudoAgente(nombre=datos["nombre"], energia=datos["energia"])

# -----------------------------------------------------------#
# Se agrega verificación deApi Key para evitar creación extendida de misiones
# puede ser util para evitar que usuarios externos creen misiones sin autorización y
# puedan sobrecargar el sistema o crear misiones con requisitos no autorizados
# -----------------------------------------------------------#
@router.post("/misiones", status_code=201)
def api_crear_mision(body: CrearMisionBody, _key: str = Depends(verificar_api_key)):
    """Crea una misión asignada a un agente específico."""
    mision_id = crear_mision(
        body.titulo,
        body.descripcion,
        body.agente_asignado,
        body.energia_requerida,
        body.prioridad,
        body.recompensa,
    )
    if mision_id is None:
        raise HTTPException(404, f"Agente '{body.agente_asignado}' no encontrado")
    logger.info("Misión creada | id=%d agente=%s", mision_id, body.agente_asignado)
    return {"id": mision_id, "mensaje": "Misión creada"}

# -----------------------------------------------------------#
# Se agrega verificación deApi Key para evitar que usuarios externos
# tengan acceso a las misiones asignadas a los agentes sin autorización
# -----------------------------------------------------------#
@router.get("/misiones/{nombre_agente}")
def api_misiones_agente(nombre_agente: str, _key: str = Depends(verificar_api_key)):
    """Devuelve las misiones asignadas a un agente específico."""
    return buscar_misiones_agente(nombre_agente)

# -----------------------------------------------------------#
# Se agrega verificación deApi Key donde no queremos revelar información confidencial
# -----------------------------------------------------------#
@router.get("/misiones/detalle/{mision_id}")
def api_obtener_mision(mision_id: int, _key: str = Depends(verificar_api_key)):
    """Devuelve los detalles de una misión específica."""
    mision = obtener_mision(mision_id)
    if mision is None:
        raise HTTPException(404, f"Misión #{mision_id} no encontrada")
    return mision

# -----------------------------------------------------------#
# Se agrega verificación deApi Key para que el cambio solo lo realice el administrador de tareas terminadas
# -----------------------------------------------------------#
@router.post("/misiones/{mision_id}/completar")
def api_completar_mision(mision_id: int, _key: str = Depends(verificar_api_key)):
    """Completa una misión usando la clase de dominio para descontar energía.

    1. Lee la misión de la DB.
    2. Reconstruye la instancia de dominio (PseudoAgente o AgenteAdmin).
    3. Llama a agente.consumir_energia() — el polimorfismo decide el costo.
    4. Persiste la nueva energía y marca la misión como completada.
    """
    mision = obtener_mision(mision_id)
    if mision is None:
        raise HTTPException(404, f"Misión #{mision_id} no encontrada")
    if mision["estado"] == "completada":
        raise HTTPException(400, f"Misión #{mision_id} ya está completada")

    # Reconstruir instancia de dominio (R2)
    agente = reconstruir_agente(mision["agente_asignado"])
    if agente is None:
        raise HTTPException(404, f"Agente '{mision['agente_asignado']}' no encontrado")

    # La clase decide cuánto descuenta (AgenteAdmin paga la mitad)
    msg_energia = agente.consumir_energia(mision["energia_requerida"])

    if "insuficiente" in msg_energia.lower():
        raise HTTPException(400, msg_energia)

    # Persistir: nueva energía + estado de la misión
    actualizar_energia_agente(agente.nombre, agente.tokens)
    completar_mision(mision_id)

    # Sumar experiencia al agente según la recompensa de la misión
    recompensa = mision.get("recompensa", 10)
    sumar_experiencia_agente(agente.nombre, recompensa)

    logger.info(
        "Misión completada | id=%d tipo=%s energia_restante=%d recompensa=%d",
        mision_id, type(agente).__name__, agente.tokens, recompensa,
    )
    return {
        "mensaje": f"Misión #{mision_id} completada",
        "detalle": msg_energia,
        "energia_restante": agente.tokens,
        "tipo_agente": type(agente).__name__,
        "recompensa": recompensa,
    }
