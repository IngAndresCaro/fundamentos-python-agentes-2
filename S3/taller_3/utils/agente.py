from datetime import datetime
from typing import Callable
# pylint: disable=import-error ## Importamos el modelo Usuario para tipar el parámetro usuario de pseudo_agente
from models.usuario import Usuario

## type es la palabra clave de Python 3.12+ para crear alias de tipo
## Recuerdo representa un registro individual del historial: todas sus claves y valores son strings
type Recuerdo = dict[str, str]
## MemoriaAgente representa el historial completo: una lista de Recuerdos
# ayuda a que la estructura de datos de su propia historia y añade semántica al código
type MemoriaAgente = list[Recuerdo]

ACCESO_DENEGADO = "[Acceso Denegado] Este comando requiere privilegios de administrador."

def registrar_historial(descripcion: str, comando: str, guardar_historial: Callable, cargar_historial: Callable[[],  MemoriaAgente], rol: str) -> None:
    """Registra comandos ejecutados. Función anidada con acceso a rol, cargar_historial y guardar_historial del scope de pseudo_agente."""
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

def mostrar_historial_encontrado(entradas: MemoriaAgente, titulo: str) -> None:
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

def contar_letras(palabra: str) -> str:
    """Cuenta vocales, consonantes y total de letras de una palabra y retorna el resultado formateado como texto."""
    vocales = sum(1 for c in palabra if c in "aeiou")
    consonantes = len(palabra) - vocales
    return (
        f"Palabra ingresada: {palabra}\n"
        f"Total de vocales: {vocales}\n"
        f"Total de consonantes: {consonantes}\n"
        f"Total de letras: {len(palabra)}"
    )

def calculadora(num1: float, num2: float, operacion: str) -> str:
    """Realiza una operación matemática básica entre dos números y retorna el resultado como texto. No hace entrada/salida."""
    if operacion == "+":
        return f"{num1} + {num2} = {num1 + num2}"
    elif operacion == "-":
        return f"{num1} - {num2} = {num1 - num2}"
    elif operacion == "*":
        return f"{num1} * {num2} = {num1 * num2}"
    elif operacion == "/":
        if num2 != 0:
            return f"{num1} / {num2} = {num1 / num2}"
        return "Error: División por cero."
    return f"Operación '{operacion}' no válida."

def validar_password(contrasena: str, usuario_nombre: str) -> str:
    """Valida la fortaleza de una contraseña: mínimo 8 caracteres y que no contenga palabras del nombre de usuario. No hace entrada/salida."""
    if len(contrasena) < 8:
        return "La contraseña es débil: demasiado corta (mínimo 8 caracteres)."
    ## any devuelve True si al menos una de las palabras del nombre de usuario está presente en la contraseña
    if any(palabra in contrasena for palabra in usuario_nombre.split()):
        return "La contraseña es débil: contiene palabras del nombre de usuario."
    return "La contraseña es fuerte."

def cmd_validar_contrasena(usuario_nombre: str, cmd: str, guardar_historial, cargar_historial, rol: str) -> None:
    """Solicita la contraseña al usuario, delega la validación a validar_password y registra el resultado en el historial."""
    contrasena = input("Ingrese su contraseña: ").strip()
    resultado = validar_password(contrasena, usuario_nombre)
    print(resultado)
    if "fuerte" in resultado:
        registrar_historial(f"Comando validar_contraseña ejecutado: {contrasena}", cmd, guardar_historial, cargar_historial, rol)
    else:
        registrar_historial(f"Comando validar_contraseña falló: {resultado}", cmd, guardar_historial, cargar_historial, rol)

def cmd_calculadora(cmd: str, guardar_historial, cargar_historial, rol: str) -> None:
    """Solicita dos números y una operación al usuario, delega el cálculo a calculadora() y registra el resultado en el historial."""
    ## try captura errores que pueden ocurrir durante la ejecución del bloque de código, como ValueError si el usuario ingresa algo que no se puede convertir a float
    try:
        num1 = float(input("Ingrese el primer número: "))
        num2 = float(input("Ingrese el segundo número: "))
        operacion = input("Ingrese la operación (+, -, *, /): ").strip()
        resultado = calculadora(num1, num2, operacion)
        print(f"Resultado: {resultado}")
        if "Error" in resultado or "no válida" in resultado:
            registrar_historial(f"Comando calculadora falló: {resultado}", cmd, guardar_historial, cargar_historial, rol)
        else:
            registrar_historial(f"Comando calculadora ejecutado: {resultado}", cmd, guardar_historial, cargar_historial, rol)
    ## except captura errores de tipo ValueError, que pueden ocurrir si el usuario ingresa algo que no se puede convertir a float
    except ValueError:
        print("Entrada no válida. Por favor ingrese números enteros o decimales.")
        registrar_historial("Comando calculadora falló: entrada no válida", cmd, guardar_historial, cargar_historial, rol)

