"""
pseudo_agente.py — Módulo del PseudoAgente

Este archivo contiene la clase PseudoAgente y la función login(),
extraídas como un módulo independiente para demostrar modularización.

Puede importarse desde otro archivo:
    from pseudo_agente import PseudoAgente, AgenteAdmin, login

O ejecutarse directamente para verificar que funciona:
    python pseudo_agente.py
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
## Clase PseudoAgente (viene de S4 Sesión 1, ahora con librerías)
# -----------------------------------------------------------#
class PseudoAgente:
    def __init__(self, nombre: str = "Athena"):
        self.nombre = nombre
        self.historial_chat: list[Historial] = []
        self.tokens: int = 100
        self.ruta_historial: str = "historial.json"

    def registrar_log(self, comando: str, rol_activo: str, mensaje: str):
        d_log: Historial = {
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "cmd": comando,
            "rol": rol_activo,
            "descripcion": mensaje
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

    ## Nuevo: Librería random
    def lanzar_dado(self) -> str:
        """Lanza un dado de 6 caras usando random.randint()."""
        self.tokens -= 5
        resultado = random.randint(1, 6)
        return f"[{self.nombre}] Resultado del dado: {resultado}"

    ## Nuevo: Librería json + os (guardar a archivo)
    def guardar_historial(self) -> str:
        """Persiste el historial_chat en un archivo JSON usando json.dump()."""
        self.tokens -= 10
        with open(self.ruta_historial, "w", encoding="utf-8") as archivo:
            json.dump(self.historial_chat, archivo, indent=2, ensure_ascii=False)
        ruta_completa = os.path.abspath(self.ruta_historial)
        return f"[{self.nombre}] Historial guardado en: {ruta_completa}"

    ## Nuevo: Librería json + os (cargar desde archivo)
    def cargar_historial(self) -> str:
        """Carga el historial_chat desde un archivo JSON usando json.load()."""
        self.tokens -= 10
        if not os.path.exists(self.ruta_historial):
            return f"[{self.nombre}] No se encontró el archivo: {self.ruta_historial}"
        with open(self.ruta_historial, "r", encoding="utf-8") as archivo:
            self.historial_chat = json.load(archivo)
        return f"[{self.nombre}] Historial cargado. {len(self.historial_chat)} registros recuperados."

    ## Nuevo: Librería os + datetime (información del sistema)
    def info_sistema(self) -> str:
        """Devuelve información del sistema usando os y datetime."""
        self.tokens -= 10
        ahora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        info = (
            f"[{self.nombre}] Info del Sistema:\n"
            f"  Fecha/Hora: {ahora}\n"
            f"  Directorio: {os.getcwd()}\n"
            f"  Sistema: {os.name}\n"
            f"  Archivos: {os.listdir('.')}"
        )
        return info


# -----------------------------------------------------------#
## Herencia: AgenteAdmin extiende PseudoAgente
# -----------------------------------------------------------#
## La clase hija hereda TODOS los atributos y métodos del padre.
## Puede sobreescribir (override) métodos para cambiar su comportamiento.
class AgenteAdmin(PseudoAgente):
    def __init__(self, nombre: str = "Athena"):
        ## super() llama al constructor del padre (PseudoAgente)
        ## Así no repetimos la lógica de inicialización
        super().__init__(nombre)

    ## Override: gestionar_historial SIN consumo de tokens para admin
    def gestionar_historial(self, op: str, rol: str) -> str | list[Historial]:
        # No se descuentan tokens para el administrador
        if op == "all":
            mensaje = f"[{self.nombre}] Historial mostrado (sin costo - Admin)"
            self.registrar_log("hist all", rol, mensaje)
            return self.historial_chat
        if op == "clear":
            mensaje = f"[{self.nombre}] Historial borrado (sin costo - Admin)"
            self.registrar_log("hist clear", rol, mensaje)
            self.historial_chat.clear()
            return mensaje


# -----------------------------------------------------------#
## Función login (extraída del bucle principal)
# -----------------------------------------------------------#
def login(user: str, passwrd: str) -> dict:
    if user == "admin" and passwrd == "admin123":
        return {
            "rol": user,
            "access": True,
            "descripcion": "[Sistema] Acceso concedido. Privilegios de Administrador activados.",
        }
    if user == "invitado" and passwrd == "1234":
        return {
            "rol": user,
            "access": True,
            "descripcion": "[Sistema] Acceso concedido. Modo Invitado.",
        }
    # Fix: retorno explícito cuando las credenciales son incorrectas
    # (En S4_sesion_1.py esto retornaba None y causaba un crash)
    return {
        "rol": "",
        "access": False,
        "descripcion": "[Sistema] Credenciales incorrectas.",
    }


# -----------------------------------------------------------#
## if __name__ == "__main__": Patrón de auto-prueba
# -----------------------------------------------------------#
## Cuando ejecutas: python pseudo_agente.py   -> __name__ == "__main__" (True)
## Cuando importas: from pseudo_agente import -> __name__ == "pseudo_agente" (False)
## Esto permite tener código de prueba que NO se ejecuta al importar
if __name__ == "__main__":
    agente = PseudoAgente("Test")
    print(f"Módulo pseudo_agente cargado. Agente: {agente.nombre}, Tokens: {agente.tokens}")
    print(agente.lanzar_dado())
    print(agente.info_sistema())

    admin = AgenteAdmin("AdminTest")
    print(f"\nAgenteAdmin creado: {admin.nombre}, Tokens: {admin.tokens}")
    print(f"¿Es instancia de PseudoAgente? {isinstance(admin, PseudoAgente)}")
