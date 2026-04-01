#Día 2: Librerías, Módulos y Herencia
## ¿Qué es un módulo? Un archivo .py que contiene código reutilizable (funciones, clases, variables)
## ¿Qué es una librería? Una colección de módulos agrupados
## ¿Por qué modularizar?
### 1. Organización: cada archivo tiene una responsabilidad clara
### 2. Reutilización: importas lo que necesitas sin copiar/pegar
### 3. Mantenibilidad: cambias un módulo sin romper el resto
## En el mundo de agentes de IA, cada "tool" suele vivir en su propio módulo

# -----------------------------------------------------------#
## Formas de importar módulos
# -----------------------------------------------------------#

## 1. import completo: accedes con prefijo modulo.funcion
import math
print(math.sqrt(144))   # 12.0
print(math.pi)          # 3.14159...

## 2. import específico: from X import Y (sin prefijo)
from math import sqrt, pi
print(sqrt(144))         # 12.0
print(pi)                # 3.14159...

## 3. import con alias: import X as Y (nombre corto)
import datetime as dt
ahora = dt.datetime.now()
print(ahora.strftime('%Y-%m-%d %H:%M:%S'))

## 4. import de todo: from X import * (NO RECOMENDADO)
# from math import *
## ¿Por qué no? Contamina el namespace: si dos módulos tienen una función
## con el mismo nombre, no sabes cuál estás usando. Siempre sé explícito.

# -----------------------------------------------------------#
## Librería estándar de Python (ya viene instalada)
# -----------------------------------------------------------#

## datetime - Ya lo usamos desde S2
import datetime
fecha = datetime.datetime.now()
print(f"Fecha actual: {fecha.strftime('%Y-%m-%d')}")
print(f"Hora actual: {fecha.strftime('%H:%M:%S')}")

## random - Generación de valores aleatorios
import random
print(random.choice(["Hola", "Adiós", "Tal vez"]))   # Elemento aleatorio de una lista
print(random.randint(1, 6))                            # Entero aleatorio entre 1 y 6
## Para revisión autónoma: random.shuffle(), random.sample(), random.uniform()

## json - Lectura y escritura de datos estructurados
import json

datos = {"nombre": "Athena", "tokens": 100, "estado": "activo"}

# dict -> string JSON (dumps = dump to string)
json_str = json.dumps(datos, indent=2, ensure_ascii=False)
print(json_str)

# string JSON -> dict (loads = load from string)
datos_cargados = json.loads(json_str)
print(datos_cargados["nombre"])   # "Athena"

# dict -> archivo JSON (dump = dump to file)
# with open("datos.json", "w", encoding="utf-8") as f:
#     json.dump(datos, f, indent=2, ensure_ascii=False)

# archivo JSON -> dict (load = load from file)
# with open("datos.json", "r", encoding="utf-8") as f:
#     datos_desde_archivo = json.load(f)

## os - Interacción con el sistema operativo
import os
print(f"Directorio actual: {os.getcwd()}")
print(f"Archivos aquí: {os.listdir('.')}")
print(f"¿Existe datos.json?: {os.path.exists('datos.json')}")
## Para revisión autónoma: os.mkdir(), os.remove(), os.environ, pathlib (alternativa moderna)

## Otros módulos útiles de la librería estándar:
# math     -> funciones matemáticas (sqrt, pi, ceil, floor)
# sys      -> información del intérprete de Python
# collections -> estructuras de datos avanzadas (Counter, defaultdict)
# pathlib  -> manejo moderno de rutas (alternativa a os.path)

# -----------------------------------------------------------#
## Librerías externas (se instalan con pip)
# -----------------------------------------------------------#

## pip es el gestor de paquetes de Python
## Se instalan desde la terminal (NO desde el código):
# pip install nombre_libreria

## Librerías populares:
# pip install requests       -> Peticiones HTTP (consumir APIs)
# pip install rich           -> Salida bonita en consola (colores, tablas)
# pip install python-dotenv  -> Variables de entorno desde archivo .env

## En el mundo de agentes de IA:
# pip install openai         -> SDK oficial de OpenAI (GPT)
# pip install anthropic      -> SDK oficial de Anthropic (Claude)

