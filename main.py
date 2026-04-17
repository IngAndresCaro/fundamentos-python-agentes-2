import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from config.settings import AGENCIA_API_KEY
from repository.db import crear_tablas
from api.agentes import router as agente_router
from api.briefing import router as briefing_router
from api.auth_routes import router as login_router
from api.misiones import router as mision_router
from templates.dashboard import DASHBOARD_HTML
from core.session import rol_sesion, sesion_valida

# -------------------------------------------------------------------
# Configuración del logger
# INFO para eventos normales del servidor (startup, requests exitosos) esto para tener información
# de lo que se esta utilizando o generando posibles problemas.
# WARNING para situaciones inesperadas pero no fatales donde tenemos que poner atención pero no
# es critico.
# ERROR para fallos que requieren atención y pueden generar daños o caidas del sistema.
# Formato: fecha + nivel + mensaje, suficiente para auditar sin ruido.
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: crea tablas al arrancar."""
    crear_tablas()
    logger.info("Startup — Tablas SQLite verificadas. La Agencia está en línea.")
    yield
    logger.info("Shutdown — La Agencia ha cerrado operaciones.")


app = FastAPI(
    title="La Agencia de Agentes",
    description="API de gestión de agentes, misiones y mensajes.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(login_router)
app.include_router(agente_router)
app.include_router(mision_router)
app.include_router(briefing_router)

# Rutas accesibles sin sesión
_RUTAS_PUBLICAS = {"/login", "/openapi.json"}
# Rutas exclusivas para administradores
_RUTAS_ADMIN = {"/docs", "/redoc"}


@app.middleware("http")
async def verificar_sesion(request: Request, call_next):
    """
    Middleware de autenticación:
    - Rutas públicas (/login): acceso libre.
    - /docs y /redoc: solo rol 'admin'.
    - Resto: cualquier sesión válida.
    Redirige a /login cuando no hay sesión; devuelve 403 si hay sesión pero sin permiso.
    """
    path = request.url.path

    # Permitir rutas públicas sin verificar
    if path in _RUTAS_PUBLICAS or path.startswith("/login"):
        return await call_next(request)

    # Las rutas /api/ pueden autenticarse con API key en vez de sesión
    if path.startswith("/api/"):
        api_key = request.headers.get("X-API-KEY", "")
        if api_key == AGENCIA_API_KEY:
            return await call_next(request)
        # Si no tiene API key, sigue el flujo normal (sesión)

    token = request.cookies.get("session", "")

    if not sesion_valida(token):
        logger.warning("Acceso bloqueado a %s — sin sesión válida", path)
        return RedirectResponse(url="/login", status_code=302)

    # Verificar si la ruta requiere rol admin
    if path in _RUTAS_ADMIN or path.startswith("/docs") or path.startswith("/redoc"):
        if rol_sesion(token) != "admin":
            logger.warning("Acceso denegado a %s — rol insuficiente", path)
            return JSONResponse(
                status_code=403,
                content={"detail": "Acceso restringido a administradores."},
            )

    return await call_next(request)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """Renderiza el dashboard con la oficina animada según el rol del usuario."""
    token = request.cookies.get("session", "")
    rol = rol_sesion(token) or "invitado"
    admin_display = "block" if rol == "admin" else "none"
    logger.info("GET / — dashboard | rol=%s", rol)
    return DASHBOARD_HTML.format(rol=rol, admin_display=admin_display, api_key=AGENCIA_API_KEY)
