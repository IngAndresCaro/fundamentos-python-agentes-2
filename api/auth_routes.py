import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from templates.login import LOGIN_HTML
from repository.db import autenticar_usuario
from core.session import cerrar_sesion, crear_sesion

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Login"])

# -----------------------------------------------------------#
# No se agrega verificación de API Key en el login ya que es el punto de entrada para obtener 
# la API Key, y no tendría sentido requerirla para acceder a la funcionalidad de autenticación.
# Además, el login es una operación que debe estar accesible para que los usuarios puedan
# autenticarse
# -----------------------------------------------------------#
@router.get("/login", response_class=HTMLResponse)
def login_form():
    """Muestra el formulario de login."""
    return LOGIN_HTML.format(mensaje="")

# -----------------------------------------------------------#
# No se agrega verificación deApi Key ya que aun estamos validando al usuarios
# y no tiene sentido aun pedirsela
# -----------------------------------------------------------#
@router.post("/login", response_class=HTMLResponse)
def login_submit(user: str = Form(...), password: str = Form(...)):
    """Valida credenciales. Si son correctas, crea sesión y redirige al inicio."""
    resultado = autenticar_usuario(user, password)

    if resultado["access"]:
        logger.info("Login exitoso | user=%s rol=%s", user, resultado["rol"])
        token = crear_sesion(resultado["rol"])
        response = RedirectResponse(url="/", status_code=302)
        # httponly=True: la cookie no es accesible desde JavaScript
        # samesite="lax": protección básica contra CSRF
        response.set_cookie("session", token, httponly=True, samesite="lax")
        return response

    logger.warning("Login fallido | user=%s", user)
    mensaje = f'<div class="msg err">{resultado["descripcion"]}</div>'
    return LOGIN_HTML.format(mensaje=mensaje)

# -----------------------------------------------------------#
# no se agrega verificación de API key ya que estamos cerrando la sesión actual
# -----------------------------------------------------------#
@router.get("/logout")
def logout(request: Request):
    """Cierra la sesión activa y redirige al login."""
    token = request.cookies.get("session", "")
    cerrar_sesion(token)
    logger.info("Logout | sesión cerrada")
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session")
    return response
