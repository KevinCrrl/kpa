# Copyright (C) 2025-2026 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

from os.path import exists, join
from os import listdir, chdir
from shutil import rmtree
from typing import Annotated
import subprocess as sb
import json
import sys

from xdg.BaseDirectory import xdg_cache_home, xdg_config_home
from pkgbuild_parser import Parser, ParserKeyError
from typer import Typer, Option
from rich.syntax import Syntax
import jsonschema

from kpa.extra_utils import (clean_cache, confirm, eula_detectado,
                             visor, no_aur, get_size_mb, anti_idn_attack)
from kpa.parser import datos, kpa_schema
from kpa.aurapi import verificar_paquetes
from kpa.colorprints import blue, yellow, red, green, console
from kpa import git

RUTA: str = join(xdg_cache_home, "kpa")

cli = Typer(suggest_commands=True)


@cli.command(name="version", help="Mostrar la versión instalada de KPA.")
def version():
    print("KPA Versión 3.1.0")


def pkgbuild(paquete: str, actualizacion: bool = False, verbose: bool = False,
             ignore_pkgbuild: bool = False, show_install_script: bool = False):
    p_ruta = join(RUTA, paquete)
    pkg = Parser()
    print("\n")

    # DETECCION DE EULA
    if datos["eula_detector"] and eula_detectado(join(RUTA, paquete)) and not actualizacion:
        value = confirm(
            "ADVERTENCIA: El paquete que intenta instalar contiene un posible EULA, se recomienda que lo lea antes de instalar.",
            "¿Desea continuar con la instalación de un paquete con EULA?",
        )
        if not value:
            rmtree(p_ruta)
            sys.exit()

    # MOSTRAR PKGBUILD O NO
    if not ignore_pkgbuild:
        archivo_pkgbuild = join(p_ruta, "PKGBUILD")
        user_visor = datos["visor"].split()
        try:
            if user_visor[0] == "kpa":
                visor(archivo_pkgbuild)
            else:
                sb.run(user_visor + [archivo_pkgbuild], check=True)
        except (FileNotFoundError, sb.CalledProcessError):
            no_aur(p_ruta)

    # MOSTRAR SCRIPT DE INSTALACION O NO
    if (not actualizacion) or show_install_script:
        try:
            install_script = pkg.get_install()
            yellow("\nADVERTENCIA: Se ha detectado un script install en el PKGBUILD, se imprimirá para que lo lea:\n")
            visor(join(p_ruta, install_script))
        except ParserKeyError:
            pass  # No hay install en el PKGBUILD, se pasa por alto
        except FileNotFoundError:
            yellow(f"ADVERTENCIA: El script install parece usar un nombre complejo que no se pudo resolver: {install_script}")

    # VERIFICAR ATAQUES IDN
    try:
        sources: list[str] = pkg.get_source()
    except ParserKeyError:
        sources = pkg.multiline(f"source_{pkg.get_arch()[0]}")

    if not anti_idn_attack(sources):
        if not actualizacion:
            rmtree(p_ruta)
        sys.exit(1)

    # PREGUNTAR POR LA LECTURA DEL PKGBUILD
    if not actualizacion:
        value = confirm(
            "", "\nLea el PKGBUILD del repositorio clonado, ¿Desea continuar con la construcción?",
            True, archivo_pkgbuild)
    else:
        value = confirm(
            "", "\nLea el PKGBUILD y/o diff del pull realizado, ¿Desea continuar con la construcción?",
            True, archivo_pkgbuild)

    # VERIFICAR DEPENDENCIAS SI SE ACEPTA LA INSTALACION
    if value:
        dependencias: list = []
        try:
            dependencias += pkg.get_depends()
            # Sumar por separado ya que no todos los paquetes tienen makedepends o checkdepends
            dependencias += pkg.get_makedepends()
            dependencias += pkg.get_checkdepends()
        except ParserKeyError:
            pass
        if verbose:
            blue(
                f"Dependencias parseadas sin procesar por KPA: {dependencias}\n")
        en_aur: list = verificar_paquetes(dependencias)
        # Limpiar paquetes repetidos
        en_aur_limpio: list = []
        for paquete_en_aur in en_aur:
            if paquete_en_aur not in en_aur_limpio:
                en_aur_limpio.append(paquete_en_aur)
        if len(en_aur_limpio) != 0:
            yellow(
                f"Las siguientes dependencias de este paquete están en el AUR: {en_aur_limpio}")
            print(
                "Si no están instaladas, estas dependencias se instalarán con KPA para evitar errores...")
            for paquete_aur in en_aur_limpio:
                # Verificar si el paquete ya está instalado para evitar errores
                try:
                    sb.run(["pacman", "-Qi", paquete_aur],
                           check=True, capture_output=True)
                except sb.CalledProcessError:  # Error producido cuando el paquete no está instalado
                    # Usar la recursividad para instalar hasta que no hayan
                    # más paquetes AUR en los demás
                    instalar(paquete_aur.split())
            chdir(p_ruta)

        # INSTALAR
        blue("Creando paquete con makepkg...")
        try:
            sb.run(["makepkg", "-sfi"], check=True)
        except sb.CalledProcessError:
            red("ERROR: Fallo al construir o instalar el paquete con makepkg.")
    else:
        # Correción de bug que eliminaba la carpeta de un paquete como si estuviera
        # instalando cuando a veces es una actualización
        # Esta correción evita que se borre la carpeta en caso de actualización
        # y solo se borre si no se quiere instalar por primera vez
        if not actualizacion:
            rmtree(p_ruta)


