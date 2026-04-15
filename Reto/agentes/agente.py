"""
agente.py — Clases de dominio PseudoAgente y AgenteAdmin.

Adaptado de S4/pseudo_agente.py para el reto de consolidación.
Aquí NO hay SQL ni FastAPI — solo lógica de dominio pura.
"""

import datetime
import json
import os
import random

# -----------------------------------------------------------#
## Type Alias (viene de S3)
# -----------------------------------------------------------#
type Historial = dict[str, str]


# -----------------------------------------------------------#
## Clase PseudoAgente
# -----------------------------------------------------------#
class PseudoAgente:
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
## Herencia: AgenteAdmin extiende PseudoAgente
# -----------------------------------------------------------#
class AgenteAdmin(PseudoAgente):
    def __init__(self, nombre: str = "Athena", energia: int = 100):
        super().__init__(nombre, energia)

    def gestionar_historial(self, op: str, rol: str) -> str | list[Historial]:
        # Admin no gasta tokens al gestionar historial
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
