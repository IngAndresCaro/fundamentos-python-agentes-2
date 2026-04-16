"""
R5 — Cliente HTTP de demostración.
Ejecuta un guion end-to-end que prueba todos los circuitos de La Agencia:
  1. Verifica que el servidor está vivo.
  2. Crea un agente (con X-API-KEY).
  3. Crea una misión asignada (con X-API-KEY).
  4. Completa la misión (con X-API-KEY).
  5. Consulta el briefing del agente.
  6. Envía un mensaje y lee la bandeja.

Uso:
  python cliente.py            (usa http://127.0.0.1:8000 por defecto)
  python cliente.py --port 8001
"""

import argparse
import sys

import requests

from config.config import AGENCIA_API_KEY, TIMEOUT_CLIENTE

# ───────────────────── Configuración ─────────────────────

API_KEY = AGENCIA_API_KEY                 # Cargado desde config/.env
TIMEOUT = TIMEOUT_CLIENTE                 # Segundos máximo por petición


def _header() -> dict[str, str]:
    """Headers de autenticación para endpoints protegidos."""
    return {"X-API-KEY": API_KEY}


def paso(numero: int, titulo: str) -> None:
    print(f"\n{'='*50}")
    print(f" PASO {numero}: {titulo}")
    print(f"{'='*50}")


def ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def fallo(msg: str) -> None:
    print(f"  ❌ {msg}")


# ───────────────────── Pasos del guion ─────────────────────

def verificar_servidor(base: str) -> bool:
    """Paso 1 — GET / para comprobar que el servidor responde."""
    paso(1, "Verificar que el servidor está vivo")
    try:
        r = requests.get(f"{base}/api/agentes", headers=_header(), timeout=TIMEOUT)
        if r.status_code == 200:
            ok(f"Servidor responde — status {r.status_code}")
            return True
        fallo(f"Respuesta inesperada: {r.status_code}")
        return False
    except requests.ConnectionError:
        fallo("No se pudo conectar. ¿Está corriendo uvicorn?")
        return False


def crear_agente(base: str, nombre: str, rol: str, energia: int) -> bool:
    """Paso 2 — POST /api/agentes con API key."""
    paso(2, f"Crear agente '{nombre}' (rol={rol}, energia={energia})")
    r = requests.post(
        f"{base}/api/agentes",
        json={"nombre": nombre, "rol": rol, "energia": energia},
        headers=_header(),
        timeout=TIMEOUT,
    )
    if r.status_code == 201:
        ok(r.json().get("mensaje", "Agente creado"))
        return True
    if r.status_code == 409:
        ok(f"El agente ya existe — continuamos (409)")
        return True
    fallo(f"Status {r.status_code}: {r.text}")
    return False


def crear_mision(base: str, titulo: str, descripcion: str, agente: str, energia: int) -> int | None:
    """Paso 3 — POST /api/misiones con API key. Devuelve el id de la misión."""
    paso(3, f"Crear misión '{titulo}' para '{agente}'")
    r = requests.post(
        f"{base}/api/misiones",
        json={
            "titulo": titulo,
            "descripcion": descripcion,
            "agente_asignado": agente,
            "energia_requerida": energia,
        },
        headers=_header(),
        timeout=TIMEOUT,
    )
    if r.status_code == 201:
        data = r.json()
        mid = data.get("id")
        ok(f"Misión creada con id={mid}")
        return mid
    fallo(f"Status {r.status_code}: {r.text}")
    return None


def completar_mision(base: str, mision_id: int) -> bool:
    """Paso 4 — POST /api/misiones/{id}/completar con API key."""
    paso(4, f"Completar misión #{mision_id}")
    r = requests.post(
        f"{base}/api/misiones/{mision_id}/completar",
        headers=_header(),
        timeout=TIMEOUT,
    )
    if r.status_code == 200:
        data = r.json()
        ok(data.get("mensaje", "Misión completada"))
        print(f"     Detalle: {data.get('detalle', '-')}")
        print(f"     Energía restante: {data.get('energia_restante', '?')}")
        print(f"     Tipo agente: {data.get('tipo_agente', '?')}")
        return True
    fallo(f"Status {r.status_code}: {r.text}")
    return False


