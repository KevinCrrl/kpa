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

from colorama import (
    init,
    Fore
)
from os.path import (
    expanduser,
    exists
)
from shutil import rmtree
from os import listdir
import subprocess as sb
import time
import sys
import os

init(autoreset=True)

def pkgbuild(paquete):
    print("\n")
    try:
        sb.run(["cat", expanduser(f"~/aur/{paquete}/PKGBUILD")], check=True)
    except sb.CalledProcessError:
        print(Fore.RED + "ERROR: Intentaste clonar un repositorio no existente del AUR.")
        sb.run(["rm", "-rf", expanduser(f"~/aur/{paquete}")], check=True)
        sys.exit(1)
    confirmacion = input(Fore.YELLOW + "\nLea el PKGBUILD del repositorio clonado, ¿desea continuar con la construcción? (s,n): ")
    if confirmacion.strip().lower() == "s":
        print(Fore.BLUE + "Creando paquete con makepkg...")
        time.sleep(3)
        sb.run(["makepkg", "-si"], check=True)
    else:
        rmtree(expanduser(f"~/aur/{paquete}"))
        sys.exit()

def instalar(paquete):
    os.chdir(expanduser("~/aur/"))
    repositorio = f"https://aur.archlinux.org/{paquete}.git"
    print(Fore.BLUE + f"Clonando {repositorio}...")
    time.sleep(3)
    try:
        sb.run(["git", "clone", repositorio], check=True)
    except sb.CalledProcessError:
        print(Fore.RED + "ERROR: El repositorio ya estaba clonado, si su intención es actualizar use el argumento -A")
        sys.exit(1)
    os.chdir(expanduser(f"~/aur/{paquete}"))
    pkgbuild(paquete)

def actualizar_uno(paquete):
    if exists(expanduser(f"~/aur/{paquete}")):
        os.chdir(expanduser("~/aur/act"))
        sb.run(["git", "clone", f"https://aur.archlinux.org/{paquete}.git"], check=True)
        with open(expanduser(f"~/aur/{paquete}/PKGBUILD"), 'rb') as antiguo, open(expanduser(f"~/aur/act/{paquete}/PKGBUILD"), 'rb') as nuevo:
            comparar = antiguo.read() == nuevo.read()
        if comparar:
            print(Fore.YELLOW + f"No hay una nueva versión de {paquete}, los PKGBUILD siguen siendo iguales.\n")
            rmtree(expanduser(f"~/aur/act/{paquete}"))
        else:
            sb.run(["mv", "-f", expanduser(f"~/aur/act/{paquete}"), expanduser("~/aur/")], check=True)
            pkgbuild(paquete)
    else:
        print(Fore.RED + f"ERROR: {paquete} no ha sido clonado, para ello use el argumento -I")

def actualizar_arg(paquete):
    if paquete == "todo":
        for directorio in listdir(expanduser("~/aur/")):
            if directorio == "act":
                pass
            else:
                actualizar_uno(directorio)
    else:
        actualizar_uno(paquete)

def desinstalar(paquete):
    print(Fore.YELLOW + f"ADVERTENCIA: Se quitará del sistema {paquete} y se eliminará su carpeta en ~/aur")
    confirmacion = input("¿Desea continuar? (s/n): ")
    if confirmacion.strip().lower() == "s":
        try:
            rmtree(expanduser(f"~/aur/{paquete}"))
        except FileNotFoundError:
            print(Fore.RED + "ERROR: Este paquete no se encuentra en la carpeta ~/aur, por ende no se intentará desinstalar.")
            sys.exit(1)
        sb.run(["sudo", "pacman", "-Rns", paquete], check=True)