def cmd_historial(cmd: str, cargar_historial, eliminar_todo_historial, guardar_historial, rol: str) -> None:
    """Muestra subcomandos del historial: ver todo, eliminar todo o buscar por palabra clave. Delega el procesamiento a gestionar_historial()."""
    print("Comando para ver todo el historial 'historial all'")
    print("Comando para eliminar todo el historial 'historial clear'")
    print("Comando Buscar en el historial 'historial'")
    sub_cmd = input("Ingrese el comando de historial: ").strip().lower()
    if sub_cmd == "historial all":
        print(gestionar_historial("all", cargar_historial()))
    elif sub_cmd == "historial clear":
        eliminar_todo_historial()
        print(gestionar_historial("clear", []))
    elif sub_cmd == "historial":
        busqueda = input("Ingresa la palabra clave a buscar: ").strip().lower()
        resultado = gestionar_historial(busqueda, cargar_historial())
        print(resultado)
        if "No encontré" not in resultado:
            registrar_historial(f"Comando historial ejecutado: búsqueda '{busqueda}' con resultados", cmd, guardar_historial, cargar_historial, rol)
        else:
            registrar_historial(f"Comando historial ejecutado: búsqueda '{busqueda}' sin resultados", cmd, guardar_historial, cargar_historial, rol)
    else:
        print("Comando de historial no válido.")

def buscar_en_historial(historial: MemoriaAgente, busqueda: str) -> MemoriaAgente:
    """Busca entradas en el historial que contengan la palabra clave."""
    resultados = []
    for entrada in historial:
        descripcion = str(entrada.get("descripcion", "")).lower()
        palabras_descripcion = descripcion.split()
        # Uso `in` para saber si la palabra clave está dentro del texto de la descripción, y `split()` me ayuda a separar la descripción en palabras para recorrerla de forma más clara.
        if busqueda in descripcion or any(
            busqueda in palabra for palabra in palabras_descripcion
        ):
            resultados.append(entrada)
    return resultados

def gestionar_historial(accion: str, memoria: MemoriaAgente) -> str:
    """Procesa una acción sobre el historial y retorna el resultado como texto formateado.
    Acciones: 'all' (todo el historial), 'clear' (confirmación de borrado), o cualquier otra cadena como palabra clave de búsqueda.
    No usa print() ni input() — es una función pura de procesamiento de datos."""
    def _formatear_entradas(entradas: MemoriaAgente, titulo: str) -> str:
        lineas = [f"\n{titulo}", "=" * 70]
        for i, entrada in enumerate(entradas, start=1):
            lineas.append(f"Registro {i}")
            lineas.append(f"  Fecha       : {entrada.get('timestamp', 'sin fecha')}")
            lineas.append(f"  Rol         : {entrada.get('rol', 'sin rol')}")
            lineas.append(f"  Comando     : {entrada.get('cmd', 'sin cmd')}")
            lineas.append(f"  Descripcion : {entrada.get('descripcion', '')}")
            if i < len(entradas):
                lineas.append("-" * 70)
        return "\n".join(lineas)

    if accion == "all":
        if not memoria:
            return "[PseudoAgente] No hay historial disponible."
        return _formatear_entradas(memoria, "Historial completo")
    elif accion == "clear":
        return "Historial eliminado."
    else:
        ## Cualquier otra cadena se trata como palabra clave de búsqueda
        resultados = buscar_en_historial(memoria, accion)
        if resultados:
            return (
                _formatear_entradas(resultados, f"Resultados para '{accion}'")
                + f"\n\n[PseudoAgente] Se encontraron {len(resultados)} coincidencias."
            )
        return f"[PseudoAgente] No encontré registros que coincidan con '{accion}'."

def cmd_permisos(rol: str, cargar_usuarios: Callable, actualizar_usuario: Callable, cargar_historial: Callable[[], MemoriaAgente], guardar_historial: Callable[[MemoriaAgente], None], cmd: str) -> None:
    usuario_actualizar = input("Ingrese el nombre de usuario al que desea dar permisos: ").strip()
    for usuario in cargar_usuarios():
        if usuario["usuario"] == usuario_actualizar:
            usuario["rol"] = "admin"
            actualizar_usuario(usuario)
            print(f"Permisos otorgados a {usuario_actualizar}.")
            registrar_historial(f"Comando permisos ejecutado: permisos otorgados a {usuario_actualizar}", cmd, guardar_historial, cargar_historial, rol)
            break
    else:
        print("Usuario no encontrado.")
        registrar_historial("Comando permisos falló: usuario no encontrado", cmd, guardar_historial, cargar_historial, rol)

