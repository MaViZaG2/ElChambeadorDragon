"""scrapers/getonboard.py"""

from urllib.parse import quote_plus, urljoin
from models import Oferta
from scrapers.base import BaseScraper
from utils.text import limpiar, limpiar_empresa, limpiar_ubicacion, limpiar_url, inferir_modalidad


class GetOnBoardScraper(BaseScraper):
    NOMBRE = "Get on Board"
    BASE = "https://www.getonbrd.com"

    def _construir_url(self, query: str, pagina: int) -> str:
        return f"{self.BASE}/jobs?q={quote_plus(query)}&page={pagina}"

    def _obtener_cards(self, soup) -> list:
        cards = soup.select("li.gb-results-list__item")
        return cards or soup.select("a[class*='JobCard'], div[data-testid='job-card']")

    def _parsear_card(self, card) -> Oferta | None:
        puesto_tag = card.select_one("h2, h3, [class*='title'], [class*='Title']")
        if not puesto_tag:
            return None
        puesto = limpiar(puesto_tag.get_text())
        if card.name == "a" and card.has_attr("href"):
            href = card["href"]
        else:
            link = card.select_one("a")
            href = link["href"] if link and link.has_attr("href") else ""
        url_oferta = limpiar_url(href if href.startswith("http") else urljoin(self.BASE, href))
        empresa_tag = card.select_one("[class*='company'], [class*='Company'], [class*='organization']")
        empresa = limpiar_empresa(empresa_tag.get_text() if empresa_tag else None)
        loc_tag = card.select_one("[class*='location'], [class*='Location'], [class*='place']")
        ubicacion = limpiar_ubicacion(loc_tag.get_text() if loc_tag else "Latinoamérica")
        texto = card.get_text(" ", strip=True)
        modalidad = inferir_modalidad(texto)
        if modalidad == "No especificado" and "remote" in texto.lower():
            modalidad = "Remoto"
        return Oferta(puesto=puesto, empresa=empresa, modalidad=modalidad,
                      ubicacion=ubicacion, url=url_oferta, fuente=self.NOMBRE)
