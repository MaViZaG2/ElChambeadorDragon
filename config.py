"""config.py — Configuración central de ElChambeadorDragon."""

import os
import logging
from pathlib import Path

# ── Carpeta raíz del proyecto ─────────────────
BASE_DIR = Path(__file__).parent

# ── Carga .env manual (sin dependencia extra) ─
_ENV = BASE_DIR / ".env"
if _ENV.exists():
    for _line in _ENV.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# ── HTTP ──────────────────────────────────────
HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}
TIMEOUT: int = 15
DELAY_MIN: float = float(os.getenv("DELAY_MIN", "2.0"))
DELAY_MAX: float = float(os.getenv("DELAY_MAX", "4.5"))
MAX_REINTENTOS: int = int(os.getenv("MAX_REINTENTOS", "3"))

# ── País (Computrabajo) ───────────────────────
PAIS: str = os.getenv("PAIS", "pe")

# ── Concurrencia ─────────────────────────────
MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "3"))

# ── Logging ───────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,       # silencioso por defecto en la terminal del usuario
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
