# Copyright (C) 2025-2026 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

from pathlib import Path
from shutil import rmtree
from os.path import join, getsize, islink, isdir
from os import listdir, remove, getenv
from subprocess import run, CalledProcessError
import sys

from rich.console import Console
from rich.syntax import Syntax

from pkgbuild_parser import Parser
from kpa.colorprints import yellow, yellow_input, red

console = Console(emoji=False)


def confirm(text: str, question: str, e_mode: bool = False, file_emode: str = "") -> bool:
    correct_input: bool = False
    yellow(text)
    while not correct_input:
        if e_mode:
            answer = yellow_input(f"{question} (S/N/[E]ditar):")
        else:
            answer = yellow_input(f"{question} (S/N):")
        answer_fix = answer.strip().lower()
        if answer_fix in ('s', 'n'):
            correct_input = True
        elif answer_fix == "e" and e_mode:
            try:
                run([getenv("EDITOR"), file_emode], check=True, shell=False)
            except CalledProcessError as e:
                yellow(f"Error al abrir el editor: {e}")
        else:
            yellow("Opción incorrecta, intente de nuevo...")

    if answer_fix == "s":
        return True
    return False


def encontrar_archivos(ruta: str, extension: str) -> list:
    return list(Path(ruta).glob(f"*{extension}"))


def visor(ruta_archivo: str, tema: str):
    console.print(Syntax.from_path(
        ruta_archivo, lexer="bash", line_numbers=True, theme=tema))


def no_aur(ruta: str):
    red("ERROR: Intentaste clonar un repositorio no existente del AUR.")
    rmtree(ruta)
    sys.exit(1)


def eula_detectado(ruta: str) -> bool:
    nombres_comunes: list[str] = ["eula.txt", "EULA.txt", "LICENSE.eula", "license.eula",
                                  "license.html", "LICENSE.html", "eula_text.html",
                                  "EULA_TEXT.html"]
    licenses_comunes: list[str] = [
        "Proprietary", "proprietary", "Custom", "custom"]
    for archivo in listdir(ruta):
        if archivo in nombres_comunes:
            return True
    pkg_licenses: list[str] = Parser(join(ruta, "PKGBUILD")).get_license()
    for license_comun in licenses_comunes:
        for pkg_license in pkg_licenses:
            if license_comun in pkg_license:
                return True
    return False


def clean_cache(path: str):
    try:
        rmtree(join(path, "src"))
        rmtree(join(path, "pkg"))
    except (PermissionError, FileNotFoundError):
        pass
    comprimidos = encontrar_archivos(path, ".pkg.tar.zst") + \
        encontrar_archivos(path, ".tar.gz") + \
        encontrar_archivos(path, ".tar.xz") + \
        encontrar_archivos(path, ".deb") + \
        encontrar_archivos(path, ".pkg.tar.xz") + \
        encontrar_archivos(path, ".zip")
    for comprimido in comprimidos:
        remove(comprimido)


def search_files(path: str) -> list[str]:
    files: list[str] = []

    try:
        for file in listdir(path):
            full_path: str = join(path, file)

            if isdir(full_path):
                files = files + search_files(full_path)
            else:
                files.append(full_path)
    except PermissionError:
        pass

    return files


def get_size_mb(path: str) -> float:
    total = 0

    for file in search_files(path):
        if not islink(file):
            try:
                total += getsize(file)
            except OSError:
                pass

    return total / 1024 ** 2  # MB
