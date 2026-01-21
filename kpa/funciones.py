# Copyright (C) 2025 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

from kpa.colorprints import yellow_input
from xdg.BaseDirectory import xdg_cache_home
from pkgbuild_parser import (
    Parser,
    parser_core
)
from os.path import (
    exists,
    join
)
from os import (
    listdir,
    chdir,
    remove,
)
from pathlib import Path
from shutil import rmtree
from kpa.parser import datos
from kpa.aurapi import verificar_paquetes
from kpa.colorprints import *
from kpa import git
from typer import Typer
import subprocess as sb
import sys

RUTA = join(xdg_cache_home, "kpa")

cli = Typer(
    context_settings={
        "allow_interspersed_args": True,
        "ignore_unknown_options": True,
    }
)


def encontrar_archivos(ruta: str, extension: str) -> list:
    return list(Path(ruta).glob(f"*{extension}"))


def visor(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        print(archivo.read())


def no_aur(ruta):
    red("ERROR: Intentaste clonar un repositorio no existente del AUR.")
    rmtree(ruta)
    sys.exit(1)


def eula_detectado(ruta):
    nombres_comunes = ["eula.txt", "EULA.txt", "LICENSE.eula", "license.eula", "license.html", "LICENSE.html", "eula_text.html", "EULA_TEXT.html"]
    licenses_comunes = ["Proprietary", "proprietary", "Custom", "custom"]
    for archivo in listdir(ruta):
        if archivo in nombres_comunes:
            return True
    pkg_license = Parser(join(ruta, "PKGBUILD")).get_license()
    for license_comun in licenses_comunes:
        if license_comun in pkg_license:
            return True
    return False


def pkgbuild(paquete, actualizacion=False):
    p_ruta = join(RUTA, paquete)
    print("\n")
    if datos["eula_detector"] and eula_detectado(join(RUTA, paquete)) and not actualizacion:
        yellow("ADVERTENCIA: El paquete que intenta instalar contiene un posible EULA, se recomienda que lo lea antes de instalar.")
        pregunta = input("¿Desea continuar con la instalación de un paquete con EULA? (S/N): ")
        if pregunta.strip().lower() != "s":
            rmtree(p_ruta)
            sys.exit()
    archivo_pkgbuild = join(p_ruta, "PKGBUILD")
    if datos["visor"] == "kpa":
        try:
            visor(archivo_pkgbuild)
        except FileNotFoundError:
            no_aur(p_ruta)
    else:
        try:
            sb.run([datos["visor"], archivo_pkgbuild], check=True)
        except sb.CalledProcessError:
            no_aur(p_ruta)
    confirmacion = yellow_input("\nLea el PKGBUILD del repositorio clonado, ¿Desea continuar con la construcción? (S,N): ")
    if confirmacion.strip().lower() == "s":
        pkg = Parser(archivo_pkgbuild)
        dependencias: list = []
        try:
            dependencias += pkg.get_depends()
            # Sumar por separado ya que no todos los paquetes tienen makedepends o checkdepends
            dependencias += pkg.get_makedepends()
            dependencias += pkg.get_checkdepends()
        except (parser_core.ParserKeyError, parser_core.ParserNoneTypeError):
            pass
        en_aur: list = verificar_paquetes(dependencias)
        # Limpiar paquetes repetidos
        en_aur_limpio: list = []
        for paquete_en_aur in en_aur:
            if paquete_en_aur not in en_aur_limpio:
                en_aur_limpio.append(paquete_en_aur)
        if len(en_aur_limpio) != 0:
            yellow(f"Las siguientes dependencias de este paquete están en el AUR: {en_aur_limpio}")
            print("Si no están instaladas, estas dependencias se instalarán con KPA para evitar errores...")
            for paquete_aur in en_aur_limpio:
                # Verificar si el paquete ya está instalado para evitar errores
                try:
                    sb.run(["pacman", "-Qi", paquete_aur], check=True, capture_output=True)
                except sb.CalledProcessError:  # Error producido cuando el paquete no está instalado
                    # Usar la recursividad para instalar hasta que no hayan más paquetes AUR en los demás paquetes
                    instalar(paquete_aur)
            chdir(p_ruta)
        blue("Creando paquete con makepkg...")
        try:
            sb.run(["makepkg", "-sfi"], check=True)
        except sb.CalledProcessError:
            red("ERROR: Fallo al construir o instalar el paquete con makepkg.")
    else:
        # Correción de bug que eliminaba la carpeta de un paquete como si estuviera instalando cuando a veces es una actualización
        # Esta correción evita que se borre la carpeta en caso de actualización y solo se borre si no se quiere instalar por primera vez
        if not actualizacion:
            rmtree(p_ruta)


@cli.command(name="-I", help="Instalar paquetes.")
def instalar(paquetes: list[str]):
    for paquete in paquetes:
        chdir(RUTA)
        blue(f"Clonando repositorio de {paquete}...")
        try:
            git.clonar(paquete)
            chdir(join(RUTA, paquete))
            pkgbuild(paquete)  # actualización por defecto queda en False
        except sb.CalledProcessError:
            red("ERROR: El repositorio ya estaba clonado, si su intención es actualizar use el argumento -A")


def actualizar_simple(paquete):
    ruta_paquete = join(RUTA, paquete)
    chdir(ruta_paquete)
    try:
        antiguo = Parser("PKGBUILD")
        git.pull()
        nuevo = Parser("PKGBUILD")
        if antiguo.get_full_package_name() == nuevo.get_full_package_name():
            yellow(f"No hay una nueva versión de {paquete}, las versiones en los PKGBUILDs siguen siendo iguales.\n")
        else:
            blue(f"Actualización encontrada para {paquete}")
            # Eliminar archivos caché
            try:
                rmtree("src")
                rmtree("pkg")
                comprimidos = encontrar_archivos(ruta_paquete, ".pkg.tar.zst") + encontrar_archivos(ruta_paquete, ".tar.gz") + encontrar_archivos(ruta_paquete, ".tar.xz") + encontrar_archivos(ruta_paquete, ".deb") + encontrar_archivos(ruta_paquete, ".pkg.tar.xz")
                for comprimido in comprimidos:
                    remove(comprimido)
            except FileNotFoundError:
                pass
            pkgbuild(paquete, True)  # Se cambia el estado de actualización a True para que no elimine la carpeta
    except sb.CalledProcessError as e:
        red(f"ERROR: Se produjo un error mientras se realizaba la actualización: {e}")


def actualizar_uno(paquete):
    if exists(join(RUTA, paquete)):
        if paquete in datos["ignorar"]:
            yellow("ADVERTENCIA: El paquete que está intentando actualizar se encuentra en la lista de ignorados.")
            forzar = input("¿Desea actualizar a pesar de que el paquete esté en la lista? (S/N): ")
            if forzar.strip().lower() == "s":
                actualizar_simple(paquete)
        else:
            actualizar_simple(paquete)
    else:
        red(f"ERROR: {paquete} no ha sido clonado, para ello use el argumento -I")


@cli.command(name="-A", help="Actualizar paquetes, use 'todo' para actualizar todos los paquetes")
def actualizar_arg(paquetes: list[str]):
    for paquete in paquetes:
        if paquete == "todo":
            for directorio in listdir(RUTA):
                if directorio == "act" or directorio in datos["ignorar"]:
                    continue
                actualizar_uno(directorio)
        else:
            actualizar_uno(paquete)


@cli.command(name="-D", help="Desinstalar paquetes")
def desinstalar(paquetes: list[str]):
    for paquete in paquetes:
        yellow(f"ADVERTENCIA: Se quitará del sistema {paquete} y se eliminará su carpeta en kpa")
        confirmacion = input("¿Desea continuar? (S/N): ")
        if confirmacion.strip().lower() == "s":
            try:
                rmtree(join(RUTA, paquete))
                sb.run([datos["root"], "pacman", "-R", paquete, "--noconfirm"], check=True)
            except FileNotFoundError:
                red("ERROR: Este paquete no se encuentra en la carpeta kpa, por ende no se intentará desinstalar.")
            except sb.CalledProcessError:
                red("ERROR: Es posible que el paquete ya no estuviera instalado, pues falló el intentar eliminarlo con Pacman.")


@cli.command("-R", help="Reinstalar paquetes.")
def reinstalar(paquetes: list[str]):
    for paquete in paquetes:
        pdir = join(RUTA, paquete)
        if exists(pdir):
            for archivo in listdir(pdir):
                if archivo.endswith(".pkg.tar.zst"):
                    completa = join(pdir, archivo)
                    remove(completa)
            chdir(pdir)
            pkgbuild(paquete, True)  # Aunque no es una actualización, igualmente la carpeta no se debe borrar en una reinstalación
        else:
            red(f"ERROR: No se puede reinstalar {paquete} ya que no está instalado.")


@cli.command(name="-L", help="Limpiar paquetes -debug con la opción 'debug' o paquetes huérfanos con la opción 'huerfanos'")
def limpiar(opciones: list[str]):
    for tipo in opciones:
        if tipo == "debug":
            try:
                instalados = sb.check_output(["pacman", "-Qm"], text=True)
            except sb.CalledProcessError:
                red("ERROR: Ha ocurrido un problema mientras se ejecutaba 'pacman -Qm'")
                sys.exit(1)
            # strip() para quitar el espacio al final que produce errores al intentar eliminar los paquetes debug y huérfanos
            for paquete in instalados.strip().split("\n"):
                if paquete.split()[0].endswith("-debug"):
                    print(f"\nSe encontró el debug: {paquete}")
                    eliminar = input("¿Desea eliminarlo del sistema? (S/N): ")
                    if eliminar.strip().lower() == "s":
                        try:
                            sb.run([datos["root"], "pacman", "-R", paquete.split(" ")[0], "--noconfirm"], check=True)
                        except sb.CalledProcessError:
                            red("ERROR: Hubo un fallo al intentar remover el paquete.\n")
        elif tipo == "huerfanos":
            try:
                huerfanos = sb.check_output(["pacman", "-Qtdq"], text=True).strip()
            except sb.CalledProcessError as e:
                yellow(f"Parece que no hay paquetes huérfanos, pues se ha producido una excepción: {e}")
                sys.exit(1)
            print("Se encontraron los siguientes paquetes huérfanos:\n")
            print(huerfanos)
            eliminar = input("\n¿Desea eliminar los huérfanos del sistema? (S/N): ")
            if eliminar.strip().lower() == "s":
                try:
                    sb.run([datos["root"], "pacman", "-Rns", "--noconfirm"] + huerfanos.split("\n"), check=True)
                except sb.CalledProcessError as e:
                    red(f"ERROR: Fallo al intentar eliminar los paquetes huérfanos: {e}")
        else:
            yellow("El tipo de limpieza ingresado no es válido, solo se permite 'debug' o 'huerfanos'")
