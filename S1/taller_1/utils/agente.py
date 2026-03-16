from .crud import cargar_usuarios, actualizar_usuario, eliminar_usuario ## Importamos las funciones necesarias desde el módulo crud, que se encarga de manejar la carga, actualización y eliminación de usuarios en el archivo JSON
from datetime import datetime ## Importamos datetime para obtener la fecha actual en el comando "fecha_hoy" del pseudo_agente

ACCESO_DENEGADO = "[Acceso Denegado] Este comando requiere privilegios de administrador."


def pseudo_agente(usuario, rol):
    """Loop principal del PseudoAgente."""

    print("Has ingresado al PseudoAgente. Escribe 'salir' para terminar.")
    print("Comando 'ping'")
    print("Comando 'contar'")
    print("Comando 'validar_contraseña'")
    print("Comando 'calculadora'")
    if rol == "admin":
        print("Comando dar 'permisos'")
        print("Comando ver 'fecha_hoy'")
        print("Comando 'eliminar' usuario")

    sistema_activo = True

    while sistema_activo:
        cmd = input("PseudoAgente>: ").lower()
        if cmd == "salir":
            sistema_activo = False
        elif cmd == "ping":
            print("pong~")
        elif cmd == "contar":
            pal = input("Ingrese una palabra: ").strip().lower()
            tot_letras = len(pal)
            tot_vocales = 0
            tot_cons = 0
            for p in pal:
                if p in "aeiou":
                    tot_vocales += 1
                else:
                    tot_cons += 1
            print(f"Palabra ingresada: {pal}")
            print(f"Total de vocales: {tot_vocales}")
            print(f"Total de consonantes: {tot_cons}")
            print(f"Total de letras: {tot_letras}")
        elif cmd == "validar_contraseña":
            contraseña = input("Ingrese su contraseña: ").strip()
            validar_contraseña_por_nombre = any(palabra in contraseña for palabra in usuario["usuario"].split()) ## any devuelve True si al menos una de las palabras del nombre de usuario está presente en la contraseña, lo que hace que la contraseña sea débil
            if len(contraseña) < 8:
                print("La contraseña es débil.")
            elif validar_contraseña_por_nombre:
                print("No puede ir ninguna palabra conocida en su contraseña.")
            else:
                print("La contraseña es fuerte.")

        elif cmd == "calculadora":
            try: ## try captura errores que pueden ocurrir durante la ejecución del bloque de código, como ValueError si el usuario ingresa algo que no se puede convertir a float
                num1 = float(input("Ingrese el primer número: "))
                num2 = float(input("Ingrese el segundo número: "))
                operacion = input("Ingrese la operación (+, -, *, /): ").strip()
                if operacion == "+":
                    resultado = num1 + num2
                elif operacion == "-":
                    resultado = num1 - num2
                elif operacion == "*":
                    resultado = num1 * num2
                elif operacion == "/":
                    if num2 != 0:
                        resultado = num1 / num2
                    else:
                        print("Error: División por cero.")
                        continue
                else:
                    print("Operación no válida.")
                    continue
                print(f"Resultado: {resultado}")
            except ValueError: ## except captura errores de tipo ValueError, que pueden ocurrir si el usuario ingresa algo que no se puede convertir a float
                print("Entrada no válida. Por favor ingrese números enteros o decimales.")
        elif cmd in ["permisos", "fecha_hoy", "eliminar"] and rol != "admin":
            print(ACCESO_DENEGADO)
        elif cmd == "permisos" and rol == "admin":
            usuario_actualizar = input("Ingrese el nombre de usuario al que desea dar permisos: ").strip()
            for usuario in cargar_usuarios():
                if usuario["usuario"] == usuario_actualizar:
                    usuario["rol"] = "admin"
                    actualizar_usuario(usuario)
                    print(f"Permisos otorgados a {usuario_actualizar}.")
                    break
            else:
                print("Usuario no encontrado.")
        elif cmd == "fecha_hoy" and rol == "admin":
            fecha_hoy = datetime.now().strftime("%Y-%m-%d") ##strftime devuelve un string con la fecha formateada según el formato especificado, en este caso "año-mes-día"
            print(f"La fecha de hoy es: {fecha_hoy}")
        elif cmd == "eliminar" and rol == "admin":
            usuario_eliminar = input("Ingrese el nombre de usuario que desea eliminar: ").strip()
            eliminar_usuario(usuario_eliminar)
            print(f"Usuario {usuario_eliminar} eliminado.")
        else:
            print("Comando desconocido, intente de nuevo.")
