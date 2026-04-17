"""
agentes.py — Clases de dominio para La Agencia.

Jerarquía de agentes especializados basados en el framework ASD (.github/agents/).
Cada tipo de agente tiene su propio costo energético según su especialización.
Aquí NO hay SQL ni FastAPI — solo lógica de dominio pura.
"""

import datetime
import json
import os
import random

# -----------------------------------------------------------#
## Type Alias
# -----------------------------------------------------------#
type Historial = dict[str, str]

# -----------------------------------------------------------#
## Roles válidos del sistema (mapeados desde .github/agents/)
# -----------------------------------------------------------#
ROLES_AGENTE = {"orquestador", "spec", "backend", "frontend", "qa", "admin"}


# -----------------------------------------------------------#
## Clase base: PseudoAgente
# -----------------------------------------------------------#
class PseudoAgente:
    """Agente base — consume el 100% de la energía requerida."""

    def __init__(self, nombre: str = "Athena", energia: int = 100):
        self.nombre = nombre
        self.historial_chat: list[Historial] = []
        self.tokens: int = energia
        self.ruta_historial: str = "historial.json"

    def registrar_log(self, comando: str, rol_activo: str, mensaje: str):
        d_log: Historial = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cmd": comando,
            "rol": rol_activo,
            "descripcion": mensaje,
        }
        self.historial_chat.append(d_log)

    def gestionar_historial(self, op: str, rol: str) -> str | list[Historial]:
        self.tokens -= 30
        if op == "all":
            mensaje = f"[{self.nombre}] Historial mostrado a las {datetime.datetime.now().strftime('%H:%M:%S')}"
            self.registrar_log("hist all", rol, mensaje)
            return self.historial_chat
        if op == "clear":
            mensaje = f"[{self.nombre}] Historial borrado a las {datetime.datetime.now().strftime('%H:%M:%S')}"
            self.registrar_log("hist clear", rol, mensaje)
            self.historial_chat.clear()
            return mensaje

    def consumir_energia(self, cantidad: int) -> str:
        """Descuenta energía del agente. Retorna mensaje con el resultado."""
        if cantidad > self.tokens:
            return f"[{self.nombre}] Energía insuficiente ({self.tokens} disponible, {cantidad} requerida)."
        self.tokens -= cantidad
        return f"[{self.nombre}] Energía consumida: -{cantidad}. Restante: {self.tokens}."

    def lanzar_dado(self) -> str:
        self.tokens -= 5
        resultado = random.randint(1, 6)
        return f"[{self.nombre}] Resultado del dado: {resultado}"

    def guardar_historial(self) -> str:
        self.tokens -= 10
        with open(self.ruta_historial, "w", encoding="utf-8") as archivo:
            json.dump(self.historial_chat, archivo, indent=2, ensure_ascii=False)
        ruta_completa = os.path.abspath(self.ruta_historial)
        return f"[{self.nombre}] Historial guardado en: {ruta_completa}"

    def cargar_historial(self) -> str:
        self.tokens -= 10
        if not os.path.exists(self.ruta_historial):
            return f"[{self.nombre}] No se encontró el archivo: {self.ruta_historial}"
        with open(self.ruta_historial, "r", encoding="utf-8") as archivo:
            self.historial_chat = json.load(archivo)
        return f"[{self.nombre}] Historial cargado. {len(self.historial_chat)} registros recuperados."

    def info_sistema(self) -> str:
        self.tokens -= 10
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"[{self.nombre}] Info del Sistema:\n"
            f"  Fecha/Hora: {ahora}\n"
            f"  Directorio: {os.getcwd()}\n"
            f"  Sistema: {os.name}"
        )


# -----------------------------------------------------------#
## AgenteAdmin — Orquestador Maestro (.github/agents/agent_orchestrator)
## Ejecuta el pipeline GAIDD, coordina agentes especializados.
## Consume 50% de energía (rol de coordinación, no de ejecución).
# -----------------------------------------------------------#
class AgenteAdmin(PseudoAgente):
    """Agente Admin / Orquestador — consume la mitad de energía."""

    def __init__(self, nombre: str = "Athena", energia: int = 100):
        super().__init__(nombre, energia)

    def gestionar_historial(self, op: str, rol: str) -> str | list[Historial]:
        if op == "all":
            mensaje = f"[{self.nombre}] Historial mostrado (sin costo - Admin)"
            self.registrar_log("hist all", rol, mensaje)
            return self.historial_chat
        if op == "clear":
            mensaje = f"[{self.nombre}] Historial borrado (sin costo - Admin)"
            self.registrar_log("hist clear", rol, mensaje)
            self.historial_chat.clear()
            return mensaje

    def consumir_energia(self, cantidad: int) -> str:
        """Admin consume la mitad de energía que un agente normal."""
        costo_real = cantidad // 2
        if costo_real > self.tokens:
            return f"[{self.nombre}] Energía insuficiente ({self.tokens} disponible, {costo_real} requerida)."
        self.tokens -= costo_real
        return f"[{self.nombre}] Energía consumida (Admin): -{costo_real}. Restante: {self.tokens}."


