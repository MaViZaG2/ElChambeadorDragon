"""
╔══════════════════════════════════════════════════════════════╗
║                    EL CHAMBEADOR DRAGON                      ║
║        Encuentra trabajo de lo que busques usando esta       ║
║        herramienta de scraping fácil de usar y vuélvete      ║
║                   el chambeador dragon                       ║
╚══════════════════════════════════════════════════════════════╝

USO:
    python main.py

DEPENDENCIAS:
    pip install requests beautifulsoup4 lxml
"""

import sys
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

import config  # noqa — inicializa logging
from exporters import guardar_en_escritorio
from models import Oferta
from scrapers import (
    ComputrabajoScraper,
    BumeranScraper,
    IndeedScraper,
    GetOnBoardScraper,
    LinkedInScraper,
)
from scrapers.base import BaseScraper


class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    VERDE  = "\033[92m"
    ROJO   = "\033[91m"
    AMARILLO = "\033[93m"
    CIAN   = "\033[96m"
    GRIS   = "\033[90m"
    MAGENTA = "\033[95m"


def habilitar_colores_windows():
    """En Windows, habilita secuencias ANSI en la consola."""
    if sys.platform == "win32":
        os.system("")   # truco: fuerza el modo VT100 en cmd/powershell


DRAGON = r"""
   /\   /\
  /  \_/  \
 /         \
/CHAMBEADOR \
\___________/
"""

BANNER = f"""
{C.AMARILLO}{C.BOLD}
╔════════════════════════════════════════════════════╗
║            EL CHAMBEADOR DRAGON                 ║
║      Encuentra chamba rápido y sin estrés         ║
╚════════════════════════════════════════════════════╝
{C.RESET}
"""

SUBTITULO = (
    f"\n{C.CIAN}  Encuentra trabajo de lo que busques usando esta herramienta\n"
    f"  de scraping fácil de usar y vuélvete el chambeador dragon.{C.RESET}\n"
)

DESPEDIDA = (
    f"\n{C.AMARILLO}{'─'*56}{C.RESET}\n"
    f"{C.BOLD}  Gracias por usarme, sigue a mi creador en sus redes\n"
    f"  para más ayuda y que te vaya bien en tu postulación.{C.RESET}\n"
    f"{C.AMARILLO}{'─'*56}{C.RESET}\n"
)

PLATAFORMAS: dict[str, tuple[str, type[BaseScraper]]] = {
    "1": ("Computrabajo  (pe.computrabajo.com)",  ComputrabajoScraper),
    "2": ("Bumeran       (bumeran.com.pe)",        BumeranScraper),
    "3": ("Indeed        (pe.indeed.com)",          IndeedScraper),
    "4": ("Get on Board  (getonbrd.com)",           GetOnBoardScraper),
    "5": ("LinkedIn      (linkedin.com/jobs)",      LinkedInScraper),
    "6": ("Todas las plataformas",                  None),
}


def limpiar_pantalla():
    os.system("cls" if sys.platform == "win32" else "clear")


def separador():
    print(f"{C.GRIS}{'─'*56}{C.RESET}")


def pedir_opcion(opciones_validas: set[str], prompt: str) -> str:
    while True:
        valor = input(f"\n{C.BOLD}{prompt}{C.RESET} ").strip()
        if valor in opciones_validas:
            return valor
        print(f"  {C.ROJO}⚠  Opción inválida. Elige: {', '.join(sorted(opciones_validas))}{C.RESET}")


def animacion_buscando(texto: str = "Buscando chambazo"):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    for i in range(20):
        print(f"\r  {C.CIAN}{frames[i % len(frames)]}  {texto}...{C.RESET}", end="", flush=True)
        time.sleep(0.1)
    print()


def _buscar_en(scraper: BaseScraper, query: str, paginas: int) -> list[Oferta]:
    session = requests.Session()
    try:
        return scraper.buscar(query, session, paginas=paginas)
    except Exception:
        return []
    finally:
        session.close()


def buscar(
    scrapers: list[BaseScraper],
    query: str,
    paginas: int = 2,
    limite: int | None = None
) -> list[Oferta]:

    todas: list[Oferta] = []

    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as pool:
        futuros = {
            pool.submit(_buscar_en, s, query, paginas): s.NOMBRE
            for s in scrapers
        }

        for futuro in as_completed(futuros):
            try:
                todas.extend(futuro.result())
            except Exception:
                pass

    vistas = set()
    unicas: list[Oferta] = []

    for oferta in todas:
        if oferta.url not in vistas:
            vistas.add(oferta.url)
            unicas.append(oferta)

    if limite:
        unicas = unicas[:limite]

    return unicas


def mostrar_banner():
    limpiar_pantalla()
    print(BANNER)
    print(SUBTITULO)


