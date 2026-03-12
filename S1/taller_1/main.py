from utils import cargar_usuarios, guardar_usuarios, pseudo_agente

print("Bienvenido al sistema de autenticación.")

salir= True
usuarios = cargar_usuarios()

while salir:
    print("Menu de ingreso al aplicativo (solo es necesario escribir el numero):")
    print("1. Ya tengo una cuenta")
    print("2. Crear una cuenta")
    print("3. Salir")
    opcion = input("Seleccione una opción (1, 2 o 3): ").strip()
    if opcion == "1":
        usuario = input("Ingrese su nombre de usuario:").strip()
        contraseña = input("Ingrese su contraseña:").strip()
        for usuario_registrado in usuarios:
            if usuario_registrado["usuario"] == usuario and usuario_registrado["contraseña"] == contraseña:
                print(f"Bienvenido, {usuario}!")
                pseudo_agente(usuario_registrado, usuario_registrado["rol"])
                break
        else:
            print("Usuario o contraseña incorrectos.")
    elif opcion == "2":
        nuevo_usuario = input("Ingrese un nuevo nombre de usuario:").strip()
        nueva_contraseña = input("Ingrese una nueva contraseña:").strip()
        nuevo_id = len(usuarios) + 1
        nuevo_usuario_dict = {"id": nuevo_id, "usuario": nuevo_usuario, "contraseña": nueva_contraseña, "user": "invitado"}
        usuarios.append(nuevo_usuario_dict)
        guardar_usuarios(usuarios)
    elif opcion == "3":
        print("Saliendo del sistema. ¡Hasta luego!")
        salir = False
    elif opcion not in ["1", "2", "3"]:
        print("Opción no válida, por favor intente de nuevo.")
