# Copyright (C) 2025-2026 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

from kpa.colorprints import yellow, yellow_input, red
from pathlib import Path
from pkgbuild_parser import Parser
from shutil import rmtree
from os.path import join
from os import listdir
import sys


def confirm(text: str, question: str) -> bool:
    correct_input: bool = False
    yellow(text)
    while not correct_input:
        answer = yellow_input(f"{question} (S/N)")
        answer_fix = answer.strip().lower()
        if answer_fix in ('s', 'n'):
            correct_input = True
        else:
            yellow("Opción incorrecta, intente de nuevo...")
    
    if answer_fix == "s":
        return True
    return False


def encontrar_archivos(ruta: str, extension: str) -> list:
    return list(Path(ruta).glob(f"*{extension}"))


def visor(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        print(archivo.read())


def no_aur(ruta):
    red("ERROR: Intentaste clonar un repositorio no existente del AUR.")
    rmtree(ruta)
    sys.exit(1)


def eula_detectado(ruta: str):
    nombres_comunes = ["eula.txt", "EULA.txt", "LICENSE.eula", "license.eula", "license.html", "LICENSE.html", "eula_text.html", "EULA_TEXT.html"]
    licenses_comunes = ["Proprietary", "proprietary", "Custom", "custom"]
    for archivo in listdir(ruta):
        if archivo in nombres_comunes:
            return True
    pkg_licenses = Parser(join(ruta, "PKGBUILD")).get_license()
    for license_comun in licenses_comunes:
        for pkg_license in pkg_licenses:
            if license_comun in pkg_license:
                return True
    return False
