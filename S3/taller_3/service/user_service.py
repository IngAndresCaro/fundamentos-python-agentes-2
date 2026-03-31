import json ## Me permite trabajar con archivos JSON para almacenar y recuperar la información de los usuarios, simula la conexión a una base de datos simple utilizando un archivo JSON como almacenamiento persistente.
import os ## Me permite interactuar con el sistema de archivos, como verificar si el archivo JSON existe antes de intentar cargarlo, lo que ayuda a evitar errores si el archivo no está presente.

##ASCII es un estándar de codificación de caracteres que representa texto en computadoras y otros dispositivos que utilizan texto. UTF-8 es una codificación de caracteres que puede representar todos los caracteres en el estándar Unicode, lo que incluye caracteres de muchos idiomas diferentes, así como símbolos y emojis. Al configurar la codificación de entrada y salida a UTF-8, nos aseguramos de que el programa pueda manejar correctamente caracteres especiales, acentos y otros símbolos que no están incluidos en el conjunto ASCII básico, lo que es especialmente importante para aplicaciones que pueden tener usuarios con nombres o contraseñas que contienen dichos caracteres.

RUTA_JSON = os.path.join(os.path.dirname(__file__), "..", "repository", "usuarios.json") ## Ruta absoluta al archivo JSON en la carpeta repository/

## GET Me permite traer todos los usuarios
def cargar_usuarios():
    """Carga usuarios desde el archivo JSON o devuelve lista vacía si no existe."""
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r", encoding="utf-8") as archivo: ## encoding="utf-8" asegura que el archivo se lea correctamente, especialmente si contiene caracteres especiales o acentos, lo que es importante para manejar nombres de usuario o contraseñas con caracteres no ASCII.
            return json.load(archivo)
    return []

## PUT Me permite guardar los usuarios en el archivo Json
def guardar_usuarios(usuarios):
    """Guarda la lista de usuarios en el archivo JSON."""
    with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
        json.dump(usuarios, archivo, indent=4, ensure_ascii=False) ## indent=4 hace que el archivo JSON sea más legible al agregar sangría y saltos de línea, lo que facilita la lectura y edición manual del archivo. ensure_ascii=False permite que los caracteres no ASCII se guarden correctamente en el archivo JSON, lo que es importante para manejar caracteres especiales o acentos en los nombres de usuario o contraseñas.

## UPDATEActualizar recorre toda la lista busca el usuario especifico y le agrega el nuevo rol
def actualizar_usuario(usuario_actualizado):
    """Actualiza un usuario específico en el archivo JSON."""
    usuarios = cargar_usuarios()
    for i, usuario in enumerate(usuarios):
        if usuario["id"] == usuario_actualizado["id"]:
            usuarios[i] = usuario_actualizado
            guardar_usuarios(usuarios)
            return True
    return False

## DELETE Eliminar funciona recorre toda la carga de usuarios si encuentra su nombre en la lista de usaurios procede a eliminarlo, luego los demas los guarda en una nueva lista
def eliminar_usuario(usuario):
    """Elimina un usuario específico del archivo JSON."""
    usuarios = cargar_usuarios()
    usuarios = [usuario_json for usuario_json in usuarios if usuario_json["usuario"] != usuario]
    guardar_usuarios(usuarios)
    return True