@cli.command(name="Ins", help="Instalar paquetes.")
def instalar(paquetes: list[str],
             verbose: Annotated[bool, Option(
                 help="Mostrar información extra.")] = False,
             reinstall: Annotated[bool, Option(help="Reinstalar el paquete en vez de intentar instalarlo.")] = False,
             show_install_script: Annotated[bool, Option(help="Mostrar el script install incluso en una reinstalación.")] = False):
    for paquete in paquetes:
        chdir(RUTA)
        RUTA_PAQUETE = join(RUTA, paquete)
        try:
            if not reinstall:
                blue(f"Clonando repositorio de {paquete}...")
                git.clone(paquete, verbose)
            else:
                if not exists(RUTA_PAQUETE):
                    red(
                        f"ERROR: No se puede reinstalar {paquete} ya que no está instalado.")
                    sys.exit(1)
                clean_cache(RUTA_PAQUETE)
            chdir(RUTA_PAQUETE)
            pkgbuild(paquete, reinstall, verbose, False, show_install_script)
        except sb.CalledProcessError:
            if confirm("""ADVERTRNCIA: El repositorio ya estaba clonado, si su intención es
actualizar use el argumento -A""", "O por el contrario...\n¿Desea realizar una reinstalación?"):
                instalar(paquetes, verbose, True, show_install_script)


