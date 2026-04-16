"""
config.py — Carga centralizada de variables de entorno y constantes del proyecto.

Lee config/.env una única vez y expone las variables como constantes del módulo.
Ningún otro archivo necesita llamar a load_dotenv() ni a os.getenv() directamente.
"""

import os

from dotenv import load_dotenv

# Cargar .env relativo a la carpeta config/
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=_ENV_PATH)

# ── Secretos (desde .env) ──
AGENCIA_API_KEY: str = os.getenv("AGENCIA_API_KEY", "")
EXTERNAL_API_URL: str = os.getenv("EXTERNAL_API_URL", "https://uselessfacts.jsph.pl/api/v2/facts/random")

# ── Timeouts (segundos) ──
TIMEOUT_EXTERNO: int = 3        # Máximo para llamadas a APIs externas
TIMEOUT_CLIENTE: int = 5        # Máximo para el script cliente.py
