"""scrapers/indeed.py"""

from urllib.parse import quote_plus, urljoin
from models import Oferta
from scrapers.base import BaseScraper
from utils.text import limpiar, limpiar_empresa, limpiar_ubicacion, limpiar_url, inferir_modalidad


class IndeedScraper(BaseScraper):
    NOMBRE = "Indeed"
    BASE = "https://pe.indeed.com"

    def _construir_url(self, query: str, pagina: int) -> str:
        q = quote_plus(query)
        start = (pagina - 1) * 10
        return f"{self.BASE}/jobs?q={q}&l=Peru&start={start}"

    def _obtener_cards(self, soup) -> list:
        cards = soup.select("div.job_seen_beacon, div[data-testid='slot-item']")
        return cards or soup.select("div.jobsearch-SerpJobCard")

    def _parsear_card(self, card) -> Oferta | None:
        puesto_tag = card.select_one("h2.jobTitle a, a[data-testid='job-title'], h2 a")
        if not puesto_tag:
            return None
        puesto = limpiar(puesto_tag.get_text())
        href = puesto_tag.get("href", "")
        url_oferta = limpiar_url(href if href.startswith("http") else urljoin(self.BASE, href))
        empresa_tag = card.select_one("[data-testid='company-name'], span.companyName, .companyInfo span")
        empresa = limpiar_empresa(empresa_tag.get_text() if empresa_tag else None)
        loc_tag = card.select_one("[data-testid='text-location'], div.companyLocation, .location")
        ubicacion = limpiar_ubicacion(loc_tag.get_text() if loc_tag else None)
        modalidad = inferir_modalidad(card.get_text(" ", strip=True))
        return Oferta(puesto=puesto, empresa=empresa, modalidad=modalidad,
                      ubicacion=ubicacion, url=url_oferta, fuente=self.NOMBRE)