def cmd_fecha_hoy(rol: str, cmd: str, guardar_historial: Callable[[MemoriaAgente], None], cargar_historial: Callable[[], MemoriaAgente]) -> None:
    """Muestra la fecha actual. Lanza PermissionError si el rol no es administrador."""
    if rol != "admin":
        ## raise interrumpe la ejecución lanzando una excepción, no devuelve un valor. PermissionError es la excepción nativa de Python.
        raise PermissionError("Privilegios insuficientes")
    fecha = datetime.now().strftime("%Y-%m-%d") ## strftime formatea la fecha según el patrón: año-mes-día
    print(f"La fecha de hoy es: {fecha}")
    registrar_historial(f"Comando fecha_hoy ejecutado: {fecha}", cmd, guardar_historial, cargar_historial, rol)

def contador_palabra() -> str:
    """Solicita una palabra al usuario, delega el conteo a contar_letras() e imprime el resultado."""
    pal = input("Ingrese una palabra: ").strip().lower()
    print(contar_letras(pal))
    return pal

def responde_pong():
    print("pong~")

def terminar_sesion():
    return False

## Callable es un tipo cualquiera de objeto que se puede llamar como una función
def pseudo_agente(
    usuario: Usuario,
    rol: str,
    cargar_usuarios: Callable,
    actualizar_usuario: Callable,
    eliminar_usuario: Callable,
    cargar_historial: Callable[[], MemoriaAgente],
    eliminar_todo_historial: Callable,
    guardar_historial: Callable[[MemoriaAgente], None],
) -> None:
    """Loop principal del PseudoAgente."""

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
            registrar_historial("Se ha solicitado terminar la sesión.", cmd, guardar_historial, cargar_historial, rol)
            sistema_activo = terminar_sesion()
        elif cmd == "ping":
            #Comando de respuesta
            responde_pong()
            registrar_historial("Comando ping ejecutado", cmd, guardar_historial, cargar_historial, rol)
        elif cmd == "contar":
            #Comando para contar vocales, consonantes y letras de una palabra ingresada por el usuario.
            pal = contador_palabra()
            registrar_historial(f"Comando contar ejecutado: {pal}", cmd, guardar_historial, cargar_historial, rol)
        elif cmd == "validar_contraseña":
            #Comando para ayudar a crear contraseñas seguras
            cmd_validar_contrasena(usuario.usuario, cmd, guardar_historial, cargar_historial, rol)
        elif cmd == "calculadora":
            #Comando para realizar operaciones matemáticas básicas
            cmd_calculadora(cmd, guardar_historial, cargar_historial, rol)
        elif cmd == "historial":
            #Comando para manejar el historial
            cmd_historial(cmd, cargar_historial, eliminar_todo_historial, guardar_historial, rol)
        elif cmd in ["permisos", "eliminar"] and rol != "admin":
            print(ACCESO_DENEGADO)
        elif cmd == "permisos" and rol == "admin":
            cmd_permisos(rol, cargar_usuarios, actualizar_usuario, cargar_historial, guardar_historial, cmd)
        elif cmd == "fecha_hoy":
            ## try/except en el bucle principal: atrapa el PermissionError que lanza cmd_fecha_hoy si el rol no es admin
            try:
                cmd_fecha_hoy(rol, cmd, guardar_historial, cargar_historial)
            except PermissionError as e:
                ## e contiene el mensaje "Privilegios insuficientes" que definimos en el raise
                print(f"[Acceso Denegado] {e}")
        elif cmd == "eliminar" and rol == "admin":
            usuario_eliminar = input("Ingrese el nombre de usuario que desea eliminar: ").strip()
            eliminar_usuario(usuario_eliminar)
            print(f"Usuario {usuario_eliminar} eliminado.")
            registrar_historial(f"Comando eliminar ejecutado: {usuario_eliminar} eliminado", cmd, guardar_historial, cargar_historial, rol)
        else:
            print("Comando desconocido, intente de nuevo.")
            registrar_historial(f"Comando desconocido ejecutado: {cmd}", cmd, guardar_historial, cargar_historial, rol)
