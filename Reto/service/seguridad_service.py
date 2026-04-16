# -----------------------------------------------------------#
# seguridad_service.py — Inteligencia de seguridad (Agente Smit).
#
# Flujo completo:
#   1. SBOM — Inventario de componentes del stack con CPEs.
#   2. Consulta — NVD (NIST) por CPE + GitHub Advisory como complemento.
#   3. Filtrado — CVSS ≥ 7.0 marcan alerta HIGH/CRITICAL.
#   4. Cache — SQLite local evita bombardear la NVD en cada petición.
#   5. Retry — Reintentos suaves ante 503/403 de la NVD.
#   6. Recomendaciones dinámicas según CVEs encontrados.
#   7. Auto-completar — Cierra misiones de seguridad tras el escaneo.
# -----------------------------------------------------------#
import logging
import time

import requests as http_client

from agentes.agente import AgenteAdmin, PseudoAgente
from config.config import (
    CACHE_CVE_TTL,
    GITHUB_ADVISORY_URL,
    NVD_API_KEY,
    SECURITY_API_URL,
    TIMEOUT_EXTERNO,
)
from repository.db import (
    actualizar_energia_agente,
    completar_mision,
    guardar_cves_cache,
    obtener_cves_cache,
)
from repository.sbom import SBOM_STACK

logger = logging.getLogger(__name__)


# ── Palabras clave que activan inteligencia de seguridad ──
KEYWORDS_SEGURIDAD = {
    "seguridad", "security", "inspección", "inspeccionar",
    "vulnerabilidad", "ataque", "protección", "hacking",
    "auditoría", "ciberseguridad", "firewall", "malware",
    "exploit", "pentesting", "amenaza", "threat",
}

# ── Recomendaciones estáticas (fallback) ──
_RECOMENDACIONES_FALLBACK = [
    "Mantener todas las dependencias (FastAPI, Uvicorn, requests) actualizadas.",
    "Verificar que todos los endpoints /api/ exijan X-API-KEY.",
    "Asegurar que las queries SQL usen parámetros (?) para prevenir inyección SQL.",
    "Configurar CORS apropiadamente si la API se expone a navegadores.",
    "Implementar rate limiting para prevenir ataques de fuerza bruta.",
    "Rotar la API key periódicamente y no exponerla en el código fuente.",
]


# -----------------------------------------------------------#
# Helpers — retry, NVD, GitHub Advisory, cache
# -----------------------------------------------------------#
def es_mision_seguridad(mision: dict) -> bool:
    """Detecta si una misión tiene contexto de seguridad por palabras clave."""
    texto = f"{mision.get('titulo', '')} {mision.get('descripcion', '')}".lower()
    return any(kw in texto for kw in KEYWORDS_SEGURIDAD)


def _request_con_retry(url: str, params: dict, headers: dict | None = None, max_reintentos: int = 2) -> dict | None:
    """GET con reintentos suaves ante 503/403/429. Devuelve JSON o None."""
    for intento in range(max_reintentos + 1):
        try:
            resp = http_client.get(url, params=params, headers=headers or {}, timeout=TIMEOUT_EXTERNO)
            if resp.status_code in (503, 403, 429):
                wait = 2 ** intento
                logger.warning("API %s — HTTP %d, reintento %d/%d en %ds", url, resp.status_code, intento + 1, max_reintentos, wait)
                if intento < max_reintentos:
                    time.sleep(wait)
                    continue
                return None
            resp.raise_for_status()
            return resp.json()
        except http_client.Timeout:
            logger.warning("API %s — timeout (intento %d/%d)", url, intento + 1, max_reintentos + 1)
            if intento < max_reintentos:
                time.sleep(1)
                continue
            return None
        except http_client.RequestException as exc:
            logger.warning("API %s — error: %s", url, exc)
            return None
    return None


def _extraer_severidad(cve: dict) -> tuple[str, float]:
    """Extrae severidad y score CVSS de un objeto CVE de la NVD."""
    metrics = cve.get("metrics", {})
    for version_key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if version_key in metrics and metrics[version_key]:
            cvss_data = metrics[version_key][0].get("cvssData", {})
            severity = cvss_data.get("baseSeverity", "N/A")
            score = cvss_data.get("baseScore", 0.0)
            return severity, score
    return "N/A", 0.0


