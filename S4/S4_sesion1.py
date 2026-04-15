import datetime
from unittest import result

#Día 1: POO in a nutshell: 
## Clases: Para instanciar/crear de objetos
## Objetos: Representaciones a partir de una clase

## clase Carro (Huella) -> carro_1, carro_2

## Constructor: __init__
## self, siempre va con el constructor, self.attribute después. Es un tema entender el propósito de self
### En resumen: self funciona como un indicador de sitio, para saber a donde debes ir cuando utilizas las 
# funciones de una clase o accedes a los atributos
## No existen modificadores de acceso (public/private/protected) pero 
# existe el "_" para hacer ._attribute: Uso interno

#TO - DO: Construir una clase PseudoAgente
##Atributos de entrada: nombre
##Atributos adicionales: tokens, historial_chat
###Métodos/Funciones
#registrar_log()
#gestionar_historial()

type Historial = dict[str, str]

class PseudoAgente:
    #Constructor
    def __init__(self, nombre: str = "Athena"):
        self.nombre = nombre
        self.tokens = 100
        self.historial_chat: list[Historial] = [] 
    
    #Funciones
    def registrar_log(self, comando: str, rol:str, mensaje:str):
        d_log: Historial = {"timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "cmd": comando,
                "rol": rol,
                "descripcion": mensaje}
        
        self.historial_chat.append(d_log)
    
    def gestionar_historial(self, op: str, rol:str):
        self.tokens -= 30
        if op == "all":
            mensaje = f"[PseudoAgente] Se mostró el historial actual hasta las {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
            self.registrar_log("historial "+op, rol, mensaje)
            return self.historial_chat

        if op == "clear":
            mensaje = f"[PseudoAgente] Se borró el historial actual a las {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} " 
            self.registrar_log("historial "+op, rol, mensaje)
            self.historial_chat.clear()
            return self.historial_chat
      

def login(user: str, passwrd: str) -> dict[str]:
    if user == "admin" and passwrd == "admin123":
        return {
            "rol": user,
            "access": True,
            "descripcion": "[Sistema] Acceso concedido. Privilegios de Administrador activados.",
        }

    if user == "invitado" and passwrd == "1234":
        return {
            "rol": user,
            "access": True,
            "descripcion": "[Sistema] Acceso concedido. Modo Invitado.",
        }

intentos = 0
rol_actual = ""
tiene_acceso = False

while intentos < 3 and not tiene_acceso:
    usuario = input("Usuario: ").strip().lower()
    password = input("Contraseña: ").strip()

    login_attempt = login(usuario, password)
    rol_actual = login_attempt["rol"]
    tiene_acceso = login_attempt["access"]

    if not tiene_acceso:
        intentos += 1
        print(f"[Error] Credenciales incorrectas. Te quedan {3 - intentos} intentos.")
    else:
        print(login_attempt["descripcion"])


## Pseudoagente
if tiene_acceso:    
    historial_chat: list[Historial] = [] 
    #{'timestamp': '2026-03-18 13:50:51', 'cmd': 'ping', 'rol': 'invitado', 'descripcion': 'Se ha enviado un ping y de respuesta se devolvió un pong.'}, {'timestamp': '2026-03-18 13:50:56', 'cmd': 'fecha_hoy', 'rol': 'invitado', 'descripcion': '[Acceso Denegado] Este comando requiere privilegios de administrador.'}, {'timestamp': '2026-03-18 13:51:02', 'cmd': 'dormir', 'rol': 'invitado', 'descripcion': 'Comando no existe. Intente de nuevo'}, {'timestamp': '2026-03-18 13:51:07', 'cmd': 'salir', 'rol': 'invitado', 'descripcion': 'Se ha solicitado terminar la sesión.'}
    pseudo_activo = True
    mensaje = ""

    mi_agente: PseudoAgente = PseudoAgente("Zeus")
    print(mi_agente)
    while pseudo_activo:
        print(f"[{mi_agente.nombre}] Tokens disponibles: {mi_agente.tokens}")
        if mi_agente.tokens <=0:
            print(f"[{mi_agente.nombre}] Tokens insuficientes para continuar. Apagando...")
            break

        cmd = input(f"\n{usuario}@PseudoAgente>: ").strip().lower()

        if cmd == "salir":
            print("[PseudoAgente] Apagando sistemas...")
            mi_agente.registrar_log(cmd, rol_actual, "Se ha solicitado terminar la sesión.")
            pseudo_activo = False
        
        elif cmd == "ping":
            print("pong~")
            mi_agente.tokens -= 10
            mi_agente.registrar_log(cmd, rol_actual, "Se ha enviado un ping y de respuesta se devolvió un pong.")
   
        
        elif cmd.startswith("hist"):
            if " " in cmd:
                sing = cmd.split(" ")[-1]
                resultado = mi_agente.gestionar_historial(sing, rol_actual)
                print(resultado)

            else:
                found = []
                word = input("Ingresa la palabra clave a buscar: ").lower()
                for i, elem in enumerate(historial_chat):
                    if(word in elem["descripcion"]):
                        found.append(elem)
                        #found.append(historial_chat[i])
                mensaje = f" [PseudoAgente] Total de concidencias: {len(found)}"
                print(mensaje)
                if len(found) > 0:                    
                    for i, elem in enumerate(found):
                        print(f"{i+1} >>> {elem}")
                else:
                    print("[PseudoAgente] No encontré registros que coincidan con esa palabra.")

        else:
            mensaje = " [PseudoAgente] Comando no existe. Intente de nuevo"
            print(mensaje)

        

else:
    print("Acceso denegado.")