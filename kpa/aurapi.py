# Copyright (C) 2025 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

import subprocess as sb
import requests

BASE_URL = "https://aur.archlinux.org/rpc/?v=5&type="


def existe(paquete) -> bool:
    url = f"{BASE_URL}info&arg[]={paquete}"
    try:
        respuesta = requests.get(url, timeout=10).json()
    except requests.exceptions.Timeout:
        print(f"Timeout verificando si el paquete {paquete} existe en AUR...")
        return False
    return respuesta["resultcount"] > 0


def oficial_en_repos(paquete) -> bool:
    try:
        sb.run(["pacman", "-Si", paquete], check=True, shell=False, capture_output=True)
    except sb.CalledProcessError:
        return False  # Si se produce este error es porque el paquete no existe
    return True


def verificar_paquetes(paquetes: list) -> list:
    """Retorna una lista de paquetes que existen en el AUR y no en los repositorios
    oficiales a partir de una lista con paquetes de origenes desconocidos."""
    paquetes_aur: list = []
    for paquete in paquetes:
        if existe(paquete) and not oficial_en_repos(paquete):
            paquetes_aur.append(paquete)
    return paquetes_aur
