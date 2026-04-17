"""
sbom.py — Software Bill of Materials (SBOM) de La Agencia.

Inventario de todos los componentes del stack con su CPE 2.3 (Common Platform
Enumeration).  El Agente Smit usa estos CPEs para consultar la NVD y GitHub
Advisory en busca de vulnerabilidades que afecten nuestro aplicativo.

Para agregar una dependencia nueva:
  1. Busca su CPE en https://nvd.nist.gov/products/cpe/search
  2. Añade un dict con componente, version, cpe y ecosystem.

Formato CPE 2.3:
  cpe:2.3:a:<vendor>:<product>:<version>:*:*:*:*:*:*:*
             │        │         │
             │        producto   versión (* = cualquiera)
             fabricante
"""

SBOM_STACK: list[dict] = [
    {
        "componente": "Python",
        "version": "3.12",
        "cpe": "cpe:2.3:a:python:python:3.12:*:*:*:*:*:*:*",
        "ecosystem": "pip",
    },
    {
        "componente": "FastAPI",
        "version": "0.115",
        "cpe": "cpe:2.3:a:tiangolo:fastapi:*:*:*:*:*:*:*:*",
        "ecosystem": "pip",
    },
    {
        "componente": "Uvicorn",
        "version": "0.34",
        "cpe": "cpe:2.3:a:encode:uvicorn:*:*:*:*:*:*:*:*",
        "ecosystem": "pip",
    },
    {
        "componente": "Starlette",
        "version": "0.45",
        "cpe": "cpe:2.3:a:encode:starlette:*:*:*:*:*:*:*:*",
        "ecosystem": "pip",
    },
    {
        "componente": "Pydantic",
        "version": "2.x",
        "cpe": "cpe:2.3:a:pydantic:pydantic:*:*:*:*:*:*:*:*",
        "ecosystem": "pip",
    },
    {
        "componente": "Requests",
        "version": "2.x",
        "cpe": "cpe:2.3:a:python-requests:requests:*:*:*:*:*:*:*:*",
        "ecosystem": "pip",
    },
    {
        "componente": "SQLite",
        "version": "3.x",
        "cpe": "cpe:2.3:a:sqlite:sqlite:*:*:*:*:*:*:*:*",
        "ecosystem": "system",
    },
]
