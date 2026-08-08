"""utils/http.py — Cliente HTTP con reintentos y backoff exponencial."""

import logging
import random
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import HEADERS, TIMEOUT, DELAY_MIN, DELAY_MAX, MAX_REINTENTOS

log = logging.getLogger(__name__)


def _esperar(intento: int) -> None:
    base = random.uniform(DELAY_MIN, DELAY_MAX)
    espera = base * (2 ** intento) + random.uniform(0, 1)
    time.sleep(espera)


def get_html(
    url: str,
    session: requests.Session,
    reintentos: int = MAX_REINTENTOS,
    extra_headers: dict | None = None,
) -> Optional[BeautifulSoup]:
    headers = {**HEADERS, **(extra_headers or {})}

    for intento in range(reintentos):
        _esperar(intento)
        try:
            resp = session.get(url, headers=headers, timeout=TIMEOUT)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 10))
                log.warning(f"429 Rate limit. Esperando {retry_after}s...")
                time.sleep(retry_after + random.uniform(1, 3))
                continue

            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")

        except requests.exceptions.Timeout:
            log.warning(f"⚠ No se pudo acceder a la plataforma (intento {intento+1})")
        except requests.exceptions.ConnectionError as e:
            log.warning(f"Conexión fallida (intento {intento+1}): {e}")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "?"
            log.warning(f"⚠ No se pudo acceder a la plataforma (intento {intento+1})")
            if status in (403, 404):
                return None

    log.error(" La plataforma bloqueó la búsqueda o no respondió.")
    return None
