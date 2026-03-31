## Nuestro proyecto esta dividido en dos archivos principales: main.py, que contiene la lógica de autenticación y el menú de opciones para el usuario, y utils/agente.py, que contiene la función pseudo_agente que simula un agente con diferentes comandos disponibles según el rol del usuario. Además, tenemos un archivo usuarios.json que almacena la información de los usuarios registrados en formato JSON.
import sys
import io
# pylint: disable=import-error ## Importamos la función pseudo_agente desde el módulo utils
from utils import pseudo_agente
# pylint: disable=import-error ## Importamos las funciones necesarias desde el módulo service
from service.user_service import cargar_usuarios, guardar_usuarios, actualizar_usuario, eliminar_usuario
# pylint: disable=import-error ## Importamos las funciones necesarias desde el módulo service para manejar el historial de comandos
from service.historial_service import cargar_historial, eliminar_todo_historial, guardar_historial
# pylint: disable=import-error ## Importamos el modelo Usuario para tipar los datos que vienen del JSON
from models.usuario import Usuario

if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stdin, io.TextIOWrapper):
    sys.stdin.reconfigure(encoding="utf-8")

def crear_nuevo_usuario(usuarios: list[Usuario]) -> None:
    """Solicita datos al usuario, crea un nuevo registro con rol 'invitado' y lo guarda en el JSON."""
    nuevo_nombre = input("Ingrese un nuevo nombre de usuario:").strip()
    nueva_contrasena = input("Ingrese una nueva contraseña:").strip()
    nuevo_usuario = Usuario(
        id=len(usuarios) + 1,
        usuario=nuevo_nombre,
        contraseña=nueva_contrasena,
        rol="invitado",
        bloqueado=False,
    )
    ## append agrega el nuevo usuario al final de la lista de usuarios
    usuarios.append(nuevo_usuario)
    guardar_usuarios([u.to_dict() for u in usuarios]) ## to_dict() convierte cada Usuario a dict para que guardar_usuarios pueda serializarlo a JSON

def usuario_incorrecto(usuarios: list[Usuario], usuario: str, intento_contrasena: int) -> tuple[int, bool]:
    """Maneja los intentos de contraseña incorrecta y bloquea al usuario después de 3 intentos fallidos."""
    print("Usuario o contraseña incorrectos.")
    intento_contrasena += 1
    salir = True
    if intento_contrasena >= 3:
        print("[Alerta] Usuario bloqueado. Comuniquese con un administrador y soporte. Cerrando sistema.")
        for usuario_registrado in usuarios:
            if usuario_registrado.usuario == usuario: ## acceso por atributo gracias al modelo Usuario
                usuario_registrado.bloqueado = True
                guardar_usuarios([u.to_dict() for u in usuarios])
                salir = False
                ## Si el usuario es bloqueado, se rompe el ciclo y no se ejecuta el bloque de "else"
                break
    return intento_contrasena, salir

def main():
    """Lógica principal de autenticación y menú de opciones del sistema."""
    print("Bienvenido al sistema de autenticación.")

    usuarios: list[Usuario] = [Usuario.from_dict(u) for u in cargar_usuarios()] ## Convertimos los dicts del JSON a objetos Usuario
    intento_contrasena = 0
    salir = True

    while salir:
        print("Menu de ingreso al aplicativo (solo es necesario escribir el numero):")
        print("1. Ya tengo una cuenta")
        print("2. Crear una cuenta")
        print("3. Salir")
        opcion = input("Seleccione una opción (1, 2 o 3): ").strip()
        ## la primera parte de nuestro menu se basa en encontrar el usuario en nuestro archivo JSON el cual simula la conección a la base de datos, utilizamos la variable usuarios para traer la data luego utilizamos un for para recorrer la lidas de usuarios si el usuario es encontrado y la contraseña concide pasamos a la etapa 2 pero si no damos tres intentos mas, si no directamente lo bloqueamos
        if opcion == "1":
            usuario = input("Ingrese su nombre de usuario:").strip()
            contrasena = input("Ingrese su contraseña:").strip()
            for usuario_registrado in usuarios:
                if usuario_registrado.usuario == usuario and usuario_registrado.contraseña == contrasena and not usuario_registrado.bloqueado: ## acceso por atributo gracias al modelo Usuario
                    print(f"Bienvenido, {usuario}!")
                    ## pasamos el objeto Usuario directamente — pseudo_agente ahora está tipado con Usuario
                    pseudo_agente(
                        usuario_registrado,
                        usuario_registrado.rol,
                        cargar_usuarios,
                        actualizar_usuario,
                        eliminar_usuario,
                        cargar_historial,
                        eliminar_todo_historial,
                        guardar_historial)
                    ##se rompe el ciclo y no se ejecuta el bloque de "else"
                    break
            else:
                intento_contrasena, salir = usuario_incorrecto(usuarios, usuario, intento_contrasena)
        ## La segunda parte le agregue algo interesante para saber como funciona un crud de crear un nuevo usuario,
        # aparte de cargarlo en una nueva lista
        elif opcion == "2":
            crear_nuevo_usuario(usuarios)
        elif opcion == "3":
            print("Saliendo del sistema. ¡Hasta luego!")
            salir = False
        else:
            print("Opción no válida, por favor intente de nuevo.")


if __name__ == "__main__":
    main()
