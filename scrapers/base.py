"""scrapers/base.py — Clase abstracta para todos los scrapers."""

import logging
from abc import ABC, abstractmethod

import requests

from models import Oferta
from utils.http import get_html

log = logging.getLogger(__name__)


class BaseScraper(ABC):
    NOMBRE: str = "Plataforma"
    BASE: str = ""

    def buscar(self, query: str, session: requests.Session, paginas: int = 2) -> list[Oferta]:
        ofertas: list[Oferta] = []
        for pagina in range(1, paginas + 1):
            url = self._construir_url(query, pagina)
            soup = get_html(url, session)
            if soup is None:
                continue
            cards = self._obtener_cards(soup)
            if not cards:
                break
            for card in cards:
                try:
                    oferta = self._parsear_card(card)
                    if oferta:
                        ofertas.append(oferta)
                except Exception as e:
                    log.debug(f"[{self.NOMBRE}] Error parseando card: {e}")
        return ofertas

    @abstractmethod
    def _construir_url(self, query: str, pagina: int) -> str: ...

    @abstractmethod
    def _obtener_cards(self, soup) -> list: ...

    @abstractmethod
    def _parsear_card(self, card) -> "Oferta | None": ...
