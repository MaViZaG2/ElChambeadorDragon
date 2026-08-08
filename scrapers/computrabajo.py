"""scrapers/computrabajo.py"""

from urllib.parse import quote_plus, urljoin
from config import PAIS
from models import Oferta
from scrapers.base import BaseScraper
from utils.text import limpiar, limpiar_empresa, limpiar_ubicacion, limpiar_url, inferir_modalidad


class ComputrabajoScraper(BaseScraper):
    NOMBRE = "Computrabajo"

    def __init__(self, pais: str = PAIS):
        self.BASE = f"https://{pais.lower()}.computrabajo.com"

    def _construir_url(self, query: str, pagina: int) -> str:
        slug = quote_plus(query.lower())
        return f"{self.BASE}/trabajo-de-{slug}?p={pagina}"

    def _obtener_cards(self, soup) -> list:
        cards = soup.select("article.box_offer")
        return cards or soup.select("div.js-offer-item, div[data-qa='job-card']")

    def _parsear_card(self, card) -> Oferta | None:
        puesto_tag = card.select_one("h2.fs18 a, .js-o-link, a[data-qa='job-title']")
        if not puesto_tag:
            return None
        puesto = limpiar(puesto_tag.get_text())
        href = puesto_tag.get("href", "")
        url_oferta = limpiar_url(href if href.startswith("http") else urljoin(self.BASE, href))
        empresa_tag = card.select_one("a.fc_base.t_ellipsis, p.fs16, a[data-qa='company-name']")
        empresa = limpiar_empresa(empresa_tag.get_text() if empresa_tag else None)
        loc_tag = card.select_one("p.fs13.fc_base.mt5, span.fc_base.t_ellipsis, span[data-qa='job-location']")
        ubicacion = limpiar_ubicacion(loc_tag.get_text() if loc_tag else None)
        badges = [b.get_text(strip=True) for b in card.select("span.tag")]
        texto = card.get_text(" ", strip=True)
        modalidad = inferir_modalidad(" ".join(badges) if badges else texto)
        return Oferta(puesto=puesto, empresa=empresa, modalidad=modalidad,
                      ubicacion=ubicacion, url=url_oferta, fuente=self.NOMBRE)
