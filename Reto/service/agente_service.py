import logging

from fastapi import APIRouter, Depends, HTTPException

from agentes.agente import AgenteAdmin, PseudoAgente
from models.agente import ActualizarAgenteBody, CrearAgenteBody, EnviarMensajeBody
from repository.db import (
    listar_agentes,
    registrar_agente,
    despertar_agente,
    actualizar_agente,
    enviar_mensaje,
    leer_mensajes,
    eliminar_agente,
    misiones_activas_agente,
)
from src.auth import verificar_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Agentes"])


# -----------------------------------------------------------#
# Al consultar un agente, se reconstruye como instancia
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
def api_listar_agentes(_key: str = Depends(verificar_api_key)):
    return listar_agentes()

# -----------------------------------------------------------#
# Se agrega verificación deApi Key entendiendo que la información de los agentes es 
# sensible y no queremos que usuarios externos tengan acceso a ella sin autorización
# -----------------------------------------------------------#
@router.get("/agentes/{nombre}")
def api_obtener_agente(nombre: str, _key: str = Depends(verificar_api_key)):
    """Devuelve los datos de un agente, incluyendo su tipo y si es admin."""
    agente = reconstruir_agente(nombre)
    if agente is None:
        raise HTTPException(404, f"Agente '{nombre}' no encontrado")
    datos = despertar_agente(nombre)
    datos["tipo_agente"] = type(agente).__name__
    datos["es_admin"] = isinstance(agente, AgenteAdmin)
    return datos

# -----------------------------------------------------------#
# Se agrega verificación deApi Key para evitar creación extendida de agentes
# puede ser util para evitar que usuarios externos creen agentes sin autorización y 
# puedan sobrecargar el sistema o crear agentes con roles no autorizados
# -----------------------------------------------------------#
@router.post("/agentes", status_code=201)
def api_crear_agente(body: CrearAgenteBody, _key: str = Depends(verificar_api_key)):
    """Crea un nuevo agente con el nombre, rol y energía especificados."""
    resultado = registrar_agente(body.nombre, body.rol, body.energia)
    if "Error" in resultado:
        raise HTTPException(409, resultado)
    logger.info("Agente creado | nombre=%s rol=%s", body.nombre, body.rol)
    return {"mensaje": resultado}

# -----------------------------------------------------------#
# Se ingresa verificación de Api key para controlar modificaciones de mensajes
# -----------------------------------------------------------#
@router.post("/mensajes", status_code=201)
def api_enviar_mensaje(body: EnviarMensajeBody, _key: str = Depends(verificar_api_key)):
    """Envía un mensaje de un agente a otro."""
    resultado = enviar_mensaje(body.remitente, body.destinatario, body.contenido)
    if "Error" in resultado:
        raise HTTPException(404, resultado)
    logger.info("Mensaje enviado | %s → %s", body.remitente, body.destinatario)
    return {"mensaje": resultado}

# -----------------------------------------------------------#
# Se agrega verificación deApi Key para evitar que usuarios externos tengan información de los
# agentes y puede utilizar información para atacar el sistema
# -----------------------------------------------------------#
@router.get("/mensajes/{nombre_agente}")
def api_leer_mensajes(nombre_agente: str, _key: str = Depends(verificar_api_key)):
    """Devuelve los mensajes recibidos por un agente."""
    return leer_mensajes(nombre_agente)

# -----------------------------------------------------------#
# Se agrega verificación deApi Key para evitar que usuarios externos tengan información de los
# agentes y puede utilizar información para atacar el sistema
# -----------------------------------------------------------#
@router.get("/agentes/{nombre}/estado-eliminacion")
def api_estado_eliminacion(nombre: str, _key: str = Depends(verificar_api_key)):
    """Devuelve si el agente puede eliminarse (sin misiones activas)."""
    activas = misiones_activas_agente(nombre)
    return {"nombre": nombre, "puede_eliminar": len(activas) == 0, "misiones_activas": activas}

# -----------------------------------------------------------#
#Se agrega validación de API key para controlar modificaciones de agentes
# -----------------------------------------------------------#
@router.put("/agentes/{nombre}")
def api_actualizar_agente(nombre: str, body: ActualizarAgenteBody, _key: str = Depends(verificar_api_key)):
    """Actualiza el rol y/o energía de un agente."""
    resultado = actualizar_agente(nombre, body.rol, body.energia)
    if "Error" in resultado:
        code = 404 if "no encontrado" in resultado else 400
        raise HTTPException(code, resultado)
    logger.info("Agente actualizado | nombre=%s rol=%s energia=%s", nombre, body.rol, body.energia)
    return {"mensaje": resultado}

# -----------------------------------------------------------#
#Se agrego validación de api key para que otro usuario no pueda eliminar un agente sin autorización"
# -----------------------------------------------------------#
@router.delete("/agentes/{nombre}")
def api_eliminar_agente(nombre: str, _key: str = Depends(verificar_api_key)):
    """Elimina un agente si no tiene misiones activas. esto por el usuario"""
    resultado = eliminar_agente(nombre)
    if "Error" in resultado:
        code = 404 if "no encontrado" in resultado else 409
        raise HTTPException(code, resultado)
    logger.info("Agente eliminado | nombre=%s", nombre)
    return {"mensaje": resultado}
