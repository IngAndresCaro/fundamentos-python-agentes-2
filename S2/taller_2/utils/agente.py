from datetime import datetime ## Importamos datetime para obtener la fecha actual en el comando "fecha_hoy" del pseudo_agente

ACCESO_DENEGADO = "[Acceso Denegado] Este comando requiere privilegios de administrador."


def pseudo_agente(
    usuario,
    rol,
    cargar_usuarios,
    actualizar_usuario,
    eliminar_usuario,
    cargar_historial,
    eliminar_todo_historial,
    guardar_historial
):
    """Loop principal del PseudoAgente."""

    def registrar_historial(descripcion, comando):
        """Registra comandos ejecutados."""
        historial = cargar_historial()
        historial.append(
            {
                "timestamp": datetime.now().isoformat(),
                "rol": rol,
                "cmd": comando,
                "descripcion": descripcion,
            }
        )
        guardar_historial(historial)

    def mostrar_historial_encontrado(entradas, titulo):
        """Muestra historial organizado de forma legible."""
        if not entradas:
            print("No hay resultados para mostrar.")
            return

        print(f"\n{titulo}")
        print("=" * 70)
        for indice, entrada in enumerate(entradas, start=1):
            print(f"Registro {indice}")
            print(f"  Fecha       : {entrada.get('timestamp', 'sin fecha')}")
            print(f"  Rol         : {entrada.get('rol', 'sin rol')}")
            print(f"  Comando     : {entrada.get('cmd', 'sin cmd')}")
            print(f"  Descripcion : {entrada.get('descripcion', '')}")
            if indice < len(entradas):
                print("-" * 70)

    def buscar_en_historial(historial, busqueda):
        """Busca entradas en el historial que contengan la palabra clave."""
        resultados = []

        for entrada in historial:
            descripcion = str(entrada.get("descripcion", "")).lower()
            palabras_descripcion = descripcion.split()
            # Uso `in` para saber si la palabra clave está dentro del texto de la descripción, y `split()` me ayuda a separar la descripción en palabras para recorrerla de forma más clara.
            if busqueda in descripcion or any(busqueda in palabra for palabra in palabras_descripcion):
                resultados.append(entrada)

        return resultados

    print("Has ingresado al PseudoAgente. Escribe 'salir' para terminar.")
    print("Comando 'ping'")
    print("Comando 'contar'")
    print("Comando 'validar_contraseña'")
    print("Comando 'calculadora'")
    print("Comando 'historial'")
    if rol == "admin":
        print("Comando dar 'permisos'")
        print("Comando ver 'fecha_hoy'")
        print("Comando 'eliminar' usuario")

    sistema_activo = True

    while sistema_activo:
        cmd = input("PseudoAgente>: ").lower()
        if cmd == "salir":
            # Comando para salir del PseudoAgente.
            registrar_historial("Se ha solicitado terminar la sesión.", cmd)
            sistema_activo = False
        elif cmd == "ping":
            #Comando de respuesta
            print("pong~")
            registrar_historial("Comando ping ejecutado", cmd)
        elif cmd == "contar":
            #Comando para contar vocales, consonantes y letras de una palabra ingresada por el usuario.
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
            registrar_historial(f"Comando contar ejecutado: {pal}", cmd)
        elif cmd == "validar_contraseña":
            #Comando para ayudar a crear contraseñas seguras
            contraseña = input("Ingrese su contraseña: ").strip()
            validar_contraseña_por_nombre = any(palabra in contraseña for palabra in usuario["usuario"].split()) ## any devuelve True si al menos una de las palabras del nombre de usuario está presente en la contraseña, lo que hace que la contraseña sea débil
            if len(contraseña) < 8:
                print("La contraseña es débil.")
                registrar_historial("Comando validar_contraseña falló: contraseña demasiado corta", cmd)
            elif validar_contraseña_por_nombre:
                print("No puede ir ninguna palabra conocida en su contraseña.")
                registrar_historial("Comando validar_contraseña falló: contraseña contiene palabras del nombre de usuario", cmd)
            else:
                print("La contraseña es fuerte.")
                registrar_historial(f"Comando validar_contraseña ejecutado: {contraseña}", cmd)
        elif cmd == "calculadora":
            #Comando para realizar operaciones matemáticas básicas
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
                        registrar_historial("Comando calculadora falló: división por cero", cmd)
                        continue
                else:
                    print("Operación no válida.")
                    registrar_historial("Comando calculadora falló: operación no válida", cmd)
                    continue
                print(f"Resultado: {resultado}")
                registrar_historial(f"Comando calculadora ejecutado: {num1} {operacion} {num2} = {resultado}", cmd)
            except ValueError: ## except captura errores de tipo ValueError, que pueden ocurrir si el usuario ingresa algo que no se puede convertir a float
                print("Entrada no válida. Por favor ingrese números enteros o decimales.")
                registrar_historial("Comando calculadora falló: entrada no válida", cmd)
        elif cmd == "historial":
            #Comando para manejar el historial
            print("Comando para ver todo el historial 'historial all'")
            print("Comando para eliminar todo el historial 'historial clear'")
            print("Comando Buscar en el historial 'historial'")
            cmd_historial = input("Ingrese el comando de historial: ").strip().lower()
            if cmd_historial == "historial all":
                #Traer todo el historial
                historial = cargar_historial()
                if historial:
                    mostrar_historial_encontrado(historial, "Historial completo")
                else:
                    print("[PseudoAgente] No hay historial disponible.")
            elif cmd_historial == "historial clear":
                #Eliminar todo el historial
                print("Eliminando todo el historial...")
                eliminar_todo_historial()
            elif cmd_historial == "historial":
                #Buscar en el historial por palabra clave
                busqueda = input("Ingresa la palabra clave a buscar: ").strip().lower()
                print(f"\nBuscando '{busqueda}' en el historial...")
                historial = cargar_historial()
                resultados = buscar_en_historial(historial, busqueda)
                if resultados:
                    print(f"[PseudoAgente] Se encontraron {len(resultados)} coincidencias.")
                    mostrar_historial_encontrado(resultados, f"Resultados para '{busqueda}'")
                    registrar_historial(f"Comando historial ejecutado: búsqueda '{busqueda}' con {len(resultados)} coincidencias", cmd)
                else:
                    print("[PseudoAgente] No encontré registros que coincidan con esa palabra.")
                    registrar_historial(f"Comando historial ejecutado: búsqueda '{busqueda}' sin resultados", cmd)

            else:
                print("Comando de historial no válido.")
        elif cmd in ["permisos", "fecha_hoy", "eliminar"] and rol != "admin":
            print(ACCESO_DENEGADO)
        elif cmd == "permisos" and rol == "admin":
            usuario_actualizar = input("Ingrese el nombre de usuario al que desea dar permisos: ").strip()
            for usuario in cargar_usuarios():
                if usuario["usuario"] == usuario_actualizar:
                    usuario["rol"] = "admin"
                    actualizar_usuario(usuario)
                    print(f"Permisos otorgados a {usuario_actualizar}.")
                    registrar_historial(f"Comando permisos ejecutado: permisos otorgados a {usuario_actualizar}", cmd)
                    break
            else:
                print("Usuario no encontrado.")
                registrar_historial("Comando permisos falló: usuario no encontrado", cmd)
        elif cmd == "fecha_hoy" and rol == "admin":
            fecha_hoy = datetime.now().strftime("%Y-%m-%d") ##strftime devuelve un string con la fecha formateada según el formato especificado, en este caso "año-mes-día"
            print(f"La fecha de hoy es: {fecha_hoy}")
            registrar_historial(f"Comando fecha_hoy ejecutado: {fecha_hoy}", cmd)
        elif cmd == "eliminar" and rol == "admin":
            usuario_eliminar = input("Ingrese el nombre de usuario que desea eliminar: ").strip()
            eliminar_usuario(usuario_eliminar)
            print(f"Usuario {usuario_eliminar} eliminado.")
            registrar_historial(f"Comando eliminar ejecutado: {usuario_eliminar} eliminado", cmd)
        else:
            print("Comando desconocido, intente de nuevo.")
            registrar_historial(f"Comando desconocido ejecutado: {cmd}", cmd)
