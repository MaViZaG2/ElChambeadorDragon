"""exporters/txt.py — Exporta ofertas a TXT en el Escritorio del usuario."""

import os
import sys
from datetime import datetime
from pathlib import Path

from models import Oferta


def _escritorio() -> Path:
    """Detecta la ruta del Escritorio en Windows, macOS y Linux."""
    home = Path.home()

    # Windows
    if sys.platform == "win32":
        escritorio = home / "Desktop"
        if not escritorio.exists():
            # Soporte para OneDrive
            escritorio = home / "OneDrive" / "Escritorio"
        if not escritorio.exists():
            escritorio = home / "OneDrive" / "Desktop"
        if not escritorio.exists():
            escritorio = home / "Escritorio"
        return escritorio

    # macOS
    if sys.platform == "darwin":
        return home / "Desktop"

    # Linux — intenta leer xdg-user-dirs
    xdg = home / ".config" / "user-dirs.dirs"
    if xdg.exists():
        for line in xdg.read_text(encoding="utf-8").splitlines():
            if line.startswith("XDG_DESKTOP_DIR"):
                _, _, ruta = line.partition("=")
                ruta = ruta.strip().strip('"').replace("$HOME", str(home))
                return Path(ruta)

    return home / "Desktop"


def guardar_en_escritorio(ofertas: list[Oferta], query: str) -> Path:
    """
    Guarda las ofertas en un TXT en el Escritorio.
    Retorna la ruta completa del archivo generado.
    """
    escritorio = _escritorio()
    escritorio.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = query.replace(" ", "_")[:30]
    nombre = f"chambeador_{slug}_{ts}.txt"
    ruta = escritorio / nombre

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("=" * 52 + "\n")
        f.write("   EL CHAMBEADOR DRAGON — Resultados\n")
        f.write(f"   Búsqueda: {query}\n")
        f.write(f"   Fecha:    {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write(f"   Total:    {len(ofertas)} ofertas\n")
        f.write("=" * 52 + "\n\n")

        for o in ofertas:
            f.write(f"Puesto   : {o.puesto}\n")
            f.write(f"Empresa  : {o.empresa}\n")
            f.write(f"Modalidad: {o.modalidad}\n")
            f.write(f"Ubicación: {o.ubicacion}\n")
            f.write(f"Fuente   : {o.fuente}\n")
            f.write(f"URL      :\n{o.url}\n")
            f.write("-" * 40 + "\n\n")

    return ruta