## Para revisión autónoma:
### ¿Qué es un entorno virtual (venv) y por qué es importante?
### ¿Qué hace: pip freeze > requirements.txt?
### ¿Qué es pyproject.toml?

# -----------------------------------------------------------#
## Crear tu propio módulo (Modularización)
# -----------------------------------------------------------#

## Estructura de nuestro proyecto ahora:
# S4/
# ├── pseudo_agente.py    <- Módulo: clase PseudoAgente, AgenteAdmin y login()
# ├── S4_sesion_2.py      <- Este archivo: programa principal
# └── S4_consolidado.py   <- Referencia rápida del curso

## Para importar desde nuestro módulo usamos from/import:
from pseudo_agente import PseudoAgente, AgenteAdmin, login

## ¿Cómo sabe Python dónde buscar pseudo_agente?
## 1. Primero busca en el directorio actual (donde ejecutas el script)
## 2. Luego en las rutas de sys.path
## Por eso es importante ejecutar desde la carpeta S4/: cd S4 && python S4_sesion_2.py

## El patrón: if __name__ == "__main__":
## Cuando ejecutas un archivo directamente -> __name__ vale "__main__"
## Cuando lo importas desde otro archivo   -> __name__ vale el nombre del módulo
## Esto permite que pseudo_agente.py tenga código de prueba que NO se ejecuta al importarlo
## Revisa el final de pseudo_agente.py para ver este patrón en acción

# -----------------------------------------------------------#
## Herencia: Reutilizar y Especializar clases
# -----------------------------------------------------------#

## Concepto: Una clase hija HEREDA todos los atributos y métodos del padre
## Sintaxis: class ClaseHija(ClasePadre):
## super(): Permite llamar métodos del padre desde la clase hija

## Ejemplo ya implementado en pseudo_agente.py:
## class AgenteAdmin(PseudoAgente):
##     def __init__(self, nombre):
##         super().__init__(nombre)     # Llama al __init__ del padre
##
##     def gestionar_historial(self, op, rol):
##         # Override: misma lógica PERO sin descontar tokens
##         ...

## ¿Por qué herencia y no copiar/pegar?
## 1. Si corriges un bug en PseudoAgente, AgenteAdmin lo hereda automáticamente
## 2. Reduces duplicación de código
## 3. Puedes crear múltiples especializaciones (AgenteAdmin, AgentePremium, etc.)

## isinstance() - Verificar si un objeto es instancia de una clase
# agente = AgenteAdmin("Zeus")
# print(isinstance(agente, PseudoAgente))   # True (hereda de PseudoAgente)
# print(isinstance(agente, AgenteAdmin))    # True

## Para revisión autónoma:
### ¿Qué es herencia múltiple? class Hijo(Padre1, Padre2):
### ¿Qué son las clases abstractas (ABC)?
### ¿Qué es polimorfismo y cómo se relaciona con override?

# -----------------------------------------------------------#
## PseudoAgente: Programa principal con librerías y herencia
# -----------------------------------------------------------#

## Login (mismo patrón, ahora importado desde pseudo_agente.py)
intentos = 0
rol_actual = ""
tiene_acceso = False

while intentos < 3 and not tiene_acceso:
    usuario = input("Usuario: ").strip().lower()
    password = input("Contraseña: ").strip()

    login_attempt = login(usuario, password)
    rol_actual = login_attempt["rol"]
    tiene_acceso = login_attempt["access"]

    if not tiene_acceso:
        intentos += 1
        print(f"[Error] Credenciales incorrectas. Te quedan {3 - intentos} intentos.")
    else:
        print(login_attempt["descripcion"])

