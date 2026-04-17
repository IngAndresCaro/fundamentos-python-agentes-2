import secrets

# Almacén en memoria: token -> rol del usuario
_sessions: dict[str, str] = {}


def crear_sesion(rol: str) -> str:
    """Genera un token único, lo registra con el rol del usuario y lo retorna."""
    token = secrets.token_hex(32)
    _sessions[token] = rol
    return token


def sesion_valida(token: str) -> bool:
    """Devuelve True si el token existe en las sesiones activas."""
    return token in _sessions


def rol_sesion(token: str) -> str:
    """Retorna el rol del usuario asociado al token, o cadena vacía si no existe."""
    return _sessions.get(token, "")


def cerrar_sesion(token: str) -> None:
    """Elimina el token de las sesiones activas (logout)."""
    _sessions.pop(token, None)
