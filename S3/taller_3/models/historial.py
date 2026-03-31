# dataclass: decorador que genera automáticamente __init__, __repr__ y __eq__
#            a partir de los atributos definidos en la clase, evitando código repetitivo.
# asdict:    función que convierte una instancia de dataclass en un diccionario de Python,
#            útil para serializar el objeto a JSON antes de guardarlo en el archivo.
from dataclasses import dataclass, asdict


@dataclass
class HistorialChat:
    timestamp: str
    rol: str
    cmd: str
    descripcion: str

    @classmethod
    def from_dict(cls, data: dict) -> "HistorialChat":
        """Crea un HistorialChat desde un diccionario (ej. cargado del JSON)."""
        return cls(
            timestamp=data["timestamp"],
            rol=data["rol"],
            cmd=data["cmd"],
            descripcion=data["descripcion"],
        )

    def to_dict(self) -> dict:
        """Convierte el HistorialChat a diccionario para guardar en JSON."""
        return asdict(self)
