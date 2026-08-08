"""scrapers/linkedin.py — LinkedIn jobs (versión pública, sin login)."""

from urllib.parse import quote_plus, urljoin
from models import Oferta
from scrapers.base import BaseScraper
from utils.text import limpiar, limpiar_empresa, limpiar_ubicacion, limpiar_url, inferir_modalidad


class LinkedInScraper(BaseScraper):
    NOMBRE = "LinkedIn"
    BASE = "https://www.linkedin.com"

    def _construir_url(self, query: str, pagina: int) -> str:
        q = quote_plus(query)
        start = (pagina - 1) * 25
        return (
            f"{self.BASE}/jobs/search/"
            f"?keywords={q}&location=Peru&start={start}"
        )

    def _obtener_cards(self, soup) -> list:
        cards = soup.select("div.base-card, li.jobs-search__results-list > div")
        return cards or soup.select("div[data-entity-urn]")

    def _parsear_card(self, card) -> Oferta | None:
        puesto_tag = card.select_one(
            "h3.base-search-card__title, h3[class*='job-title'], a.base-card__full-link"
        )
        if not puesto_tag:
            return None
        puesto = limpiar(puesto_tag.get_text())

        link_tag = card.select_one("a.base-card__full-link, a[data-tracking-id]")
        href = link_tag["href"] if link_tag and link_tag.has_attr("href") else ""
        url_oferta = limpiar_url(href if href.startswith("http") else urljoin(self.BASE, href))

        empresa_tag = card.select_one(
            "h4.base-search-card__subtitle a, a[class*='company'], [class*='subtitle']"
        )
        empresa = limpiar_empresa(empresa_tag.get_text() if empresa_tag else None)

        loc_tag = card.select_one("span.job-search-card__location, [class*='location']")
        ubicacion = limpiar_ubicacion(loc_tag.get_text() if loc_tag else None)

        modalidad = inferir_modalidad(card.get_text(" ", strip=True))
        return Oferta(puesto=puesto, empresa=empresa, modalidad=modalidad,
                      ubicacion=ubicacion, url=url_oferta, fuente=self.NOMBRE)
