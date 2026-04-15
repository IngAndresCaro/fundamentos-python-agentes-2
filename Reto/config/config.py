"""
config.py — Carga centralizada de variables de entorno.

Lee config/.env una única vez y expone las variables como constantes del módulo.
Ningún otro archivo necesita llamar a load_dotenv() ni a os.getenv() directamente.
"""

import os

from dotenv import load_dotenv

# Cargar .env relativo a la carpeta config/
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=_ENV_PATH)

AGENCIA_API_KEY: str = os.getenv("AGENCIA_API_KEY", "")
EXTERNAL_API_URL: str = os.getenv("EXTERNAL_API_URL", "https://uselessfacts.jsph.pl/api/v2/facts/random")
