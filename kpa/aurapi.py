# Copyright (C) 2025-2026 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

import subprocess as sb
import requests

BASE_URL = "https://aur.archlinux.org/rpc/v5/info?arg[]="


def existe(paquete: str) -> bool:
    url: str = f"{BASE_URL}{paquete}"
    try:
        respuesta = requests.get(url, timeout=10).json()
    except requests.exceptions.Timeout:
        print(f"Timeout verificando si el paquete {paquete} existe en AUR...")
        return False
    return respuesta["resultcount"] > 0


def oficial_en_repos(paquete: str) -> bool:
    return sb.run(["pacman", "-Si", paquete], check=False, shell=False,
                  capture_output=True).returncode == 0


def verificar_paquetes(paquetes: list[str]) -> list[str]:
    """Retorna una lista de paquetes que existen en el AUR y no en los repositorios
    oficiales a partir de una lista con paquetes de origenes desconocidos."""
    paquetes_aur: list = []
    for paquete in paquetes:
        if (not oficial_en_repos(paquete)) and existe(paquete):
            paquetes_aur.append(paquete)
    return paquetes_aur


def extra_vals(package: str) -> list[str]:
    url: str = f"{BASE_URL}{package}"
    warnings: list[str] = []

    try:
        request = requests.get(url, timeout=10).json()
    except requests.exceptions.Timeout:
        pass
    else:
        results = request["results"][0]
        if results["Maintainer"] is None:
            warnings.append("- El paquete está huérfano en el AUR.")

        if results["OutOfDate"] is not None:
            warnings.append("- El paquete está marcado como desactualizado en el AUR.")

    return warnings
