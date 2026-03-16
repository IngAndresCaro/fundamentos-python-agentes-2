## Nuestro proyecto esta dividido en dos archivos principales: main.py, que contiene la lógica de autenticación y el menú de opciones para el usuario, y utils/agente.py, que contiene la función pseudo_agente que simula un agente con diferentes comandos disponibles según el rol del usuario. Además, tenemos un archivo usuarios.json que almacena la información de los usuarios registrados en formato JSON.
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")
from utils import cargar_usuarios, guardar_usuarios, pseudo_agente ## Importamos las funciones necesarias desde el módulo utils

def main():
    """Lógica principal de autenticación y menú de opciones del sistema."""
    print("Bienvenido al sistema de autenticación.")

    usuarios = cargar_usuarios()
    intentoContraseña = 0
    salir= True

    while salir:
        print("Menu de ingreso al aplicativo (solo es necesario escribir el numero):")
        print("1. Ya tengo una cuenta")
        print("2. Crear una cuenta")
        print("3. Salir")
        opcion = input("Seleccione una opción (1, 2 o 3): ").strip()
        ## la primera parte de nuestro menu se basa en encontrar el usuario en nuestro archivo JSON el cual simula la conección a la base de datos, utilizamos la variable usuarios para traer la data luego utilizamos un for para recorrer la lidas de usuarios si el usuario es encontrado y la contraseña concide pasamos a la etapa 2 pero si no damos tres intentos mas, si no directamente lo bloqueamos
        if opcion == "1":
            usuario = input("Ingrese su nombre de usuario:").strip()
            contraseña = input("Ingrese su contraseña:").strip()
            for usuario_registrado in usuarios:
                if usuario_registrado["usuario"] == usuario and usuario_registrado["contraseña"] == contraseña and not usuario_registrado["bloqueado"]:
                    print(f"Bienvenido, {usuario}!")
                    pseudo_agente(usuario_registrado, usuario_registrado["rol"])
                    break ## Si el usuario y contraseña son correctos, se rompe el ciclo y no se ejecuta el bloque de "else"
            else:
                print("Usuario o contraseña incorrectos.")
                intentoContraseña += 1
                if intentoContraseña >= 3:
                    print("[Alerta] Usuario bloqueado. Comuniquese con un administrador y soporte. Cerrando sistema.")
                    for usuario_registrado in usuarios:
                        if usuario_registrado["usuario"] == usuario:
                            usuario_registrado["bloqueado"] = True
                            guardar_usuarios(usuarios)
                            salir = False
                            break ## Si el usuario es bloqueado, se rompe el ciclo y no se ejecuta el bloque de "else"
        ## La segunda parte le agregue algo interesante para saber como funciona un crud de crear un nuevo usuario, aparte de cargarlo en una nueva lista
        elif opcion == "2":
            nuevo_usuario = input("Ingrese un nuevo nombre de usuario:").strip()
            nueva_contraseña = input("Ingrese una nueva contraseña:").strip()
            nuevo_id = len(usuarios) + 1
            nuevo_usuario_dict = {"id": nuevo_id, "usuario": nuevo_usuario, "contraseña": nueva_contraseña, "rol": "invitado", "bloqueado": False}
            usuarios.append(nuevo_usuario_dict) ## append agrega el nuevo usuario al final de la lista de usuarios
            guardar_usuarios(usuarios)
        elif opcion == "3":
            print("Saliendo del sistema. ¡Hasta luego!")
            salir = False
        elif opcion not in ["1", "2", "3"]:
            print("Opción no válida, por favor intente de nuevo.")

main()
