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

from xdg.BaseDirectory import (
    xdg_cache_home,
    xdg_config_home
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
import subprocess as sb
import jsonschema
import webbrowser
import json
import time
import sys

init(autoreset=True)

RUTA = join(xdg_cache_home, "kpa")

datos = {
    "visor": "kpa",  # Visor independiente de KPA
    "torsocks": False,  # Evitar uso de Tor si no está instalado o configurado
    "navegador": "firefox",  # Uno de los navegadores más usados en Linux, sin embargo, está opción es para no dejar vacío el espacio de configuración
    "root": "sudo",  # La forma más común de acceder a root es sudo, también se usa para no dejar vacío el espacio
    "ignorar": [],  # No ignorar paquetes por defecto
    "eula_detector": True  # Activado por defecto para mejor seguridad legal
}

try:
    with open(join(xdg_config_home, "kpa", "kpa.json"), "r", encoding="utf-8") as cf:
        datos = json.load(cf)
except FileNotFoundError:
    print(Fore.RED + "ERROR: Archivo de configuración 'kpa.json' no encontrado.\n")
except json.decoder.JSONDecodeError:
    print(Fore.RED + "ERROR: No se pudo obtener contenido del archivo 'kpa.json'\n")

# Validacipon extra del archivo JSON usando jsonschema

kpa_schema = {
    "type": "object",
    "properties": {
        "visor": {"type": "string"},
        "torsocks": {"type": "boolean"},
        "navegador": {"type": "string"},
        "root": {"type": "string"},
        "ignorar": {"type": "array", "items": {"type": "string"}},
        "eula_detector": {"type": "boolean"}
    },
    "required": ["visor", "torsocks", "navegador", "root", "ignorar", "eula_detector"]
}

try:
    jsonschema.validate(datos, kpa_schema)
except jsonschema.exceptions.ValidationError as e:
    print(Fore.RED + f"ERROR: La validación de configuración de KPA encontró un error en tu archivo kpa.json: {e}")
    sys.exit(1)


def clonar(url_repo):
    if datos["torsocks"]:
        sb.run(["torsocks", "git", "clone", url_repo], check=True)
    else:
        sb.run(["git", "clone", url_repo], check=True)


def visor(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as a_recorrer:
        for linea in a_recorrer:
            print(linea.strip())


def no_aur(ruta):
    print(Fore.RED + "ERROR: Intentaste clonar un repositorio no existente del AUR.")
    rmtree(ruta)
    sys.exit(1)


def eula_detectado(ruta):
    nombres_comunes = ["eula.txt", "EULA.txt", "LICENSE.eula", "license.eula", "license.html", "LICENSE.html", "eula_text.html", "EULA_TEXT.html"]
    for archivo in listdir(ruta):
        if archivo in nombres_comunes:
            return True
    return False


def pkgbuild(paquete, actualizacion=False):
    print("\n")
    if datos["eula_detector"] and eula_detectado(join(RUTA, paquete)) and not actualizacion:
        print(Fore.YELLOW + "ADVERTENCIA: El paquete que intenta instalar contiene un posible EULA, se recomienda que lo lea antes de instalar.")
        instalar = input("¿Desea continuar con la instalación de un paquete con EULA? (S/N): ")
        if instalar.strip().lower() != "s":
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
    confirmacion = input(Fore.YELLOW + "\nLea el PKGBUILD del repositorio clonado, ¿desea continuar con la construcción? (s,n): ")
    if confirmacion.strip().lower() == "s":
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
        clonar(f"https://aur.archlinux.org/{paquete}.git")
    except sb.CalledProcessError:
        print(Fore.RED + "ERROR: El repositorio ya estaba clonado, si su intención es actualizar use el argumento -A")
        sys.exit(1)
    chdir(join(RUTA, paquete))
    pkgbuild(paquete)  # actualización por defecto queda en False


def actualizar_uno(paquete):
    if exists(join(RUTA, paquete)):
        if paquete in datos["ignorar"]:
            print(Fore.YELLOW + "ADVERTENCIA: El paquete que está intentando actualizar se encuentra en la lista de ignorados.")
            forzar = input("¿Desea actualizar a pesar de que el paquete esté en la lista? (S/N): ")
            if forzar.strip().lower() == "s":
                pass
            else:
                sys.exit(0)
        chdir(join(RUTA, "act"))
        try:
            clonar(f"https://aur.archlinux.org/{paquete}.git")
            with open(join(RUTA, paquete, "PKGBUILD"), 'rb') as antiguo, open(join(RUTA, "act", paquete, "PKGBUILD"), 'rb') as nuevo:
                comparar = antiguo.read() == nuevo.read()
            if comparar:
                print(Fore.YELLOW + f"No hay una nueva versión de {paquete}, los PKGBUILD siguen siendo iguales.\n")
                rmtree(join(RUTA, "act", paquete))
            else:
                rmtree(join(RUTA, paquete))
                move(join(RUTA, "act", paquete), join(RUTA))
                chdir(join(RUTA, paquete))
                pkgbuild(paquete, True)  # Se cambia el estado de actualización a True para que no elimine la carpeta
        except sb.CalledProcessError as e:
            print(Fore.RED + f"ERROR: Se produjo un error mientras se realizaba la actualización: {e}")
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
    confirmacion = input("¿Desea continuar? (s/n): ")
    if confirmacion.strip().lower() == "s":
        try:
            rmtree(join(RUTA, paquete))
            sb.run([datos["root"], "pacman", "-Rns", paquete, "--noconfirm"], check=True)
        except FileNotFoundError:
            print(Fore.RED + "ERROR: Este paquete no se encuentra en la carpeta kpa, por ende no se intentará desinstalar.")
        except sb.CalledProcessError:
            print(Fore.RED + "ERROR: Es posible que él paquete ya no estuviera instalado, pues falló el intentar eliminarlo con Pacman.")


def consultar(paquete):
    try:
        nav = webbrowser.get(datos["navegador"])
        nav.open(f"https://aur.archlinux.org/packages/{paquete}")
    except webbrowser.Error:
        print(Fore.RED + f"ERROR: No se ha encontrado el navegador {datos["navegador"]} que fue seleccionado.")


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
