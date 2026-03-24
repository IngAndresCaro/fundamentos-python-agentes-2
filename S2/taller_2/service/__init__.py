from .user_service import cargar_usuarios, guardar_usuarios, actualizar_usuario, eliminar_usuario
from .historial_service import cargar_historial, eliminar_todo_historial, guardar_historial

__all__ = [
           "cargar_usuarios",
           "guardar_usuarios",
           "actualizar_usuario",
           "eliminar_usuario", 
           "cargar_historial", 
           "eliminar_todo_historial", 
           "guardar_historial"
           ]
