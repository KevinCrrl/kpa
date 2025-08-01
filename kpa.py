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

from utlds.funciones import (
    instalar,
    actualizar_arg,
    desinstalar,
    consultar,
    reinstalar
)
from colorama import (
    init,
    Fore
)
from os.path import (
    exists,
    expanduser,
    join
)
from os import (
    geteuid,
    makedirs
)
from utlds.multiple import multiarg
from shutil import move
from xdg.BaseDirectory import xdg_cache_home
import sys

init(autoreset=True)

args = {
    "-I": instalar,
    "-A": actualizar_arg,
    "-D": desinstalar,
    "-C": consultar,
    "-R": reinstalar,
    "-M": multiarg,
}

if geteuid() == 0:
    print(Fore.YELLOW + "ATENCIÓN: No se debe usa KPA con permisos root, los comandos que lo requieran se gestionan internamente.")
    print("Vuelva a ejecutar KPA como usuario no-root.")
    sys.exit(1)

# Verificación de cada posible caso de rutas, la ruta ~/aur aún se revisa, sin embargo, no se usa como tal en el programa. se usa ahora el éstandar XDG

# La verificación de ~/aur desaparecerá en la versión 2.0 de KPA
RUTA_ANTIGUA = expanduser("~/aur/act")
RUTA_NUEVA = join(xdg_cache_home, "kpa/act")

if exists(RUTA_ANTIGUA) and not exists(RUTA_NUEVA):
    print(Fore.YELLOW + "ADVERTENCIA: la ruta ~/aur/ no será usada más, KPA moverá la carpeta antigua a tu carpeta .cache")
    move(expanduser("~/aur"), join(xdg_cache_home, "kpa"))

elif not exists(RUTA_ANTIGUA) and not exists(RUTA_NUEVA):
    print("Creando ruta para KPA...\n")
    makedirs(RUTA_NUEVA, exist_ok=True)

elif not exists(RUTA_ANTIGUA) and exists(RUTA_NUEVA):
    print(Fore.GREEN + "Ruta de KPA encontrada...\n")

try:
    for arg, funcion in args.items():
        if sys.argv[1] == "-h":
            print("""Argumentos válidos en KPA Versión 1.3.0:
-I paquete para instalar
-A paquete para actualizar un paquete instalado por kpa(o "-A todo" para actualización completa de todo lo instalado con kpa)
-D paquete para desinstalar. -D solo desinstala paquetes instalados por este AUR helper, no desinstala paquetes de otras fuentes como otro AUR helper o Pacman.
-C paquete para consultar sobre un paquete (abre un navegador con la página del paquete en el AUR)
-R paquete para reinstalar un paquete instalado por kpa

Recuerde crear el archivo kpa.json para configurar kpa correctamente, vea en https://KevinCrrl.github.io/KevinCrrl/documentacion/kpa.html un ejemplo de como debería ser el archivo.""")
            break
        elif sys.argv[1] == arg:
            funcion(sys.argv[2])
            break

    else:
        print(Fore.RED + "ERROR: No se encontró el argumento ingresado. Use -h para obtener los comandos disponibles.")
except IndexError:
    print(Fore.RED + "ERROR: Ingresó una cantidad incorrecta de argumentos.")
except KeyboardInterrupt:
    print(Fore.YELLOW + "\nSaliendo del programa por interrupción de teclado.")
