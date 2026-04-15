"""
db.py — Funciones de persistencia SQLite.

Adaptado de S5/S5_sesion_1.py para el reto de consolidación.
Aquí NO hay FastAPI — solo queries SQL y manejo de conexiones.
Todas las queries usan parámetros ? para prevenir SQL injection.
"""

import datetime
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agentes.db")
USER_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user.db")


# -----------------------------------------------------------#
## Tablas: agentes, mensajes, misiones
# -----------------------------------------------------------#
def crear_tablas() -> None:
    """Crea las tablas agentes, mensajes y misiones si no existen."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agentes (
            nombre TEXT PRIMARY KEY,
            rol TEXT,
            energia INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente TEXT,
            destinatario TEXT,
            contenido TEXT,
            timestamp TEXT
        )
    """)
    # Decisión de ingeniería: se agregan prioridad y updated_at
    # - prioridad: permite ordenar misiones por urgencia (baja, media, alta, critica)
    # - updated_at: registra cuándo cambió el estado por última vez
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            agente_asignado TEXT,
            estado TEXT DEFAULT 'pendiente',
            energia_requerida INTEGER,
            prioridad TEXT DEFAULT 'media',
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# -----------------------------------------------------------#
## Agentes
# -----------------------------------------------------------#
def registrar_agente(nombre: str, rol: str, energia: int) -> str:
    """Registra un agente en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO agentes (nombre, rol, energia) VALUES (?, ?, ?)",
            (nombre, rol, energia),
        )
        conn.commit()
        resultado = f"[DB] Agente '{nombre}' registrado con éxito."
    except sqlite3.IntegrityError:
        resultado = f"[DB] Error: El agente '{nombre}' ya existe."
    finally:
        conn.close()
    return resultado


def despertar_agente(nombre: str) -> dict | None:
    """Busca un agente por nombre. Retorna dict o None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, rol, energia FROM agentes WHERE nombre = ?", (nombre,))
    fila = cursor.fetchone()
    conn.close()
    if fila is None:
        return None
    return {"nombre": fila[0], "rol": fila[1], "energia": fila[2]}


def actualizar_energia_agente(nombre: str, nueva_energia: int) -> None:
    """Actualiza la energía de un agente en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE agentes SET energia = ? WHERE nombre = ?",
        (nueva_energia, nombre),
    )
    conn.commit()
    conn.close()


def listar_agentes() -> list[dict]:
    """Retorna una lista con todos los agentes registrados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, rol, energia FROM agentes")
    filas = cursor.fetchall()
    conn.close()
    return [{"nombre": f[0], "rol": f[1], "energia": f[2]} for f in filas]


# -----------------------------------------------------------#
## Mensajes
# -----------------------------------------------------------#
def enviar_mensaje(remitente: str, destinatario: str, contenido: str) -> str:
    """Inserta un mensaje en la tabla mensajes con timestamp automático."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM agentes WHERE nombre = ?", (destinatario,))
    if cursor.fetchone() is None:
        conn.close()
        return f"[DB] Error: El agente destinatario '{destinatario}' no existe."
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO mensajes (remitente, destinatario, contenido, timestamp) VALUES (?, ?, ?, ?)",
        (remitente, destinatario, contenido, timestamp),
    )
    conn.commit()
    conn.close()
    return f"[DB] Mensaje de '{remitente}' a '{destinatario}' enviado."


def leer_mensajes(nombre_agente: str) -> list[dict]:
    """Lee todos los mensajes dirigidos a un agente, ordenados por timestamp."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT remitente, destinatario, contenido, timestamp FROM mensajes WHERE destinatario = ? ORDER BY timestamp",
        (nombre_agente,),
    )
    filas = cursor.fetchall()
    conn.close()
    return [
        {"remitente": f[0], "destinatario": f[1], "contenido": f[2], "timestamp": f[3]}
        for f in filas
    ]


# -----------------------------------------------------------#
## Misiones
# -----------------------------------------------------------#
def crear_mision(
    titulo: str,
    descripcion: str,
    agente_asignado: str,
    energia_requerida: int,
    prioridad: str = "media",
) -> int | None:
    """Crea una misión. Retorna el id de la misión creada, o None si el agente no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Verificar que el agente asignado existe
    cursor.execute("SELECT 1 FROM agentes WHERE nombre = ?", (agente_asignado,))
    if cursor.fetchone() is None:
        conn.close()
        return None
    ahora = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO misiones (titulo, descripcion, agente_asignado, estado, energia_requerida, prioridad, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (titulo, descripcion, agente_asignado, "pendiente", energia_requerida, prioridad, ahora, ahora),
    )
    conn.commit()
    mision_id = cursor.lastrowid
    conn.close()
    return mision_id


def obtener_mision(mision_id: int) -> dict | None:
    """Busca una misión por id. Retorna dict o None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, titulo, descripcion, agente_asignado, estado, energia_requerida, prioridad, created_at, updated_at FROM misiones WHERE id = ?",
        (mision_id,),
    )
    fila = cursor.fetchone()
    conn.close()
    if fila is None:
        return None
    return {
        "id": fila[0],
        "titulo": fila[1],
        "descripcion": fila[2],
        "agente_asignado": fila[3],
        "estado": fila[4],
        "energia_requerida": fila[5],
        "prioridad": fila[6],
        "created_at": fila[7],
        "updated_at": fila[8],
    }


def buscar_misiones_agente(nombre_agente: str) -> list[dict]:
    """Lista todas las misiones asignadas a un agente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, titulo, descripcion, agente_asignado, estado, energia_requerida, prioridad, created_at, updated_at FROM misiones WHERE agente_asignado = ? ORDER BY created_at",
        (nombre_agente,),
    )
    filas = cursor.fetchall()
    conn.close()
    return [
        {
            "id": f[0],
            "titulo": f[1],
            "descripcion": f[2],
            "agente_asignado": f[3],
            "estado": f[4],
            "energia_requerida": f[5],
            "prioridad": f[6],
            "created_at": f[7],
            "updated_at": f[8],
        }
        for f in filas
    ]


def completar_mision(mision_id: int) -> bool:
    """Marca una misión como completada. Retorna True si se actualizó."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ahora = datetime.datetime.now().isoformat()
    cursor.execute(
        "UPDATE misiones SET estado = ?, updated_at = ? WHERE id = ? AND estado != ?",
        ("completada", ahora, mision_id, "completada"),
    )
    conn.commit()
    actualizado = cursor.rowcount > 0
    conn.close()
    return actualizado


# -----------------------------------------------------------#
## Autenticación de usuarios (user.db)
# -----------------------------------------------------------#
def autenticar_usuario(user: str, password: str) -> dict:
    """Valida credenciales contra la tabla 'usuarios' en user.db."""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rol FROM usuarios WHERE user = ? AND password = ?",
            (user, password),
        )
        fila = cursor.fetchone()
        conn.close()
    except sqlite3.Error:
        return {
            "rol": "",
            "access": False,
            "descripcion": "[Sistema] Error al conectar con la base de datos.",
        }

    if fila:
        rol = fila[0]
        if rol == "admin":
            descripcion = "[Sistema] Acceso concedido. Privilegios de Administrador activados."
        else:
            descripcion = f"[Sistema] Acceso concedido. Modo {rol.capitalize()}."
        return {"rol": rol, "access": True, "descripcion": descripcion}

    return {
        "rol": "",
        "access": False,
        "descripcion": "[Sistema] Credenciales incorrectas.",
    }
