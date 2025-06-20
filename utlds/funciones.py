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
    exists,
    join
)
from shutil import rmtree
from os import (
    listdir,
    chdir,
    makedirs,
    remove
)
import subprocess as sb
import webbrowser
import json
import time
import sys

init(autoreset=True)

if exists(expanduser("~/aur/act")):
    print(Fore.GREEN + "Ruta de AUR encontrada...\n")
else:
    print(Fore.RED + "ATENCIÓN: No se encontró la carpeta ~/aur o ~/aur/act\nCreando carpeta...")
    makedirs(expanduser("~/aur/act"), exist_ok=True)

datos = {
    "visor": "cat",
    "torsocks": False,
}
try:
    with open(expanduser("~/aur/kpa.json"), "r", encoding="utf-8") as cf:
        datos = json.load(cf)
except FileNotFoundError:
    print(Fore.RED + "ERROR: Archivo de configuración '~/aur/kpa.json' no encontrado.\n")
except json.decoder.JSONDecodeError:
    print(Fore.RED + "ERROR: No se pudo obtener contenido del archivo '~/aur/kpa.json'\n")

def novar(variable):
    print(Fore.RED + f"ERROR: No se pudo obtener la variable '{variable}' de ~/aur/kpa.json")

def clonar(url_repo):
    try:
        if datos["torsocks"]:
            sb.run(["torsocks", "git", "clone", url_repo], check=True)
        else:
            sb.run(["git", "clone", url_repo], check=True)
    except KeyError:
        novar("torsocks")
        print(Fore.YELLOW + ">> Clonando de manera común y corriente...")
        sb.run(["git", "clone", url_repo], check=True)

def pkgbuild(paquete):
    print("\n")
    try:
        sb.run([datos["visor"], expanduser(f"~/aur/{paquete}/PKGBUILD")], check=True)
    except sb.CalledProcessError:
        print(Fore.RED + "ERROR: Intentaste clonar un repositorio no existente del AUR.")
        rmtree(expanduser(f"~/aur/{paquete}"))
        sys.exit(1)
    confirmacion = input(Fore.YELLOW + "\nLea el PKGBUILD del repositorio clonado, ¿desea continuar con la construcción? (s,n): ")
    if confirmacion.strip().lower() == "s":
        print(Fore.BLUE + "Creando paquete con makepkg...")
        time.sleep(3)
        try:
            sb.run(["makepkg", "-si"], check=True)
        except sb.CalledProcessError:
            print(Fore.RED + "ERROR: Fallo al construir o instalar el paquete con makepkg.")
    else:
        rmtree(expanduser(f"~/aur/{paquete}"))
        sys.exit()

def instalar(paquete):
    chdir(expanduser("~/aur/"))
    print(Fore.BLUE + f"Clonando repositorio de {paquete}...")
    time.sleep(1)
    try:
        clonar(f"https://aur.archlinux.org/{paquete}.git")
    except sb.CalledProcessError:
        print(Fore.RED + "ERROR: El repositorio ya estaba clonado, si su intención es actualizar use el argumento -A")
        sys.exit(1)
    chdir(expanduser(f"~/aur/{paquete}"))
    pkgbuild(paquete)

def actualizar_uno(paquete):
    if exists(expanduser(f"~/aur/{paquete}")):
        chdir(expanduser("~/aur/act"))
        clonar(f"https://aur.archlinux.org/{paquete}.git")
        with open(expanduser(f"~/aur/{paquete}/PKGBUILD"), 'rb') as antiguo, open(expanduser(f"~/aur/act/{paquete}/PKGBUILD"), 'rb') as nuevo:
            comparar = antiguo.read() == nuevo.read()
        if comparar:
            print(Fore.YELLOW + f"No hay una nueva versión de {paquete}, los PKGBUILD siguen siendo iguales.\n")
            rmtree(expanduser(f"~/aur/act/{paquete}"))
        else:
            rmtree(expanduser(f"~/aur/{paquete}"))
            sb.run(["mv", expanduser(f"~/aur/act/{paquete}"), expanduser("~/aur/")], check=True)
            chdir(expanduser(f"~/aur/{paquete}"))
            pkgbuild(paquete)
    else:
        print(Fore.RED + f"ERROR: {paquete} no ha sido clonado, para ello use el argumento -I")

def actualizar_arg(paquete):
    if paquete == "todo":
        for directorio in listdir(expanduser("~/aur/")):
            if directorio == "act" or directorio == "kpa.json":
                continue
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

def consultar(paquete):
    try:
        nav = webbrowser.get(datos["navegador"])
        nav.open(f"https://aur.archlinux.org/packages/{paquete}")
    except webbrowser.Error:
        print(Fore.RED + f"ERROR: No se ha encontrado el navegador {datos["navegador"]} que fue seleccionado.")
    except KeyError:
        novar("navegador")

def reinstalar(paquete):
    pdir = expanduser(f"~/aur/{paquete}") 
    if exists(pdir):
        for archivo in listdir(pdir):
            if archivo.endswith(".pkg.tar.zst"):
                completa = join(pdir, archivo)
                remove(completa)
        chdir(pdir)
        pkgbuild(paquete)
    else:
        print(Fore.RED + f"ERROR: No se puede reinstalar {paquete} ya que no está instalado.")
