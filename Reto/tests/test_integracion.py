"""
Tests de integración — La Agencia de Agentes.

Cubre:
 - Reto Eutagógico (a): POST /api/misiones sin API key → rechazado.
 - Reto Eutagógico (b): GET /api/briefing/{nombre} → estructura correcta con mock.
 - Flujo completo R5: crear agente → crear misión → completar → briefing → mensaje.

Ejecutar:
    cd Reto
    python -m pytest pruebas/ -v
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
import requests as req_lib
from fastapi.testclient import TestClient

from config.config import AGENCIA_API_KEY
from main import app

API_KEY = AGENCIA_API_KEY
HEADERS = {"X-API-KEY": API_KEY}


@pytest.fixture()
def client():
    """TestClient de FastAPI — no necesita servidor corriendo."""
    with TestClient(app, follow_redirects=False) as c:
        yield c


def _nombre_unico() -> str:
    """Genera un nombre de agente único para evitar colisiones entre tests."""
    return f"Test_{uuid.uuid4().hex[:8]}"


# ─────────────────────────────────────────────────────────────
# Eutagógico (a): POST /api/misiones sin API key → rechazado
# ─────────────────────────────────────────────────────────────
class TestProteccionApiKey:
    """Endpoints protegidos rechazan peticiones sin API key válida."""

    def test_crear_mision_sin_key_rechaza(self, client):
        """POST /api/misiones sin X-API-KEY no devuelve 2xx."""
        r = client.post(
            "/api/misiones",
            json={
                "titulo": "Mision sin llave",
                "descripcion": "No debería crearse",
                "agente_asignado": "Nadie",
                "energia_requerida": 10,
            },
        )
        assert r.status_code not in (200, 201), f"Debería rechazar, pero dio {r.status_code}"

    def test_crear_agente_sin_key_rechaza(self, client):
        """POST /api/agentes sin X-API-KEY no devuelve 2xx."""
        r = client.post(
            "/api/agentes",
            json={"nombre": "Fantasma", "rol": "explorador", "energia": 100},
        )
        assert r.status_code not in (200, 201)

    def test_completar_mision_sin_key_rechaza(self, client):
        """POST /api/misiones/999/completar sin X-API-KEY no devuelve 2xx."""
        r = client.post("/api/misiones/999/completar")
        assert r.status_code not in (200, 201)

    def test_enviar_mensaje_sin_key_rechaza(self, client):
        """POST /api/mensajes sin X-API-KEY no devuelve 2xx."""
        r = client.post(
            "/api/mensajes",
            json={"remitente": "A", "destinatario": "B", "contenido": "Hola"},
        )
        assert r.status_code not in (200, 201)


# ─────────────────────────────────────────────────────────────
# Eutagógico (b): GET /briefing/{nombre} → estructura esperada
# ─────────────────────────────────────────────────────────────
class TestBriefing:
    """El briefing devuelve datos locales + inteligencia externa mockeada."""

    def test_briefing_estructura_con_mock(self, client):
        """GET /api/briefing/{nombre} retorna la estructura completa con dato externo."""
        nombre = _nombre_unico()
        # Crear agente de prueba
        client.post(
            "/api/agentes",
            json={"nombre": nombre, "rol": "espía", "energia": 90},
            headers=HEADERS,
        )

        # Mock de la API externa (requests se importa como http_client en briefing_service)
        # espía → Advice Slip con formato {"slip": {"advice": "..."}}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"slip": {"advice": "Dato secreto mockeado"}}

        with patch("service.briefing_service.http_client.get", return_value=mock_resp):
            r = client.get(f"/api/briefing/{nombre}", headers=HEADERS)

        assert r.status_code == 200
        data = r.json()

        # Verificar estructura
        assert "agente" in data
        assert data["agente"]["nombre"] == nombre
        assert data["agente"]["rol"] == "espía"
        assert data["agente"]["energia"] == 90

        assert "resumen_misiones" in data
        assert "total" in data["resumen_misiones"]
        assert "pendientes" in data["resumen_misiones"]
        assert "completadas" in data["resumen_misiones"]

        assert "inteligencia_externa" in data
        assert data["inteligencia_externa"] == "💡 Dato secreto mockeado"
        assert data["tono"] == "empático"

        assert "fuente_externa" in data

    def test_briefing_fallback_cuando_api_falla(self, client):
        """Si la API externa falla, el briefing responde con fallback."""
        nombre = _nombre_unico()
        client.post(
            "/api/agentes",
            json={"nombre": nombre, "rol": "analista", "energia": 100},
            headers=HEADERS,
        )

        with patch("service.briefing_service.http_client.get", side_effect=req_lib.ConnectionError("Connection refused")):
            r = client.get(f"/api/briefing/{nombre}", headers=HEADERS)

        assert r.status_code == 200
        data = r.json()
        assert "[Fallback]" in data["inteligencia_externa"]

    def test_briefing_agente_inexistente_404(self, client):
        """Briefing de un agente que no existe devuelve 404."""
        r = client.get("/api/briefing/NoExisto_XYZ", headers=HEADERS)
        assert r.status_code == 404


# ─────────────────────────────────────────────────────────────
# Flujo completo R5 (equivalente a cliente.py como test)
# ─────────────────────────────────────────────────────────────
class TestFlujoCompletoR5:
    """Recorre el guion completo de R5 en un solo test."""

    def test_circuito_completo(self, client):
        """Crear agente → crear misión → completar → briefing → mensaje."""
        agente = _nombre_unico()
        receptor = _nombre_unico()

        # Paso 1: servidor responde
        r = client.get("/api/agentes", headers=HEADERS)
        assert r.status_code == 200

        # Paso 2: crear agentes
        r = client.post(
            "/api/agentes",
            json={"nombre": agente, "rol": "explorador", "energia": 100},
            headers=HEADERS,
        )
        assert r.status_code == 201

        r = client.post(
            "/api/agentes",
            json={"nombre": receptor, "rol": "admin", "energia": 100},
            headers=HEADERS,
        )
        assert r.status_code == 201

        # Paso 3: crear misión
        r = client.post(
            "/api/misiones",
            json={
                "titulo": "Misión de prueba",
                "descripcion": "Test automatizado",
                "agente_asignado": agente,
                "energia_requerida": 25,
            },
            headers=HEADERS,
        )
        assert r.status_code == 201
        mision_id = r.json()["id"]

        # Paso 4: completar misión
        r = client.post(f"/api/misiones/{mision_id}/completar", headers=HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert data["energia_restante"] == 75  # 100 - 25 (PseudoAgente paga completo)
        assert data["tipo_agente"] == "PseudoAgente"

        # Paso 5: briefing (con mock de API externa)
        # explorador → JokeAPI con formato {"joke": "..."}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"joke": "Hecho curioso de prueba"}

        with patch("service.briefing_service.http_client.get", return_value=mock_resp):
            r = client.get(f"/api/briefing/{agente}", headers=HEADERS)

        assert r.status_code == 200
        briefing = r.json()
        assert briefing["agente"]["energia"] == 75
        assert briefing["resumen_misiones"]["completadas"] == 1

        # Paso 6: enviar mensaje y leer bandeja
        r = client.post(
            "/api/mensajes",
            json={
                "remitente": agente,
                "destinatario": receptor,
                "contenido": "Misión finalizada.",
            },
            headers=HEADERS,
        )
        assert r.status_code == 201

        r = client.get(f"/api/mensajes/{receptor}", headers=HEADERS)
        assert r.status_code == 200
        mensajes = r.json()
        assert any(m["remitente"] == agente for m in mensajes)

    def test_admin_paga_mitad_energia(self, client):
        """R2 — AgenteAdmin descuenta solo 50% de energía en misión."""
        admin = _nombre_unico()

        client.post(
            "/api/agentes",
            json={"nombre": admin, "rol": "admin", "energia": 100},
            headers=HEADERS,
        )

        r = client.post(
            "/api/misiones",
            json={
                "titulo": "Misión admin",
                "descripcion": "Test polimorfismo",
                "agente_asignado": admin,
                "energia_requerida": 40,
            },
            headers=HEADERS,
        )
        mision_id = r.json()["id"]

        r = client.post(f"/api/misiones/{mision_id}/completar", headers=HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert data["energia_restante"] == 80  # 100 - (40 // 2) = 80
        assert data["tipo_agente"] == "AgenteAdmin"
