"""models.py — Modelo de datos Oferta."""

from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class Oferta:
    puesto: str
    empresa: str
    modalidad: str
    ubicacion: str
    url: str
    fuente: str
    fecha_scraping: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    def to_dict(self) -> dict:
        return asdict(self)