class Updater:
    def __init__(self, paquetes: list[str], verbose: bool,
                 force: bool, ignorados: bool, solo_ignorados: bool,
                 ignore_diff: bool, ignore_pkgbuild: bool):
        self.paquetes = paquetes
        self.verbose = verbose
        self.force = force
        self.ignorados = ignorados
        self.solo_ignorados = solo_ignorados
        self.ignore_diff = ignore_diff
        self.ignore_pkgbuild = ignore_pkgbuild

    def actualizar_simple(self, paquete: str):
        ruta_paquete: str = join(RUTA, paquete)
        chdir(ruta_paquete)
        try:
            antiguo = Parser()
            output: str = git.pull(self.verbose, self.ignore_diff)
            nuevo = Parser()
            a_name: str = antiguo.get_full_package_name()
            n_name: str = nuevo.get_full_package_name()
            if self.verbose:
                blue(
                    f"Versión antes del pull: {a_name} y versión despues del pull: {n_name}")
            if a_name == n_name:
                yellow(
                    f"No hay una nueva versión de {paquete}, las versiones en los PKGBUILDs siguen siendo iguales.\n")
            else:
                blue(f"Actualización encontrada para {paquete}")
                if not self.ignore_diff:
                    if output == "" and self.ignore_pkgbuild:
                        yellow(
                            "El diff está vacío por un aparente error, se forzará la vista del PKGBUILD completo.")
                        self.ignore_pkgbuild = False
                    else:
                        blue("Mostrando diff...\n")
                        console.print(
                            Syntax(output, "diff", theme=datos["visor_theme"], line_numbers=True))
                        if not self.ignore_pkgbuild:
                            blue("\n\nMostrando PKGBUILD...\n")
                clean_cache(ruta_paquete)
                # Se cambia el estado de actualización a True para que no elimine la carpeta
                pkgbuild(paquete, True, self.verbose, self.ignore_pkgbuild)
        except sb.CalledProcessError as e:
            red(
                f"ERROR: Se produjo un error mientras se realizaba la actualización: {e}")
            if self.force:
                yellow("Reintentando en modo force...")
                rmtree(join(RUTA, paquete))
                pkgbuild(paquete, True, self.verbose)

    def actualizar_uno(self, paquete: str):
        if exists(join(RUTA, paquete)):
            if paquete in datos["ignorar"] and (not self.ignorados and not self.solo_ignorados):
                value = confirm(
                    "ADVERTENCIA: El paquete que está intentando actualizar se encuentra en la lista de ignorados.",
                    "¿Desea actualizar a pesar de que el paquete esté en la lista?"
                )
                if value:
                    self.actualizar_simple(paquete)
            else:
                self.actualizar_simple(paquete)
        else:
            red(f"ERROR: {paquete} no ha sido clonado, para ello use el argumento -I")

    def iniciar_actualizar(self):
        for paquete in self.paquetes:
            if paquete == "todo":
                for directorio in listdir(RUTA):
                    if not ((not self.ignorados) and directorio
                            in datos["ignorar"]) and not self.solo_ignorados:
                        self.actualizar_uno(directorio)
                    elif self.solo_ignorados and directorio in datos["ignorar"]:
                        self.actualizar_uno(directorio)
            else:
                self.actualizar_uno(paquete)


@cli.command(name="Act", help="Actualizar paquetes, use 'todo' para actualizar todos los paquetes.")
def actualizar_arg(paquetes: list[str],
                   verbose: Annotated[bool, Option(
                       help="Mostrar información extra.")] = False,
                   force: Annotated[bool, Option(
                       help="Forzar la actualización en caso de error.")] = False,
                   ignorados: Annotated[bool, Option(
                       help="Actualizar los paquetes ignorados.")] = False,
                   ignore_diff: Annotated[bool, Option(
                       help="No mostrar el diff de cambios, solo el PKGBUILD.")] = False,
                   ignore_pkgbuild: Annotated[bool, Option(
                       help="No muestra el PKGBUILD, solo el diff")] = False,
                   solo_ignorados: Annotated[bool, Option(help="Actualizar SOLO los ignorados \
(No aplica a paquetes individuales).")] = False):
    if ignore_pkgbuild and ignore_diff:
        red("""ERROR: No se puede ignorar tanto el PKGBUILD como el diff.
Esto supone un riesgo de seguridad, solo puede ignorar una de las 2 cosas.""")
        sys.exit(1)
    Updater(paquetes, verbose, force, ignorados,
            solo_ignorados, ignore_diff, ignore_pkgbuild).iniciar_actualizar()


