"""
    Copyright (C) 2025 KevinCrrl

    Este programa es software libre: puedes redistribuirlo y/o modificarlo
    está bajo los términos de la Licencia Pública General GNU publicada por
    la Free Software Foundation, ya sea la versión 3 de la Licencia, o
    (a su elección) cualquier versión posterior.

    Este programa se distribuye con la esperanza de que sea útil,
    pero SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de
    COMERCIABILIDAD o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Véase la
    Licencia Pública General GNU para más detalles.

    Debería haber recibido una copia de la Licencia Pública General GNU
    junto con este programa. Si no, consulte <https://www.gnu.org/licenses/>."""

from xdg.BaseDirectory import xdg_cache_home
from pkgbuild_parser import (
    Parser,
    parser_core
)
from colorama import (
    init,
    Fore
)
from os.path import (
    exists,
    join
)
from shutil import (
    rmtree,
    move
)
from os import (
    listdir,
    chdir,
    remove
)
from pathlib import Path
from utlds.parser import datos
from utlds.aurapi import existe, verificar_paquetes
import subprocess as sb
import webbrowser
import time
import sys

init(autoreset=True)

RUTA = join(xdg_cache_home, "kpa")


def clonar(paquete):
    if datos["clone_branch"]:
        url_repo = f"--branch {paquete} --single-branch {datos['url']} {paquete}"
    else:
        url_repo = f"{datos['url']}/{paquete}.git"

    if datos["torsocks"]:
        sb.run(["torsocks", "git", "clone"] + url_repo.split(), check=True)
    else:
        sb.run(["git", "clone"] + url_repo.split(), check=True)