# -----------------------------------------------------------#
## AgenteOrquestador — (.github/agents/agent_orchestrator)
## Coordina pipeline GAIDD y delega a agentes especializados.
## Consume 30% de energía (coordinación pura).
# -----------------------------------------------------------#
class AgenteOrquestador(PseudoAgente):
    """Orquestador Maestro — coordina el pipeline GAIDD y delega a agentes especializados.
    Consume solo el 30% de la energía (rol de coordinación, no ejecución)."""

    def consumir_energia(self, cantidad: int) -> str:
        costo_real = max(1, int(cantidad * 0.3))
        if costo_real > self.tokens:
            return f"[{self.nombre}] Energía insuficiente ({self.tokens} disponible, {costo_real} requerida)."
        self.tokens -= costo_real
        return f"[{self.nombre}] Energía consumida (Orquestador): -{costo_real}. Restante: {self.tokens}."


# -----------------------------------------------------------#
## AgenteSpec — (.github/agents/agent_spec)
## Analiza requerimientos, genera HU con criterios de aceptación.
## Consume 70% de energía (análisis intensivo).
# -----------------------------------------------------------#
class AgenteSpec(PseudoAgente):
    """Agente de Especificaciones — analiza requerimientos y genera HU.
    Consume el 70% de la energía (trabajo analítico intensivo)."""

    def consumir_energia(self, cantidad: int) -> str:
        costo_real = max(1, int(cantidad * 0.7))
        if costo_real > self.tokens:
            return f"[{self.nombre}] Energía insuficiente ({self.tokens} disponible, {costo_real} requerida)."
        self.tokens -= costo_real
        return f"[{self.nombre}] Energía consumida (Spec): -{costo_real}. Restante: {self.tokens}."


# -----------------------------------------------------------#
## AgenteBackend — (.github/agents/agent_backend)
## Implementa lógica de negocio, endpoints REST, persistencia.
## Consume 100% de energía (implementación pesada).
# -----------------------------------------------------------#
class AgenteBackend(PseudoAgente):
    """Agente Backend — implementa lógica de negocio, endpoints REST, persistencia.
    Consume el 100% de la energía (implementación completa)."""
    pass  # Hereda consumir_energia() de PseudoAgente (100%)


# -----------------------------------------------------------#
## AgenteFrontend — (.github/agents/agent_frontend)
## Implementa componentes, consume APIs, gestiona estado.
## Consume 100% de energía (implementación pesada).
# -----------------------------------------------------------#
class AgenteFrontend(PseudoAgente):
    """Agente Frontend — implementa componentes UI, consume APIs, gestiona estado.
    Consume el 100% de la energía (implementación completa)."""
    pass  # Hereda consumir_energia() de PseudoAgente (100%)


# -----------------------------------------------------------#
## AgenteQA — (.github/agents/agent_qa)
## Ejecuta estrategia de testing, genera casos Gherkin, identifica riesgos.
## Consume 80% de energía (testing y análisis).
# -----------------------------------------------------------#
class AgenteQA(PseudoAgente):
    """Agente QA — ejecuta estrategia de testing, genera casos Gherkin.
    Consume el 80% de la energía (testing intensivo)."""

    def consumir_energia(self, cantidad: int) -> str:
        costo_real = max(1, int(cantidad * 0.8))
        if costo_real > self.tokens:
            return f"[{self.nombre}] Energía insuficiente ({self.tokens} disponible, {costo_real} requerida)."
        self.tokens -= costo_real
        return f"[{self.nombre}] Energía consumida (QA): -{costo_real}. Restante: {self.tokens}."


# -----------------------------------------------------------#
## Mapeo rol → clase de dominio
## Usado por reconstruir_agente() en los servicios API.
# -----------------------------------------------------------#
MAPA_ROLES_CLASE: dict[str, type[PseudoAgente]] = {
    "admin": AgenteAdmin,
    "orquestador": AgenteOrquestador,
    "spec": AgenteSpec,
    "backend": AgenteBackend,
    "frontend": AgenteFrontend,
    "qa": AgenteQA,
}


def reconstruir_desde_datos(datos: dict) -> PseudoAgente:
    """Reconstruye la instancia de dominio correcta según el rol del agente."""
    clase = MAPA_ROLES_CLASE.get(datos["rol"], PseudoAgente)
    return clase(nombre=datos["nombre"], energia=datos["energia"])
