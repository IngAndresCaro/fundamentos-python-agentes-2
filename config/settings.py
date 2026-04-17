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

# ── APIs externas por rol de agente ──
API_ADVICE_URL: str = os.getenv("API_ADVICE_URL", "https://api.adviceslip.com/advice")
API_JOKE_URL: str = os.getenv("API_JOKE_URL", "https://v2.jokeapi.dev/joke/Programming?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single")
API_WIKIPEDIA_URL: str = os.getenv("API_WIKIPEDIA_URL", "https://en.wikipedia.org/api/rest_v1/feed/featured")

# ── APIs de seguridad ──
SECURITY_API_URL: str = os.getenv("SECURITY_API_URL", "https://services.nvd.nist.gov/rest/json/cves/2.0")
GITHUB_ADVISORY_URL: str = os.getenv("GITHUB_ADVISORY_URL", "https://api.github.com/advisories")
NVD_API_KEY: str = os.getenv("NVD_API_KEY", "")

# ── Timeouts (segundos) ──
TIMEOUT_EXTERNO: int = 3        # Máximo para llamadas a APIs externas
TIMEOUT_CLIENTE: int = 5        # Máximo para el script cliente.py
CACHE_CVE_TTL: int = 3600       # Cache de CVEs: 1 hora (segundos)