def _consultar_nvd_por_cpe(cpe: str) -> list[dict]:
    """Consulta la NVD API v2.0 usando cpeName. Usa cache si disponible."""
    cached = obtener_cves_cache(cpe, CACHE_CVE_TTL)
    if cached is not None:
        real = [c for c in cached if c["id"] != "_EMPTY_"]
        logger.info("NVD cache hit | cpe=%s cves=%d", cpe, len(real))
        return real

    headers = {}
    if NVD_API_KEY:
        headers["apiKey"] = NVD_API_KEY

    data = _request_con_retry(
        SECURITY_API_URL,
        params={"cpeName": cpe, "resultsPerPage": 5},
        headers=headers,
    )

    if data is None:
        guardar_cves_cache([{"id": "_EMPTY_", "descripcion": "", "severidad": "N/A", "score": 0.0}], cpe, "NVD")
        logger.info("NVD — API no disponible (sentinel cacheado) | cpe=%s", cpe)
        return []

    vulnerabilidades = []
    for item in data.get("vulnerabilities", [])[:5]:
        cve = item.get("cve", {})
        cve_id = cve.get("id", "N/A")
        descriptions = cve.get("descriptions", [])
        desc = next(
            (d["value"] for d in descriptions if d.get("lang") == "en"),
            "Sin descripción disponible",
        )
        severidad, score = _extraer_severidad(cve)
        vulnerabilidades.append({
            "id": cve_id,
            "descripcion": desc[:250],
            "severidad": severidad,
            "score": score,
        })

    if vulnerabilidades:
        guardar_cves_cache(vulnerabilidades, cpe, "NVD")
        logger.info("NVD — %d CVEs cacheados | cpe=%s", len(vulnerabilidades), cpe)
    else:
        guardar_cves_cache([{"id": "_EMPTY_", "descripcion": "", "severidad": "N/A", "score": 0.0}], cpe, "NVD")
        logger.info("NVD — 0 CVEs (sentinel cacheado) | cpe=%s", cpe)

    return vulnerabilidades


def _consultar_github_advisory(ecosystem: str, componente: str) -> list[dict]:
    """Consulta la GitHub Advisory Database como complemento."""
    cached = obtener_cves_cache(f"github:{ecosystem}:{componente}", CACHE_CVE_TTL)
    if cached is not None:
        real = [c for c in cached if c["id"] != "_EMPTY_"]
        logger.info("GitHub Advisory cache hit | %s:%s cves=%d", ecosystem, componente, len(real))
        return real

    data = _request_con_retry(
        GITHUB_ADVISORY_URL,
        params={
            "ecosystem": ecosystem,
            "severity": "high,critical",
            "per_page": 3,
        },
        headers={"Accept": "application/vnd.github+json"},
    )

    if data is None or not isinstance(data, list):
        guardar_cves_cache([{"id": "_EMPTY_", "descripcion": "", "severidad": "N/A", "score": 0.0}], f"github:{ecosystem}:{componente}", "GitHub Advisory")
        logger.info("GitHub Advisory — API no disponible (sentinel) | %s:%s", ecosystem, componente)
        return []

    vulnerabilidades = []
    for advisory in data[:3]:
        ghsa_id = advisory.get("ghsa_id", "N/A")
        cve_id = advisory.get("cve_id") or ghsa_id
        summary = advisory.get("summary", "Sin descripción")
        severity = (advisory.get("severity") or "N/A").upper()
        score = advisory.get("cvss", {}).get("score", 0.0) if advisory.get("cvss") else 0.0
        vulnerabilidades.append({
            "id": cve_id,
            "descripcion": summary[:250],
            "severidad": severity,
            "score": score,
        })

    if vulnerabilidades:
        guardar_cves_cache(vulnerabilidades, f"github:{ecosystem}:{componente}", "GitHub Advisory")
        logger.info("GitHub Advisory — %d advisories | %s:%s", len(vulnerabilidades), ecosystem, componente)
    else:
        guardar_cves_cache([{"id": "_EMPTY_", "descripcion": "", "severidad": "N/A", "score": 0.0}], f"github:{ecosystem}:{componente}", "GitHub Advisory")
        logger.info("GitHub Advisory — 0 advisories (sentinel) | %s:%s", ecosystem, componente)

    return vulnerabilidades


