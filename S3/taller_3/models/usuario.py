# `dataclass` es un decorador que genera automáticamente métodos especiales
# como __init__, __repr__ y __eq__ a partir de los atributos que declaras en la clase,
# evitando escribir ese código repetitivo a mano.
#
# `asdict` es una función que convierte una instancia de dataclass en un diccionario
# ordinario de Python, útil para serializar el objeto y guardarlo en JSON.
from dataclasses import dataclass, asdict


@dataclass
class Usuario:
    id: int
    usuario: str
    contraseña: str
    rol: str
    bloqueado: bool

    @classmethod
    def from_dict(cls, data: dict) -> "Usuario":
        """Crea un Usuario desde un diccionario (ej. cargado del JSON)."""
        return cls(
            id=data["id"],
            usuario=data["usuario"],
            contraseña=data["contraseña"],
            rol=data["rol"],
            bloqueado=data["bloqueado"],
        )

    def to_dict(self) -> dict:
        """Convierte el Usuario a diccionario para guardar en JSON."""
        return asdict(self)
