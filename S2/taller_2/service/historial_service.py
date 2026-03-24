import json ## Me permite trabajar con archivos JSON para almacenar y recuperar la información de los usuarios, simula la conexión a una base de datos simple utilizando un archivo JSON como almacenamiento persistente.
import os ## Me permite interactuar con el sistema de archivos, como verificar si el archivo JSON existe antes de intentar cargarlo, lo que ayuda a evitar errores si el archivo no está presente.

##ASCII es un estándar de codificación de caracteres que representa texto en computadoras y otros dispositivos que utilizan texto. UTF-8 es una codificación de caracteres que puede representar todos los caracteres en el estándar Unicode, lo que incluye caracteres de muchos idiomas diferentes, así como símbolos y emojis. Al configurar la codificación de entrada y salida a UTF-8, nos aseguramos de que el programa pueda manejar correctamente caracteres especiales, acentos y otros símbolos que no están incluidos en el conjunto ASCII básico, lo que es especialmente importante para aplicaciones que pueden tener usuarios con nombres o contraseñas que contienen dichos caracteres.

RUTA_JSON = os.path.join(os.path.dirname(__file__), "..", "repository", "historial_chat.json") ## Ruta absoluta al archivo JSON en la carpeta repository/

## GET Me permite traer todo el historial
def cargar_historial():
    """Carga historial desde el archivo JSON o devuelve lista vacía si no existe."""
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    return []

## PUT Me permite guardar el historial en el archivo Json
def guardar_historial(historial):
    """Guarda la lista de historial en el archivo JSON."""
    with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
        json.dump(historial, archivo, indent=4, ensure_ascii=False)

## DELETE Eliminar todo el historial
def eliminar_todo_historial():
    """Elimina todo el historial del archivo JSON."""
    print("Eliminando historial...")
    with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
        json.dump([], archivo, indent=4, ensure_ascii=False)