## Instanciación según rol: Admin obtiene AgenteAdmin, Invitado obtiene PseudoAgente
## Ambas clases comparten la misma interfaz (mismos métodos), pero se comportan diferente
## Esto es polimorfismo en acción
if tiene_acceso:
    if rol_actual == "admin":
        mi_agente = AgenteAdmin()
    else:
        mi_agente = PseudoAgente()

    print(f"\n[Sistema] Agente {mi_agente.nombre} activado. Tipo: {type(mi_agente).__name__}")

    ## Intentar cargar historial previo (librería json + os)
    print(mi_agente.cargar_historial())

    ## Bucle principal: SIN break, usamos bandera pseudo_activo
    pseudo_activo = True

    while pseudo_activo:
        print(f"\n[{mi_agente.nombre}] Tokens disponibles: {mi_agente.tokens}")

        ## Verificar tokens: si se agotan, apagar sin break
        if mi_agente.tokens <= 0:
            print(f"[{mi_agente.nombre}] Tokens agotados. Apagando...")
            mi_agente.registrar_log("sistema", rol_actual, "Agente apagado por falta de tokens")
            pseudo_activo = False
            continue

        cmd = input(f"\n{usuario}@{mi_agente.nombre}>: ").strip().lower()

        if cmd == "salir":
            print(f"[{mi_agente.nombre}] Apagando sistemas...")
            mi_agente.registrar_log(cmd, rol_actual, "Sesión finalizada")
            pseudo_activo = False

        elif cmd == "ping":
            mi_agente.tokens -= 20
            print("pong~")
            mi_agente.registrar_log(cmd, rol_actual, "Ping enviado, pong recibido.")

        ## hist: all, clear, o búsqueda por palabra
        elif cmd.startswith("hist"):
            if " " in cmd:
                sub = cmd.split(" ")[-1]
                resultado = mi_agente.gestionar_historial(sub, rol_actual)
                print(resultado)
            else:
                found = []
                word = input("Ingresa la palabra clave a buscar: ").strip().lower()
                for elem in mi_agente.historial_chat:
                    if word in elem["descripcion"].lower():
                        found.append(elem)
                print(f"[{mi_agente.nombre}] Total de coincidencias: {len(found)}")
                if len(found) > 0:
                    for i, elem in enumerate(found):
                        print(f"  {i+1} >>> {elem}")
                else:
                    print(f"[{mi_agente.nombre}] No encontré registros que coincidan.")

        ## Nuevo comando: dado (librería random)
        elif cmd == "dado":
            resultado = mi_agente.lanzar_dado()
            print(resultado)
            mi_agente.registrar_log(cmd, rol_actual, resultado)

        ## Nuevo comando: guardar (librería json - persistir a archivo)
        elif cmd == "guardar":
            resultado = mi_agente.guardar_historial()
            print(resultado)
            mi_agente.registrar_log(cmd, rol_actual, "Historial guardado en archivo JSON")

        ## Nuevo comando: cargar (librería json + os - leer desde archivo)
        elif cmd == "cargar":
            resultado = mi_agente.cargar_historial()
            print(resultado)
            mi_agente.registrar_log(cmd, rol_actual, "Historial cargado desde archivo JSON")

        ## Nuevo comando: exportar (json.dumps para ver el historial formateado)
        elif cmd == "exportar":
            mi_agente.tokens -= 15
            historial_json = json.dumps(mi_agente.historial_chat, indent=2, ensure_ascii=False)
            print(f"[{mi_agente.nombre}] Historial exportado como JSON:")
            print(historial_json)
            mi_agente.registrar_log(cmd, rol_actual, "Historial exportado como JSON formateado")

        ## Nuevo comando: info (librería os + datetime, solo admin)
        elif cmd == "info":
            if rol_actual == "admin":
                resultado = mi_agente.info_sistema()
                print(resultado)
                mi_agente.registrar_log(cmd, rol_actual, "Info del sistema consultada")
            else:
                print(f"[{mi_agente.nombre}] Acceso Denegado. Requiere privilegios de administrador.")
                mi_agente.registrar_log(cmd, rol_actual, "[Denegado] Intento de acceso a info del sistema")

        else:
            print(f"[{mi_agente.nombre}] Comando no existe. Intente de nuevo.")
            mi_agente.registrar_log(cmd, rol_actual, "Comando no reconocido")

    ## Al salir: mostrar historial final y guardar automáticamente
    print(f"\n--- Historial final ({len(mi_agente.historial_chat)} registros) ---")
    for reg in mi_agente.historial_chat:
        print(f"  [{reg['timestamp']}] {reg['cmd']} -> {reg['descripcion']}")

    print(mi_agente.guardar_historial())
    print(f"[Sistema] Sesión terminada. Tokens restantes: {mi_agente.tokens}")

else:
    print("[Sistema] Acceso denegado. Sistema bloqueado.")
