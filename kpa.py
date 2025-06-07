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
    expanduser
)
import sys

init(autoreset=True)

args = {
    "-I": instalar,
    "-A": actualizar_arg,
    "-D": desinstalar,
    "-C": consultar,
    "-R": reinstalar
}

try:
    for arg, funcion in args.items():
        if sys.argv[1] == "-h":
            print("""Argumentos válidos en KPA Versión 1.1.0:
-I paquete para instalar
-A paquete para actualizar un paquete instalado por kpa(o "-A todo" para actualización completa de todo lo instalado con kpa)
-D paquete para desinstalar. -D solo desinstala paquetes instalados por este AUR helper, no desinstala paquetes de otras fuentes como otro AUR helper o Pacman.
-C paquete para consultar sobre un paquete (abre un navegador con la página del paquete en el AUR)
-R paquete para reinstalar un paquete instalado por kpa

Recuerde crear el archivo ~/aur/kpa.json para configurar kpa correctamente, vea en https://github.com/KevinCrrl/kpa/blob/main/docs/json.png un ejemplo de como debería ser el archivo.""")
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
