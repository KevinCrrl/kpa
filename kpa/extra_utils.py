# Copyright 2025-2026 - KevinCrrl
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from os import getenv, listdir, remove
from os.path import getsize, isdir, islink, join
from pathlib import Path
from shutil import rmtree
from subprocess import CalledProcessError, run

from pkgbuild_parser import Parser
from rich.syntax import Syntax
from rich.table import Table

from kpa.aurapi import extra_vals
from kpa.colorprints import console, red, yellow, yellow_input
from kpa.parser import datos


def confirm(
    text: str, question: str, e_mode: bool = False, file_emode: str = ""
) -> bool:
    correct_input: bool = False
    yellow(text)
    answer_fix: str = ""
    while not correct_input:
        if e_mode:
            answer = yellow_input(f"{question} (S/N/[E]ditar):")
        else:
            answer = yellow_input(f"{question} (S/N):")
        answer_fix = answer.strip().lower()
        if answer_fix in ("s", "n"):
            correct_input = True
        elif answer_fix == "e" and e_mode:
            editor: str | None = getenv("EDITOR")
            if editor is None:
                yellow("EDITOR no está definido, se intentará usar Nano como editor...")
                editor = "nano"

            try:
                run(editor.split() + [file_emode], check=True, shell=False)
            except CalledProcessError as e:
                yellow(f"Error al abrir el editor: {e}")
        else:
            yellow("Opción incorrecta, intente de nuevo...")

    return answer_fix == "s"


def encontrar_archivos(ruta: str, extension: str) -> list:
    return list(Path(ruta).glob(f"*{extension}"))


def visor(ruta_archivo: str):
    console.print(
        Syntax.from_path(
            ruta_archivo, lexer="bash", line_numbers=True, theme=datos["visor_theme"]
        )
    )


def no_aur(ruta: str):
    red("ERROR: Intentaste clonar un repositorio no existente del AUR.")
    rmtree(ruta)
    sys.exit(1)


def eula_detectado(ruta: str, parser: Parser) -> bool:
    nombres_comunes: list[str] = [
        "eula.txt",
        "license.eula",
        "license.html",
        "eula_text.html",
    ]
    licenses_comunes: list[str] = ["proprietary", "custom", "eula"]
    for archivo in listdir(ruta):
        if archivo.lower() in nombres_comunes:
            yellow(f"Posible EULA detectado en archivo: {archivo}")
            return True
    pkg_licenses: list[str] = parser.get_license()
    for license_comun in licenses_comunes:
        for pkg_license in pkg_licenses:
            if license_comun in pkg_license.lower():
                yellow(f"Posible EULA detectado en PKGBUILD: {pkg_license}")
                return True
    return False


def clean_cache(path: str):
    try:
        rmtree(join(path, "src"))
        rmtree(join(path, "pkg"))
    except (PermissionError, FileNotFoundError):
        pass
    to_remove: list[str] = []
    extensiones: list[str] = [
        ".tar.zst",
        ".tar.gz",
        "tar.xz",
        ".deb",
        ".zip",
        ".part",
        ".sig",
    ]
    for extension in extensiones:
        to_remove += encontrar_archivos(path, extension)
    for file_to_remove in to_remove:
        remove(file_to_remove)


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

    return total / 1024**2  # MB


def anti_idn_attack(sources: list[str]):
    abc: str = "abcdefghijklmnopqrstuvwxyz1234567890:/$¿?={}.,-_!¡[]#*+~&%';<>| "
    urls = 0
    for source in sources:
        alert = False
        positions: list[int] = []
        for index, char in enumerate(source.lower()):
            if char not in abc:
                alert = True
                positions.append(index)

        if alert:
            urls += 1
            red("ALERTA DE ATAQUE DE HOMÓGRAFOS DE IDN; URL sospechosa:")
            print(source)
            for i in range(len(source)):
                if i in positions:
                    red("^", "")
                else:
                    print(" ", end="")

            print()

        positions = []

    if urls != 0:
        red(
            f"Se encontraron {urls} sources sospechosos, aunque pueden ser falsas alarmas. Lea más aquí:"
        )
        print("https://en.wikipedia.org/wiki/IDN_homograph_attack\n")
        return confirm(
            "Los sources sospechosos pueden ser URLs que suplantan a una original.",
            "¿Continuar a pesar de la advertencia o pasar falsa alarma?",
        )

    return True


def warnings_table(package: str):
    warnings: list[str] = extra_vals(package)
    if len(warnings) > 0:
        table = Table(
            "ADVERTENCIAS", title="Advertencias adicionales para este paquete:"
        )

        for warning in warnings:
            table.add_row(warning, style="yellow")

        console.print(table)
