def pseudo_agente(usuario, rol):
    """Loop principal del PseudoAgente."""

    print("Has ingresado al PseudoAgente. Escribe 'salir' para terminar.")
    print("Comando 'ping'")
    print("Comando 'contar'")
    print("Comando 'validar_contraseña'")
    print("Comando 'calculadora'")
    if rol == "admin":
        print("Comando 'permisos'")
        print("Comando 'fecha_hoy'")

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
            if len(contraseña) < 8:
                print("La contraseña es débil.")
            else:
                print("La contraseña es fuerte.")
        elif cmd == "calculadora":
            try:
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
            except ValueError:
                print("Entrada no válida. Por favor ingrese números.")
        else:
            print("Comando desconocido, intente de nuevo.")
