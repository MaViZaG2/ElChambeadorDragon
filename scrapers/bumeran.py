"""scrapers/bumeran.py"""

from urllib.parse import urljoin
from models import Oferta
from scrapers.base import BaseScraper
from utils.text import limpiar, limpiar_empresa, limpiar_ubicacion, limpiar_url, inferir_modalidad


class BumeranScraper(BaseScraper):
    NOMBRE = "Bumeran"
    BASE = "https://www.bumeran.com.pe"

    def _construir_url(self, query: str, pagina: int) -> str:
        slug = query.lower().replace(" ", "-")
        return f"{self.BASE}/empleos-busqueda-{slug}.html?recientes=true&page={pagina}"

    def _obtener_cards(self, soup) -> list:
        cards = soup.select("div[class*='CardAnuncio']")
        return cards or soup.select("li.aviso, article[data-jobid]")

    def _parsear_card(self, card) -> Oferta | None:
        puesto_tag = card.select_one("h2 a, a[class*='title'], [class*='JobTitle']")
        if not puesto_tag:
            return None
        puesto = limpiar(puesto_tag.get_text())
        href = puesto_tag.get("href", "")
        url_oferta = limpiar_url(href if href.startswith("http") else urljoin(self.BASE, href))
        empresa_tag = card.select_one("span[class*='company'], a[class*='company'], [class*='CompanyName']")
        empresa = limpiar_empresa(empresa_tag.get_text() if empresa_tag else None)
        loc_tag = card.select_one("span[class*='location'], span[class*='ubicacion'], [class*='Location']")
        ubicacion = limpiar_ubicacion(loc_tag.get_text() if loc_tag else None)
        modalidad = inferir_modalidad(card.get_text(" ", strip=True))
        return Oferta(puesto=puesto, empresa=empresa, modalidad=modalidad,
                      ubicacion=ubicacion, url=url_oferta, fuente=self.NOMBRE)