@cli.command(name="Des", help="Desinstalar paquetes.")
def desinstalar(paquetes: list[str]):
    for paquete in paquetes:
        value = confirm(
            f"ADVERTENCIA: Se quitará del sistema {paquete} y se eliminará su carpeta en kpa",
            "¿Desea continuar?"
        )
        if value:
            try:
                rmtree(join(RUTA, paquete))
                sb.run([datos["root"], "pacman", "-R",
                       paquete, "--noconfirm"], check=True)
            except FileNotFoundError:
                red("ERROR: Este paquete no se encuentra en la carpeta kpa, \
por ende no se intentará desinstalar.")
            except sb.CalledProcessError:
                red("ERROR: Es posible que el paquete ya no estuviera \
instalado, pues falló el intentar eliminarlo con Pacman.")


@cli.command(name="Limp", help="Limpiar paquetes huérfanos \
con la opción 'huerfanos' o caché con la opción 'cache'")
def limpiar(opciones: list[str]):
    for tipo in opciones:
        if tipo == "huerfanos":
            try:
                huerfanos = sb.check_output(
                    ["pacman", "-Qtdq"], text=True).strip()
            except sb.CalledProcessError as e:
                yellow(
                    f"Parece que no hay paquetes huérfanos, pues se ha producido una excepción: {e}")
                sys.exit(1)
            value = confirm(
                "Se encontraron los siguientes paquetes huérfanos:\n\n" + huerfanos,
                "\n¿Desea eliminar los huérfanos del sistema?"
            )
            if value:
                try:
                    sb.run([datos["root"], "pacman", "-Rns",
                           "--noconfirm"] + huerfanos.split("\n"), check=True)
                except sb.CalledProcessError as e:
                    red(
                        f"ERROR: Fallo al intentar eliminar los paquetes huérfanos: {e}")
        elif tipo == "cache":
            blue("Limpiando caché de KPA...")
            yellow(
                f"Peso antes de realizar la limpieza: {round(get_size_mb(RUTA), 2)} MB")
            for paquete in listdir(RUTA):
                ppath = join(RUTA, paquete)
                chdir(ppath)
                clean_cache(ppath)
            green("La caché de KPA ha sido eliminada!")
            green(
                f"Peso despues de la limpieza: {round(get_size_mb(RUTA), 2)} MB")
        else:
            yellow(
                "El tipo de limpieza ingresado no es válido, solo se permite 'huerfanos' o 'cache'")


@cli.command(name="Conf", help="Cambiar la configuración en el archivo kpa.json")
def conf(to_set: str):
    to_set_list = to_set.split("=")
    bools = {
        "True": True,
        "False": False,
        "true": True,
        "false": False
    }
    if to_set_list[0] not in datos:
        yellow("El valor que intentas configurar no es un valor válido para KPA.")
        sys.exit(1)
    try:
        if to_set_list[0] in ["eula_detector", "clone_branch"]:
            if to_set_list[1] not in bools:
                yellow(
                    f"{to_set_list[0]} solo admite booleanos, use 'True', 'true' o 'False', 'false'")
                sys.exit(1)
            to_set_list[1] = bools[to_set_list[1]]
        elif to_set_list[0] == "ignorar":
            if "[" in to_set_list[1] or "]" in to_set_list[1]:
                yellow(
                    "El valor de 'ignorar' no puede incluir corchetes, debe ser 'ignorar=\"paquete paquete2\"'")
                sys.exit(1)
            to_set_list[1] = to_set_list[1].split()
        datos[to_set_list[0]] = to_set_list[1]

        # Validar antes de aplicar
        jsonschema.validate(datos, kpa_schema)

        # Escribir despues de todas las validaciones
        with open(join(xdg_config_home, "kpa", "kpa.json"), "w", encoding="utf-8") as cf:
            json.dump(datos, cf, indent=4, ensure_ascii=False)
    except IndexError:
        red("ERROR: El valor que intentaste configurar no tiene el estilo 'llave=valor'")
    except jsonschema.exceptions.ValidationError as e:
        red(f"Error: Falló la validación de la configuración: {e}")