def pantalla_bienvenida() -> bool:
    """Retorna True si el usuario quiere continuar."""
    separador()
    print(f"\n  {C.BOLD}[1]{C.RESET} Presiona 1 para continuar")
    print(f"  {C.BOLD}[0]{C.RESET} Presiona 0 para cancelar")
    opcion = pedir_opcion({"1", "0"}, "→")
    return opcion == "1"


def elegir_plataformas() -> list[BaseScraper]:
    print(f"\n{C.AMARILLO}{C.BOLD}  ¿En qué plataforma buscamos?{C.RESET}")
    separador()
    for k, (nombre, _) in PLATAFORMAS.items():
        print(f"  {C.BOLD}[{k}]{C.RESET}  {nombre}")
    separador()

    opcion = pedir_opcion(set(PLATAFORMAS.keys()), "→ Elige una opción:")

    if opcion == "6":
        return [cls() for _, cls in PLATAFORMAS.values() if cls is not None]
    else:
        _, cls = PLATAFORMAS[opcion]
        return [cls()]


def pedir_puesto() -> str:
    print(f"\n{C.VERDE}{C.BOLD}Escribe el puesto que busques:{C.RESET}")
    while True:
        puesto = input(f"  {C.BOLD}→{C.RESET} ").strip()
        if puesto:
            return puesto
        print(f"  {C.ROJO}El puesto no puede estar vacío.{C.RESET}")

def pedir_limite() -> int | None:
    print(f"\n{C.AMARILLO}{C.BOLD}  ¿Limitar cantidad de trabajos?{C.RESET}")
    print(f"  {C.BOLD}[1]{C.RESET} Sí, elegir máximo")
    print(f"  {C.BOLD}[2]{C.RESET} No, sin límite")

    opcion = pedir_opcion({"1", "2"}, "→")

    if opcion == "2":
        return None

    while True:
        valor = input("\n  Máximo de trabajos: ").strip()

        if valor.isdigit() and int(valor) > 0:
            return int(valor)

        print(f"  {C.ROJO}Ingresa un número válido.{C.RESET}")


def mostrar_preview(ofertas: list[Oferta]):
    print(f"\n{C.VERDE}    {len(ofertas)} oferta(s) encontradas:{C.RESET}\n")
    separador()
    for o in ofertas[:3]:
        print(f"  {C.BOLD}{o.puesto}{C.RESET} @ {o.empresa}")
        print(f"  {C.GRIS}{o.modalidad} | {o.ubicacion} | {o.fuente}{C.RESET}")
        separador()
    if len(ofertas) > 3:
        print(f"  {C.GRIS}... y {len(ofertas) - 3} más en el archivo.{C.RESET}")


def seguir_buscando() -> bool:
    print(f"\n{C.AMARILLO}{C.BOLD}  ¿Seguir buscando chamba?{C.RESET}")
    print(f"  {C.BOLD}[1]{C.RESET} Sí, buscar más")
    print(f"  {C.BOLD}[0]{C.RESET} No, ya conseguí mi chambazo ")
    opcion = pedir_opcion({"1", "0"}, "→")
    return opcion == "1"


def main():
    habilitar_colores_windows()

    while True:
        mostrar_banner()

        if not pantalla_bienvenida():
            print(DESPEDIDA)
            sys.exit(0)

        scrapers = elegir_plataformas()

        puesto = pedir_puesto()
        limite = pedir_limite()

        nombres = ", ".join(s.NOMBRE for s in scrapers)
        print(f"\n{C.CIAN}  Buscando «{puesto}» en: {nombres}{C.RESET}")
        animacion_buscando()

        ofertas = buscar(scrapers, puesto, paginas=2)

        if not ofertas:
            print(f"\n  {C.ROJO}  No encontré resultados. Prueba con otro término.{C.RESET}")
        else:
            mostrar_preview(ofertas)

            print(f"\n  {C.CIAN}  Guardando en tu Escritorio...{C.RESET}")
            ruta = guardar_en_escritorio(ofertas, puesto)
            print(f"\n  {C.VERDE}{C.BOLD}  Archivo creado:{C.RESET}")
            print(f"  {C.VERDE}{ruta}{C.RESET}")

        if not seguir_buscando():
            print(DESPEDIDA)
            sys.exit(0)


if __name__ == "__main__":
    main()

def pedir_limite() -> int | None:
    print(f"\n{C.AMARILLO}{C.BOLD}  ¿Limitar cantidad de trabajos?{C.RESET}")
    print(f"  {C.BOLD}[1]{C.RESET} Sí, elegir máximo")
    print(f"  {C.BOLD}[2]{C.RESET} No, sin límite")

    opcion = pedir_opcion({"1", "2"}, "→")

    if opcion == "2":
        return None

    while True:
        valor = input(f"\n  Máximo de trabajos: ").strip()

        if valor.isdigit() and int(valor) > 0:
            return int(valor)

        print(f"  {C.ROJO}⚠  Ingresa un número válido.{C.RESET}")


