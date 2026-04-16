# -----------------------------------------------------------#
# 5.2 — Endpoint GET /briefing/{nombre}.
#
# Inteligencia por rol:
#   • guardián / espía  → Advice Slip (consejos de vida — tono empático)
#   • analista / admin   → Wikipedia Featured (cultura general — tono profesional)
#   • explorador / otros → JokeAPI Programming (chistes geek — tono divertido)
#   • Seguridad          → Delegada a seguridad_service.py (Agente Smit).
#
# Si la API externa falla o tarda, el briefing se entrega con fallback.
# -----------------------------------------------------------#
import logging
from datetime import date

import requests as http_client
from fastapi import APIRouter, Depends, HTTPException

from config.config import API_ADVICE_URL, API_JOKE_URL, API_WIKIPEDIA_URL, TIMEOUT_EXTERNO
from src.auth import verificar_api_key
from agentes.agente import AgenteAdmin, PseudoAgente
from repository.db import (
    actualizar_energia_agente,
    buscar_misiones_agente,
    completar_mision,
    despertar_agente,
    sumar_experiencia_agente,
)
from service.seguridad_service import (
    auto_completar_misiones_seguridad,
    es_mision_seguridad,
    obtener_inteligencia_seguridad,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Briefing"])

# ── Mapeo rol → API + tono ──
_ROLES_ADVICE = {"guardián", "espía"}
_ROLES_WIKIPEDIA = {"analista", "admin"}
# El resto usa JokeAPI


def _obtener_advice() -> tuple[str | None, str]:
    """Advice Slip — consejo de vida aleatorio."""
    url = API_ADVICE_URL
    try:
        resp = http_client.get(url, timeout=TIMEOUT_EXTERNO)
        resp.raise_for_status()
        body = resp.json()
        texto = body.get("slip", {}).get("advice", str(body))
        return f"💡 {texto}", url
    except http_client.Timeout:
        return "[Fallback] Advice Slip no respondió a tiempo.", url + " (timeout)"
    except http_client.RequestException as exc:
        logger.warning("Advice Slip error: %s", exc)
        return "[Fallback] Advice Slip no está disponible.", url + " (error)"


def _obtener_joke() -> tuple[str | None, str]:
    """JokeAPI — chiste de programación."""
    url = API_JOKE_URL
    try:
        resp = http_client.get(url, timeout=TIMEOUT_EXTERNO)
        resp.raise_for_status()
        body = resp.json()
        texto = body.get("joke", str(body))
        return f"😂 {texto}", url
    except http_client.Timeout:
        return "[Fallback] JokeAPI no respondió a tiempo.", url + " (timeout)"
    except http_client.RequestException as exc:
        logger.warning("JokeAPI error: %s", exc)
        return "[Fallback] JokeAPI no está disponible.", url + " (error)"


def _obtener_wikipedia() -> tuple[str | None, str]:
    """Wikipedia Featured — artículo destacado del día."""
    hoy = date.today()
    url = f"{API_WIKIPEDIA_URL}/{hoy.year}/{hoy.month:02d}/{hoy.day:02d}"
    try:
        resp = http_client.get(url, timeout=TIMEOUT_EXTERNO)
        resp.raise_for_status()
        body = resp.json()
        tfa = body.get("tfa", {})
        titulo = tfa.get("normalizedtitle", "")
        extracto = tfa.get("extract", "")
        if titulo and extracto:
            texto = f"📚 {titulo}: {extracto[:300]}"
        else:
            texto = f"📚 {str(body)[:300]}"
        return texto, url
    except http_client.Timeout:
        return "[Fallback] Wikipedia no respondió a tiempo.", url + " (timeout)"
    except http_client.RequestException as exc:
        logger.warning("Wikipedia API error: %s", exc)
        return "[Fallback] Wikipedia no está disponible.", url + " (error)"


def _obtener_inteligencia_por_rol(rol: str) -> tuple[str | None, str, str]:
    """Selecciona la API externa según el rol del agente.

    Retorna (texto, fuente_url, tono).
    """
    if rol in _ROLES_ADVICE:
        texto, fuente = _obtener_advice()
        return texto, fuente, "empático"
    if rol in _ROLES_WIKIPEDIA:
        texto, fuente = _obtener_wikipedia()
        return texto, fuente, "profesional"
    # Default: humor geek
    texto, fuente = _obtener_joke()
    return texto, fuente, "divertido"


def _auto_completar_misiones(datos_agente: dict, misiones: list[dict]) -> dict:
    """Auto-completa misiones de un agente admin al consultar briefing.

    Usa polimorfismo R2: AgenteAdmin paga mitad de energía.
    """
    if datos_agente["rol"] == "admin":
        agente = AgenteAdmin(nombre=datos_agente["nombre"], energia=datos_agente["energia"])
    else:
        agente = PseudoAgente(nombre=datos_agente["nombre"], energia=datos_agente["energia"])

    completadas = []
    sin_energia = []
    for m in misiones:
        if m["estado"] == "completada":
            continue
        msg = agente.consumir_energia(m["energia_requerida"])
        if "insuficiente" in msg.lower():
            sin_energia.append(m["titulo"])
            continue
        actualizar_energia_agente(agente.nombre, agente.tokens)
        completar_mision(m["id"])
        recompensa = m.get("recompensa", 10)
        sumar_experiencia_agente(agente.nombre, recompensa)
        completadas.append(m["titulo"])
        logger.info(
            "Misión auto-completada | agente=%s id=%d titulo=%s energia_restante=%d recompensa=%d",
            agente.nombre, m["id"], m["titulo"], agente.tokens, recompensa,
        )

    return {
        "misiones_auto_completadas": completadas,
        "misiones_sin_energia": sin_energia,
        "energia_final": agente.tokens,
        "tipo_agente": type(agente).__name__,
    }

# -----------------------------------------------------------#

#  Se traen en total 4 api publicas 3 en este servicio 1 en servicio de seguridad siendo la que mas tiempo le inverti
# esto porque al momento de ejecutar la aplicación debemos validar que todo el sistema no se rompa y tenga vulneravilidades
# las demas son solo de prueba para ver diferentes conexiones y que trae cada uno, en su practica
# lo chevere de esto es que entre mejor su uso esto deja de ser un bot de tareas a un asistente inteligente
# -----------------------------------------------------------#
# -----------------------------------------------------------#
# Tambien se deja verificación con API key para que en casos de hakeo no nos traten sobre cargar
# el sistema con petesiones masivas o no sean validas
# -----------------------------------------------------------#
@router.get("/briefing/{nombre}")
def api_briefing(nombre: str, _key: str = Depends(verificar_api_key)):
    """Combina datos locales del agente con inteligencia externa por rol.

    Cada rol recibe un tipo de inteligencia distinta:
      • guardián/espía  → Advice Slip (consejos)
      • analista/admin   → Wikipedia (cultura general)
      • explorador/otros → JokeAPI (humor geek)

    Si el agente tiene misiones de seguridad, delega a seguridad_service.
    """
    datos = despertar_agente(nombre)
    if datos is None:
        raise HTTPException(404, f"Agente '{nombre}' no encontrado")

    misiones = buscar_misiones_agente(nombre)
    pendientes = [m for m in misiones if m["estado"] == "pendiente"]
    en_curso = [m for m in misiones if m["estado"] == "en_curso"]
    completadas = [m for m in misiones if m["estado"] == "completada"]

    # Inteligencia externa según rol
    inteligencia_externa, fuente_externa, tono = _obtener_inteligencia_por_rol(datos["rol"])

    respuesta = {
        "agente": {
            "nombre": datos["nombre"],
            "rol": datos["rol"],
            "energia": datos["energia"],
        },
        "resumen_misiones": {
            "total": len(misiones),
            "pendientes": len(pendientes),
            "en_curso": len(en_curso),
            "completadas": len(completadas),
        },
        "inteligencia_externa": inteligencia_externa,
        "fuente_externa": fuente_externa,
        "tono": tono,
    }

    # Detectar contexto de seguridad en misiones activas (pendientes + en_curso)
    misiones_activas = pendientes + en_curso
    misiones_seguridad = [m for m in misiones_activas if es_mision_seguridad(m)]

    if misiones_seguridad:
        logger.info(
            "Briefing seguridad activado | agente=%s misiones_seguridad=%d",
            nombre, len(misiones_seguridad),
        )
        respuesta["inteligencia_seguridad"] = obtener_inteligencia_seguridad()
        respuesta["inteligencia_seguridad"]["misiones_analizadas"] = [
            m["titulo"] for m in misiones_seguridad
        ]

        # Auto-completar misiones de seguridad tras el escaneo
        resultado = auto_completar_misiones_seguridad(datos, misiones_seguridad)
        respuesta["inteligencia_seguridad"]["misiones_auto_completadas"] = resultado["misiones_auto_completadas"]
        if resultado["misiones_sin_energia"]:
            respuesta["inteligencia_seguridad"]["misiones_sin_energia"] = resultado["misiones_sin_energia"]
        respuesta["agente"]["energia"] = resultado["energia_final"]
        respuesta["agente"]["tipo_agente"] = resultado["tipo_agente"]

    # Auto-completar misiones regulares (no de seguridad) para agentes admin
    misiones_regulares = [m for m in misiones_activas if not es_mision_seguridad(m)]
    if datos["rol"] == "admin" and misiones_regulares:
        energia_actual = respuesta["agente"].get("energia", datos["energia"])
        datos_para_auto = {**datos, "energia": energia_actual}
        resultado_admin = _auto_completar_misiones(datos_para_auto, misiones_regulares)
        respuesta["auto_completadas"] = {
            "misiones_completadas": resultado_admin["misiones_auto_completadas"],
            "tipo_agente": resultado_admin["tipo_agente"],
        }
        if resultado_admin["misiones_sin_energia"]:
            respuesta["auto_completadas"]["misiones_sin_energia"] = resultado_admin["misiones_sin_energia"]
        respuesta["agente"]["energia"] = resultado_admin["energia_final"]
        respuesta["agente"]["tipo_agente"] = resultado_admin["tipo_agente"]
        logger.info(
            "Admin auto-completó %d misiones | agente=%s energia_final=%d",
            len(resultado_admin["misiones_auto_completadas"]), nombre, resultado_admin["energia_final"],
        )

    logger.info("Briefing generado | agente=%s rol=%s tono=%s seguridad=%s", nombre, datos["rol"], tono, bool(misiones_seguridad))

    return respuesta
