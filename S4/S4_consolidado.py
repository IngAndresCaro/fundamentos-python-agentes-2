# ============================================================
# CONSOLIDADO: Fundamentos de Python (S1 - S4 Sesión 1)
# Referencia rápida para la Sesión 2 de la Semana 4
# ============================================================

# -----------------------------------------------------------#
## S1: Entrada/Salida, Tipos Primitivos, Condicionales y Bucles
# -----------------------------------------------------------#

## I/O básico
# nombre = input("¿Cómo te llamas? ")
# print(f"Hola, {nombre}")

## Tipos primitivos: str, int, float, bool
# edad: int = int(input("Edad: "))      # Casting: str -> int
# precio: float = float("19.99")        # Casting: str -> float
# activo: bool = True

## Formateo de salida (4 formas, f-string es la moderna)
# print(f"Nombre: {nombre}, Edad: {edad}")        # f-string
# print("Nombre: %s, Edad: %d" % (nombre, edad))  # placeholder
# print("Nombre: {}, Edad: {}".format(nombre, edad))
# print("Nombre: " + nombre + ", Edad: " + str(edad))

## Condicionales
# if edad >= 18:
#     print("Mayor de edad")
# elif edad >= 13:
#     print("Adolescente")
# else:
#     print("Menor de edad")

## Operadores lógicos: and, or, not
## Operadores de comparación: >, <, >=, <=, ==, !=

## Bucle while con bandera
# activo = True
# while activo:
#     cmd = input("> ")
#     if cmd == "salir":
#         activo = False       # Bandera para salir del bucle
#     # break -> rompe el bucle inmediatamente
#     # continue -> salta a la siguiente iteración

## Bucle for
# for letra in "Python":
#     print(letra)
# for i in range(5):          # 0, 1, 2, 3, 4
#     print(i)

# -----------------------------------------------------------#
## S2: Listas, Diccionarios y Estructuras Anidadas
# -----------------------------------------------------------#

## Listas: colecciones ordenadas y mutables
# frutas = ["manzana", "pera", "uva"]
# frutas[0]          # "manzana" (índice positivo)
# frutas[-1]         # "uva" (índice negativo)
# frutas.append("kiwi")
# len(frutas)        # 4
# frutas.extend(["fresa", "mango"])

## Diccionarios: pares clave-valor
# usuario = {"nombre": "Athena", "rol": "admin", "tokens": 100}
# usuario["nombre"]              # "Athena"
# usuario.get("rol", "sin rol")  # "admin" (con valor por defecto)
# usuario.update({"tokens": 80}) # Actualizar valor
# for clave, valor in usuario.items():
#     print(f"{clave}: {valor}")

## Estructuras anidadas: list[dict] (la base del historial_chat)
# historial = [
#     {"cmd": "ping", "descripcion": "pong"},
#     {"cmd": "salir", "descripcion": "Sesión finalizada"}
# ]
# for registro in historial:
#     print(registro["cmd"])

# -----------------------------------------------------------#
## S3: Funciones, Type Hints y Excepciones
# -----------------------------------------------------------#

## Funciones con type hints y return
# def sumar(a: int, b: int) -> int:
#     """Suma dos números enteros."""
#     return a + b

## Type Alias: darle nombre a una estructura compleja
# type Historial = dict[str, str]
# type MemoriaAgente = list[Historial]

## Excepciones: try/except (filosofía EAFP de Python)
# try:
#     resultado = 10 / 0
# except ZeroDivisionError:
#     print("No se puede dividir por cero")
# else:
#     print(f"Resultado: {resultado}")

## raise: lanzar una excepción manualmente
# if rol != "admin":
#     raise PermissionError("Privilegios insuficientes")

# -----------------------------------------------------------#
## S4 Sesión 1: Programación Orientada a Objetos (POO)
# -----------------------------------------------------------#

## Conceptos clave:
# Clase: El molde/plano (blueprint) para crear objetos
# Objeto: Una instancia creada a partir de una clase
# __init__: Constructor, se ejecuta al crear el objeto
# self: Referencia a la instancia actual (indica "este objeto")
# _atributo: Convención para uso interno (Python no tiene private/protected)

## Estructura mínima de una clase:
# class MiClase:
#     def __init__(self, nombre: str):
#         self.nombre = nombre        # Atributo de instancia
#         self.contador: int = 0
#
#     def saludar(self) -> str:       # Método de instancia
#         return f"Hola, soy {self.nombre}"
#
# obj = MiClase("Test")              # Instanciar
# print(obj.saludar())               # Llamar método

# -----------------------------------------------------------#
## Estado actual del PseudoAgente (hasta S4 Sesión 1)
# -----------------------------------------------------------#

# ┌─────────────────────────────────────────┐
# │          PseudoAgente                   │
# ├─────────────────────────────────────────┤
# │ Atributos:                              │
# │   nombre: str = "Athena"                │
# │   tokens: int = 100                     │
# │   historial_chat: list[Historial] = []  │
# ├─────────────────────────────────────────┤
# │ Métodos:                                │
# │   registrar_log(cmd, rol, mensaje)      │
# │   gestionar_historial(op, rol)          │
# ├─────────────────────────────────────────┤
# │ Comandos disponibles:                   │
# │   salir, ping (-20 tokens),             │
# │   hist all/clear (-30 tokens)           │
# ├─────────────────────────────────────────┤
# │ Externo:                                │
# │   login(user, password) -> dict         │
# └─────────────────────────────────────────┘

# En la Sesión 2: vamos a separar esta clase en su propio módulo,
# integrar librerías estándar (random, json, os) y aprender herencia.
