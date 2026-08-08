"""utils/text.py — Limpieza y normalización de texto scrapeado."""

import re
import unicodedata


def limpiar(texto: str | None) -> str:
    if not texto:
        return "N/D"
    texto = re.sub(r"[\t\r\n]+", " ", texto)
    texto = re.sub(r" {2,}", " ", texto)
    texto = texto.strip()
    return texto or "N/D"


def normalizar(texto: str) -> str:
    return unicodedata.normalize("NFC", texto)


def limpiar_empresa(texto: str | None) -> str:
    texto = limpiar(texto)
    if texto == "N/D":
        return texto
    texto = normalizar(texto)
    texto = re.sub(r"\s+(S\.?A\.?C?\.?|S\.?R\.?L\.?|E\.?I\.?R\.?L\.?)$", "", texto, flags=re.IGNORECASE)
    return texto.strip() or "N/D"


def limpiar_ubicacion(texto: str | None) -> str:
    texto = limpiar(texto)
    if texto == "N/D":
        return texto
    texto = normalizar(texto)
    texto = re.sub(r"\b\d{4,6}\b", "", texto).strip()
    texto = re.sub(r"[,;|\-]+$", "", texto).strip()
    return texto or "N/D"


def limpiar_url(url: str | None) -> str:
    if not url:
        return "N/D"
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return "N/D"
    url = re.sub(r"[?&](utm_source|utm_medium|utm_campaign|ref|tracking)[^&]*", "", url)
    return url.rstrip("?&")


_REMOTO    = ["remoto", "remote", "teletrabajo", "home office", "trabajo desde casa"]
_HIBRIDO   = ["híbrido", "hibrido", "hybrid", "mixto"]
_PRESENCIAL = ["presencial", "on-site", "on site", "oficina"]


def inferir_modalidad(texto: str) -> str:
    t = texto.lower()
    if any(p in t for p in _REMOTO):
        return "Remoto"
    if any(p in t for p in _HIBRIDO):
        return "Híbrido"
    if any(p in t for p in _PRESENCIAL):
        return "Presencial"
    return "No especificado"
