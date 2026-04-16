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
            energia INTEGER,
            experiencia INTEGER DEFAULT 0
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
            recompensa INTEGER DEFAULT 10,
            prioridad TEXT DEFAULT 'media',
            created_at TEXT,
            updated_at TEXT
        )
    """)
    # Cache de CVEs: evita consultar la NVD/GitHub en cada petición.
    # cpe_consultado agrupa los resultados por componente del stack.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache_cves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cve_id TEXT NOT NULL,
            cpe_consultado TEXT NOT NULL,
            descripcion TEXT,
            severidad TEXT,
            score REAL DEFAULT 0.0,
            fuente TEXT NOT NULL,
            consultado_en TEXT NOT NULL
        )
    """)

    # ── Migraciones: añadir columnas a tablas existentes ──
    for col, ddl in [
        ("experiencia", "ALTER TABLE agentes ADD COLUMN experiencia INTEGER DEFAULT 0"),
        ("recompensa", "ALTER TABLE misiones ADD COLUMN recompensa INTEGER DEFAULT 10"),
    ]:
        try:
            cursor.execute(ddl)
        except sqlite3.OperationalError:
            pass  # la columna ya existe

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
    cursor.execute("SELECT nombre, rol, energia, experiencia FROM agentes WHERE nombre = ?", (nombre,))
    fila = cursor.fetchone()
    conn.close()
    if fila is None:
        return None
    return {"nombre": fila[0], "rol": fila[1], "energia": fila[2], "experiencia": fila[3] or 0}


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


def actualizar_agente(nombre: str, rol: str | None = None, energia: int | None = None) -> str:
    """Actualiza el rol y/o energía de un agente. Retorna mensaje de éxito o error."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM agentes WHERE nombre = ?", (nombre,))
    if cursor.fetchone() is None:
        conn.close()
        return f"[DB] Error: Agente '{nombre}' no encontrado."
    campos = []
    valores = []
    if rol is not None:
        campos.append("rol = ?")
        valores.append(rol)
    if energia is not None:
        campos.append("energia = ?")
        valores.append(energia)
    if not campos:
        conn.close()
        return "[DB] Error: Nada que actualizar."
    valores.append(nombre)
    cursor.execute(f"UPDATE agentes SET {', '.join(campos)} WHERE nombre = ?", valores)
    conn.commit()
    conn.close()
    return f"[DB] Agente '{nombre}' actualizado."


def listar_agentes() -> list[dict]:
    """Retorna una lista con todos los agentes registrados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, rol, energia, experiencia FROM agentes")
    filas = cursor.fetchall()
    conn.close()
    return [{"nombre": f[0], "rol": f[1], "energia": f[2], "experiencia": f[3] or 0} for f in filas]


def sumar_experiencia_agente(nombre: str, puntos: int) -> None:
    """Suma puntos de experiencia a un agente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE agentes SET experiencia = COALESCE(experiencia, 0) + ? WHERE nombre = ?",
        (puntos, nombre),
    )
    conn.commit()
    conn.close()


def misiones_activas_agente(nombre: str) -> list[dict]:
    """Retorna misiones pendientes o en_curso de un agente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, titulo, estado FROM misiones WHERE agente_asignado = ? AND estado IN ('pendiente', 'en_curso')",
        (nombre,),
    )
    filas = cursor.fetchall()
    conn.close()
    return [{"id": f[0], "titulo": f[1], "estado": f[2]} for f in filas]


def eliminar_agente(nombre: str) -> str:
    """Elimina un agente si no tiene misiones activas (pendiente/en_curso)."""
    activas = misiones_activas_agente(nombre)
    if activas:
        titulos = ", ".join(m["titulo"] for m in activas)
        return f"[DB] Error: '{nombre}' tiene misiones activas: {titulos}"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM agentes WHERE nombre = ?", (nombre,))
    if cursor.fetchone() is None:
        conn.close()
        return f"[DB] Error: Agente '{nombre}' no encontrado."
    cursor.execute("DELETE FROM mensajes WHERE remitente = ? OR destinatario = ?", (nombre, nombre))
    cursor.execute("DELETE FROM misiones WHERE agente_asignado = ?", (nombre,))
    cursor.execute("DELETE FROM agentes WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()
    return f"[DB] Agente '{nombre}' eliminado."


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
    recompensa: int = 10,
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
        "INSERT INTO misiones (titulo, descripcion, agente_asignado, estado, energia_requerida, recompensa, prioridad, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (titulo, descripcion, agente_asignado, "pendiente", energia_requerida, recompensa, prioridad, ahora, ahora),
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
        "SELECT id, titulo, descripcion, agente_asignado, estado, energia_requerida, recompensa, prioridad, created_at, updated_at FROM misiones WHERE id = ?",
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
        "recompensa": fila[6] or 10,
        "prioridad": fila[7],
        "created_at": fila[8],
        "updated_at": fila[9],
    }


def buscar_misiones_agente(nombre_agente: str) -> list[dict]:
    """Lista todas las misiones asignadas a un agente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, titulo, descripcion, agente_asignado, estado, energia_requerida, recompensa, prioridad, created_at, updated_at FROM misiones WHERE agente_asignado = ? ORDER BY created_at",
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
            "recompensa": f[6] or 10,
            "prioridad": f[7],
            "created_at": f[8],
            "updated_at": f[9],
        }
        for f in filas
    ]


def completar_mision(mision_id: int) -> bool:
    """Marca una misión como completada en la DB. Retorna True si se actualizó."""
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


# -----------------------------------------------------------#
## Cache de CVEs (Agente Smit — seguridad)
# -----------------------------------------------------------#
def guardar_cves_cache(cves: list[dict], cpe: str, fuente: str) -> None:
    """Persiste una lista de CVEs en cache para un CPE dado."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ahora = datetime.datetime.now().isoformat()
    for cve in cves:
        cursor.execute(
            "INSERT INTO cache_cves (cve_id, cpe_consultado, descripcion, severidad, score, fuente, consultado_en) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (cve["id"], cpe, cve.get("descripcion", ""), cve.get("severidad", "N/A"), cve.get("score", 0.0), fuente, ahora),
        )
    conn.commit()
    conn.close()


def obtener_cves_cache(cpe: str, ttl_segundos: int) -> list[dict] | None:
    """Retorna CVEs cacheados si no han expirado. None si hay que refrescar."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT consultado_en FROM cache_cves WHERE cpe_consultado = ? ORDER BY consultado_en DESC LIMIT 1",
        (cpe,),
    )
    fila = cursor.fetchone()
    if fila is None:
        conn.close()
        return None

    ultimo = datetime.datetime.fromisoformat(fila[0])
    if (datetime.datetime.now() - ultimo).total_seconds() > ttl_segundos:
        # Cache expirado — limpiar
        cursor.execute("DELETE FROM cache_cves WHERE cpe_consultado = ?", (cpe,))
        conn.commit()
        conn.close()
        return None

    cursor.execute(
        "SELECT cve_id, descripcion, severidad, score, fuente FROM cache_cves WHERE cpe_consultado = ? ORDER BY score DESC",
        (cpe,),
    )
    filas = cursor.fetchall()
    conn.close()
    return [
        {"id": f[0], "descripcion": f[1], "severidad": f[2], "score": f[3], "fuente": f[4]}
        for f in filas
    ]


def limpiar_cache_cves() -> int:
    """Elimina todo el cache de CVEs. Retorna filas eliminadas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cache_cves")
    conn.commit()
    eliminadas = cursor.rowcount
    conn.close()
    return eliminadas