def _generar_recomendaciones(vulnerabilidades: list[dict], alertas: list[dict]) -> list[str]:
    """Genera recomendaciones dinámicas a partir de los CVEs y alertas encontrados."""
    recs: list[str] = []

    if alertas:
        recs.append(
            f"🚨 ALERTA: {len(alertas)} vulnerabilidades con CVSS ≥ 7.0 detectadas. Priorizar revisión inmediata."
        )
        for a in alertas[:3]:
            recs.append(f"   → {a['id']} ({a['componente']}) — Severidad: {a['severidad']} (Score: {a['score']})")

    recs.append("Mantener todas las dependencias (FastAPI, Uvicorn, requests, Pydantic) actualizadas.")
    recs.append("Revisar que todos los endpoints protegidos exijan X-API-KEY.")
    recs.append("Validar que las queries SQL usen parámetros (?) para prevenir inyección SQL.")

    componentes_afectados = {v.get("componente", "").lower() for v in vulnerabilidades}

    if "python" in componentes_afectados:
        recs.append("Verificar versión de Python (3.12+) y aplicar parches de seguridad.")
    if "starlette" in componentes_afectados or "fastapi" in componentes_afectados:
        recs.append("Revisar headers de seguridad del servidor: CORS, CSP, X-Frame-Options, X-Content-Type-Options.")
    if "requests" in componentes_afectados:
        recs.append("Verificar que todas las llamadas HTTP usen verify=True (validación SSL).")
    if "sqlite" in componentes_afectados:
        recs.append("Considerar cifrado de la base de datos (SQLCipher) para datos sensibles.")

    if not vulnerabilidades:
        recs.extend(_RECOMENDACIONES_FALLBACK[3:])

    return recs


# -----------------------------------------------------------#
# Funciones públicas (usadas por briefing_service)
# -----------------------------------------------------------#
def obtener_inteligencia_seguridad() -> dict:
    """Escanea el SBOM completo: NVD por CPE + GitHub Advisory por ecosistema."""
    todas_vulns: list[dict] = []
    componentes_escaneados: list[dict] = []

    for item in SBOM_STACK:
        cpe = item["cpe"]
        componente = item["componente"]
        ecosystem = item["ecosystem"]

        nvd_vulns = _consultar_nvd_por_cpe(cpe)
        for v in nvd_vulns:
            v["componente"] = componente
            v["fuente"] = v.get("fuente", "NVD")

        gh_vulns = []
        if ecosystem == "pip":
            gh_vulns = _consultar_github_advisory(ecosystem, componente.lower())
            for v in gh_vulns:
                v["componente"] = componente
                v["fuente"] = v.get("fuente", "GitHub Advisory")

        total = len(nvd_vulns) + len(gh_vulns)
        componentes_escaneados.append({
            "componente": componente,
            "version": item["version"],
            "cpe": cpe,
            "cves_encontrados": total,
        })

        todas_vulns.extend(nvd_vulns)
        todas_vulns.extend(gh_vulns)

    vistos: set[str] = set()
    vulns_unicas: list[dict] = []
    for v in todas_vulns:
        if v["id"] not in vistos:
            vistos.add(v["id"])
            vulns_unicas.append(v)

    vulns_unicas.sort(key=lambda v: v.get("score", 0.0), reverse=True)
    alertas = [v for v in vulns_unicas if v.get("score", 0.0) >= 7.0]
    recomendaciones = _generar_recomendaciones(vulns_unicas, alertas)

    estado = "activo" if todas_vulns else "fallback"
    fuentes = [SECURITY_API_URL]
    if any(v.get("fuente") == "GitHub Advisory" for v in vulns_unicas):
        fuentes.append(GITHUB_ADVISORY_URL)

    return {
        "sbom": componentes_escaneados,
        "vulnerabilidades_recientes": vulns_unicas[:10],
        "alertas_criticas": alertas[:5],
        "total_vulnerabilidades": len(vulns_unicas),
        "recomendaciones": recomendaciones,
        "fuentes": fuentes,
        "estado": estado,
    }


def auto_completar_misiones_seguridad(
    datos_agente: dict,
    misiones: list[dict],
) -> dict:
    """Auto-completa misiones de seguridad tras escaneo exitoso.

    Usa el polimorfismo de R2 para descontar energía.
    Retorna dict con misiones_auto_completadas, misiones_sin_energia y energía final.
    """
    if datos_agente["rol"] == "admin":
        agente = AgenteAdmin(nombre=datos_agente["nombre"], energia=datos_agente["energia"])
    else:
        agente = PseudoAgente(nombre=datos_agente["nombre"], energia=datos_agente["energia"])

    completadas = []
    sin_energia = []
    for m in misiones:
        if m["estado"] == "completada":
            continue
        msg = agente.consumir_energia(m["energia_requerida"])
        if "insuficiente" in msg.lower():
            sin_energia.append(m["titulo"])
            continue
        actualizar_energia_agente(agente.nombre, agente.tokens)
        completar_mision(m["id"])
        completadas.append(m["titulo"])
        logger.info(
            "Misión auto-completada por Smit | id=%d titulo=%s energia_restante=%d",
            m["id"], m["titulo"], agente.tokens,
        )

    return {
        "misiones_auto_completadas": completadas,
        "misiones_sin_energia": sin_energia,
        "energia_final": agente.tokens,
        "tipo_agente": type(agente).__name__,
    }
