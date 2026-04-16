"""
models/agente.py — Esquemas Pydantic para tipado de requests/responses.

Aquí NO hay lógica de dominio ni SQL.
Solo estructuras que validan la forma de los datos en la API.
Las clases de comportamiento (PseudoAgente, AgenteAdmin) viven en agentes/agente.py.
"""

from pydantic import BaseModel, Field, field_validator


# -----------------------------------------------------------#
## Request Bodies
# -----------------------------------------------------------#

# Valores permitidos para campos de tipo enum
_ESTADOS_MISION = {"pendiente", "en_curso", "completada", "fallida"}
_PRIORIDADES = {"baja", "media", "alta", "critica"}
_ROLES_AGENTE = {"espía", "analista", "guardián", "admin", "explorador"}


class CrearAgenteBody(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    rol: str = Field(..., min_length=1)
    energia: int = Field(default=100, ge=1, le=200)

    @field_validator("rol")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        if v.lower() not in _ROLES_AGENTE:
            raise ValueError(f"Rol inválido '{v}'. Permitidos: {', '.join(sorted(_ROLES_AGENTE))}")
        return v.lower()


class ActualizarAgenteBody(BaseModel):
    rol: str | None = Field(default=None, min_length=1)
    energia: int | None = Field(default=None, ge=1, le=200)

    @field_validator("rol")
    @classmethod
    def rol_valido(cls, v: str | None) -> str | None:
        if v is not None and v.lower() not in _ROLES_AGENTE:
            raise ValueError(f"Rol inválido '{v}'. Permitidos: {', '.join(sorted(_ROLES_AGENTE))}")
        return v.lower() if v else v


class EnviarMensajeBody(BaseModel):
    remitente: str = Field(..., min_length=1)
    destinatario: str = Field(..., min_length=1)
    contenido: str = Field(..., min_length=1, max_length=500)


class CrearMisionBody(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=100)
    descripcion: str = Field(default="")
    agente_asignado: str = Field(..., min_length=1)
    energia_requerida: int = Field(default=20, ge=1)
    recompensa: int = Field(default=10, ge=0)
    prioridad: str = Field(default="media")

    @field_validator("energia_requerida")
    @classmethod
    def energia_positiva(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("energia_requerida debe ser mayor a 0")
        return v

    @field_validator("prioridad")
    @classmethod
    def prioridad_valida(cls, v: str) -> str:
        if v.lower() not in _PRIORIDADES:
            raise ValueError(f"Prioridad inválida '{v}'. Permitidas: {', '.join(sorted(_PRIORIDADES))}")
        return v.lower()
