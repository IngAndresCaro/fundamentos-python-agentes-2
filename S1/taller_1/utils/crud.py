import json
import os

def cargar_usuarios():
    """Carga usuarios desde el archivo JSON o devuelve lista vacía si no existe."""
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as f:
            return json.load(f)
    return []

def guardar_usuarios(usuarios):
    """Guarda la lista de usuarios en el archivo JSON."""
    with open("usuarios.json", "w") as f:
        json.dump(usuarios, f, indent=4)