def visor(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        print(archivo.read())


def no_aur(ruta):
    print(Fore.RED + "ERROR: Intentaste clonar un repositorio no existente del AUR.")
    rmtree(ruta)
    sys.exit(1)


def eula_detectado(ruta):
    nombres_comunes = ["eula.txt", "EULA.txt", "LICENSE.eula", "license.eula", "license.html", "LICENSE.html", "eula_text.html", "EULA_TEXT.html"]
    for archivo in listdir(ruta):
        if archivo in nombres_comunes:
            return True
    license = Parser(join(ruta, "PKGBUILD")).get_license()
    if "proprietary" in license or "Proprietary" in license:
        return True
    return False


def pkgbuild(paquete, actualizacion=False):
    print("\n")
    if datos["eula_detector"] and eula_detectado(join(RUTA, paquete)) and not actualizacion:
        print(Fore.YELLOW + "ADVERTENCIA: El paquete que intenta instalar contiene un posible EULA, se recomienda que lo lea antes de instalar.")
        pregunta = input("¿Desea continuar con la instalación de un paquete con EULA? (S/N): ")
        if pregunta.strip().lower() != "s":
            rmtree(join(RUTA, paquete))
            sys.exit()
    PKGBUILD = join(RUTA, paquete, "PKGBUILD")
    if datos["visor"] == "kpa":
        try:
            visor(PKGBUILD)
        except FileNotFoundError:
            no_aur(join(RUTA, paquete))
    else:
        try:
            sb.run([datos["visor"], PKGBUILD], check=True)
        except sb.CalledProcessError:
            no_aur(join(RUTA, paquete))
    confirmacion = input(Fore.YELLOW + "\nLea el PKGBUILD del repositorio clonado, ¿Desea continuar con la construcción? (S,N): ")
    if confirmacion.strip().lower() == "s":
        pkg = Parser(PKGBUILD)
        try:
            dependencias: list = pkg.get_depends() + pkg.get_makedepends()
        except (parser_core.ParserKeyError, parser_core.ParserNoneTypeError):
            print(Fore.RED + "Error al intentar obtener las dependencias del paquete.")
            dependencias = []
        en_aur: list = verificar_paquetes(dependencias)
        # Limpiar paquetes repetidos
        en_aur_limpio: list = []
        for paquete_en_aur in en_aur:
            if paquete_en_aur not in en_aur_limpio:
                en_aur_limpio.append(paquete_en_aur)
        if len(en_aur_limpio) != 0:
            print(Fore.YELLOW + f"Las siguientes dependencias de este paquete están en el AUR: {en_aur_limpio}")
            print("Si no están instaladas, estas dependencias se instalarán con KPA para evitar errores...")
            time.sleep(1)
            for paquete_aur in en_aur_limpio:
                # Verificar si el paquete ya está instalado para evitar errores
                try:
                    sb.run(["pacman", "-Qi", paquete_aur], check=True, capture_output=True)
                except sb.CalledProcessError:  # Error producido cuando el paquete no está instalado
                    # Usar la recursividad para instalar hasta que no hayan más paquetes AUR en los demás paquetes
                    instalar(paquete_aur)
            chdir(join(RUTA, paquete))
        print(Fore.BLUE + "Creando paquete con makepkg...")
        time.sleep(3)
        try:
            if datos["torsocks"]:
                sb.run(["torsocks", "makepkg", "-s"], check=True)  # Descargar el source usando TOR
            else:
                sb.run(["makepkg", "-s"], check=True)
            sb.run([datos["root"], "pacman", "-U"] + list(Path(join(RUTA, paquete)).glob("*.pkg.tar.zst")), check=True)  # Instala fuera pues si se usa TOR puede fallar la instalación.
        except sb.CalledProcessError:
            print(Fore.RED + "ERROR: Fallo al construir o instalar el paquete con makepkg.")
    else:
        # Correción de bug que eliminaba la carpeta de un paquete como si estuviera instalando cuando a veces es una actualización
        # Esta correción evita que se borre la carpeta en caso de actualización y solo se borre si no se quiere instalar por primera vez
        if not actualizacion:
            rmtree(join(RUTA, paquete))


def instalar(paquete):
    chdir(RUTA)
    print(Fore.BLUE + f"Clonando repositorio de {paquete}...")
    time.sleep(1)
    try:
        clonar(paquete)
    except sb.CalledProcessError:
        print(Fore.RED + "ERROR: El repositorio ya estaba clonado, si su intención es actualizar use el argumento -A")
        sys.exit(1)
    chdir(join(RUTA, paquete))
    pkgbuild(paquete)  # actualización por defecto queda en False


def actualizar_simple(paquete):
    chdir(join(RUTA, "act"))
    try:
        clonar(paquete)
        antiguo = Parser(join(RUTA, paquete, "PKGBUILD"))
        nuevo = Parser(join(RUTA, "act", paquete, "PKGBUILD"))
        if antiguo.get_full_package_name() == nuevo.get_full_package_name():
            print(Fore.YELLOW + f"No hay una nueva versión de {paquete}, las versiones en los PKGBUILDs siguen siendo iguales.\n")
            rmtree(join(RUTA, "act", paquete))
        else:
            rmtree(join(RUTA, paquete))
            move(join(RUTA, "act", paquete), join(RUTA))
            chdir(join(RUTA, paquete))
            pkgbuild(paquete, True)  # Se cambia el estado de actualización a True para que no elimine la carpeta
    except sb.CalledProcessError as e:
        print(Fore.RED + f"ERROR: Se produjo un error mientras se realizaba la actualización: {e}")


def actualizar_uno(paquete):
    if exists(join(RUTA, paquete)):
        if paquete in datos["ignorar"]:
            print(Fore.YELLOW + "ADVERTENCIA: El paquete que está intentando actualizar se encuentra en la lista de ignorados.")
            forzar = input("¿Desea actualizar a pesar de que el paquete esté en la lista? (S/N): ")
            if forzar.strip().lower() == "s":
                actualizar_simple(paquete)
        else:
            actualizar_simple(paquete)
    else:
        print(Fore.RED + f"ERROR: {paquete} no ha sido clonado, para ello use el argumento -I")


def actualizar_arg(paquete):
    if paquete == "todo":
        for directorio in listdir(RUTA):
            if directorio == "act" or directorio in datos["ignorar"]:
                continue
            actualizar_uno(directorio)
    else:
        actualizar_uno(paquete)


def desinstalar(paquete):
    print(Fore.YELLOW + f"ADVERTENCIA: Se quitará del sistema {paquete} y se eliminará su carpeta en kpa")
    confirmacion = input("¿Desea continuar? (S/N): ")
    if confirmacion.strip().lower() == "s":
        try:
            rmtree(join(RUTA, paquete))
            sb.run([datos["root"], "pacman", "-R", paquete, "--noconfirm"], check=True)
        except FileNotFoundError:
            print(Fore.RED + "ERROR: Este paquete no se encuentra en la carpeta kpa, por ende no se intentará desinstalar.")
        except sb.CalledProcessError:
            print(Fore.RED + "ERROR: Es posible que el paquete ya no estuviera instalado, pues falló el intentar eliminarlo con Pacman.")


def consultar(paquete):
    try:
        nav = webbrowser.get(datos["navegador"])
        nav.open(f"https://aur.archlinux.org/packages/{paquete}")
    except webbrowser.Error:
        print(Fore.RED + f"ERROR: No se ha encontrado el navegador {datos['navegador']} que fue seleccionado.")


def reinstalar(paquete):
    pdir = join(RUTA, paquete)
    if exists(pdir):
        for archivo in listdir(pdir):
            if archivo.endswith(".pkg.tar.zst"):
                completa = join(pdir, archivo)
                remove(completa)
        chdir(pdir)
        pkgbuild(paquete, True)  # Aunque no es una actualización, igualmente la carpeta no se debe borrar en una reinstalación
    else:
        print(Fore.RED + f"ERROR: No se puede reinstalar {paquete} ya que no está instalado.")


def limpiar(tipo):
    if tipo == "debug":
        try:
            instalados = sb.check_output(["pacman", "-Qm"], text=True)
        except sb.CalledProcessError:
            print(Fore.RED + "ERROR: Ha ocurrido un problema mientras se ejecutaba 'pacman -Qm'")
            sys.exit(1)
        for paquete in instalados.split("\n"):
            if "debug" in paquete:
                print(f"\nSe encontró el debug: {paquete}")
                eliminar = input("¿Desea eliminarlo del sistema? (S/N): ")
                if eliminar.strip().lower() == "s":
                    try:
                        sb.run([datos["root"], "pacman", "-R", paquete.split(" ")[0], "--noconfirm"], check=True)
                    except sb.CalledProcessError:
                        print(Fore.RED + "ERROR: Hubo un fallo al intentar remover el paquete.\n")
    elif tipo == "huerfanos":
        try:
            huerfanos = sb.check_output(["pacman", "-Qtdq"], text=True).strip()  # strip() para quitar el espacio al final que produce errores al intentar eliminar los paquetes huérfanos
        except sb.CalledProcessError as e:
            print(Fore.YELLOW + f"Parece que no hay paquetes huérfanos, pues se ha producido una excepción: {e}")
            sys.exit(1)
        print("Se encontraron los siguientes paquetes huérfanos:\n")
        print(huerfanos)
        eliminar = input("\n¿Desea eliminar los huérfanos del sistema? (S/N): ")
        if eliminar.strip().lower() == "s":
            try:
                sb.run([datos["root"], "pacman", "-Rns", "--noconfirm"] + huerfanos.split("\n"), check=True)
            except sb.CalledProcessError as e:
                print(Fore.RED + f"ERROR: Fallo al intentar eliminar los paquetes huérfanos: {e}")
    else:
        print(Fore.YELLOW + "El tipo de limpieza ingresado no es válido, solo se permite 'debug' o 'huerfanos'")