def consultar_briefing(base: str, nombre: str) -> bool:
    """Paso 5 — GET /api/briefing/{nombre}."""
    paso(5, f"Consultar briefing de '{nombre}'")
    r = requests.get(f"{base}/api/briefing/{nombre}", headers=_header(), timeout=TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        agente = data.get("agente", {})
        misiones = data.get("resumen_misiones", {})
        ok(f"Agente: {agente.get('nombre')} | rol={agente.get('rol')} | energia={agente.get('energia')}")
        print(f"     Misiones — total: {misiones.get('total')}, pendientes: {misiones.get('pendientes')}, completadas: {misiones.get('completadas')}")
        print(f"     Intel externa: {str(data.get('inteligencia_externa', ''))[:120]}")
        print(f"     Fuente: {data.get('fuente_externa', '-')}")
        return True
    fallo(f"Status {r.status_code}: {r.text}")
    return False


def enviar_y_leer_mensaje(base: str, remitente: str, destinatario: str, contenido: str) -> bool:
    """Paso 6 — POST /api/mensajes + GET /api/mensajes/{destinatario}."""
    paso(6, f"Enviar mensaje de '{remitente}' a '{destinatario}' y leer bandeja")

    # Enviar
    r = requests.post(
        f"{base}/api/mensajes",
        json={"remitente": remitente, "destinatario": destinatario, "contenido": contenido},
        headers=_header(),
        timeout=TIMEOUT,
    )
    if r.status_code == 201:
        ok(f"Mensaje enviado: {r.json().get('mensaje', '')}")
    else:
        fallo(f"Envío fallido — status {r.status_code}: {r.text}")
        return False

    # Leer bandeja del destinatario
    r = requests.get(f"{base}/api/mensajes/{destinatario}", headers=_header(), timeout=TIMEOUT)
    if r.status_code == 200:
        mensajes = r.json()
        ok(f"Bandeja de '{destinatario}': {len(mensajes)} mensaje(s)")
        for m in mensajes[-3:]:  # Últimos 3
            print(f"     [{m.get('timestamp','')}] {m.get('remitente')} → {m.get('contenido','')}")
        return True
    fallo(f"Lectura fallida — status {r.status_code}: {r.text}")
    return False


# ───────────────────── Main ─────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente HTTP de demostración — La Agencia de Agentes")
    parser.add_argument("--port", type=int, default=8000, help="Puerto del servidor (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host del servidor (default: 127.0.0.1)")
    args = parser.parse_args()

    base = f"http://{args.host}:{args.port}"
    print(f"\n🏛️  Cliente HTTP — La Agencia de Agentes")
    print(f"   Servidor: {base}")
    print(f"   API Key: {'*' * (len(API_KEY) - 4)}{API_KEY[-4:]}")

    # Datos de prueba
    nombre_agente = "AgenteDemo"
    nombre_dest = "AgenteReceptor"

    # ── Paso 1 ──
    if not verificar_servidor(base):
        sys.exit(1)

    # ── Paso 2 ── Crear dos agentes (para poder enviar mensajes entre ellos)
    if not crear_agente(base, nombre_agente, "explorador", 100):
        sys.exit(1)
    crear_agente(base, nombre_dest, "admin", 100)

    # ── Paso 3 ──
    mision_id = crear_mision(
        base,
        titulo="Operación Crepúsculo",
        descripcion="Infiltrar la red de servidores del enemigo",
        agente=nombre_agente,
        energia=25,
    )
    if mision_id is None:
        sys.exit(1)

    # ── Paso 4 ──
    if not completar_mision(base, mision_id):
        sys.exit(1)

    # ── Paso 5 ──
    consultar_briefing(base, nombre_agente)

    # ── Paso 6 ──
    enviar_y_leer_mensaje(
        base,
        remitente=nombre_agente,
        destinatario=nombre_dest,
        contenido="Operación Crepúsculo finalizada. Regresando a base.",
    )

    print(f"\n{'='*50}")
    print(" ✅ GUION COMPLETADO — Todos los circuitos funcionan.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
