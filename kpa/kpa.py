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

from kpa.funciones import (
    instalar,
    actualizar_arg,
    desinstalar,
    consultar,
    reinstalar,
    limpiar
)
from os.path import (
    exists,
    join
)
from os import (
    geteuid,
    makedirs
)
from kpa.colorprints import *
from xdg.BaseDirectory import xdg_cache_home
import sys

args = {
    "-I": instalar,
    "-A": actualizar_arg,
    "-D": desinstalar,
    "-C": consultar,
    "-R": reinstalar,
    "-L": limpiar,
}

if geteuid() == 0:
    yellow("ATENCIÓN: No se debe usar KPA con permisos root, los comandos que lo requieran se gestionan internamente.")
    print("Vuelva a ejecutar KPA como usuario no-root.")
    sys.exit(1)

# Verificación de rutas

RUTA = join(xdg_cache_home, "kpa")

if exists(RUTA):
    green("Ruta de KPA encontrada...\n")

else:
    print("Creando ruta para KPA...\n")
    makedirs(RUTA, exist_ok=True)


def main():
    try:
        for arg, funcion in args.items():
            if sys.argv[1] == "-h":
                print("""Argumentos válidos en KPA versión 2.0.0-beta:

    Instalar paquetes:
        -I [PAQUETES]

    Actualizar paquetes:
        -A [PAQUETES]
    Actualizar TODOS los paquetes instalados con KPA:
        -A todo

    Reinstalar paquetes:
        -R [PAQUETES]

    Limpiar paquetes huérfanos y/o paquetes que sean de tipo '-debug':
        -L huerfanos
        -L debug

    Limpiar tanto huérfanos como debug:
        -L huerfanos debug

    Ver esta ayuda: -h

Recuerde crear el archivo kpa.json para configurar kpa correctamente,
vea en https://KevinCrrl.github.io/KevinCrrl/documentacion/kpa.html un
ejemplo de como debería ser el archivo.""")
                break
            if sys.argv[1] == arg:
                for paquete in sys.argv[2:]:
                    funcion(paquete)
                break

        else:
            red("ERROR: No se encontró el argumento ingresado. Use -h para obtener los comandos disponibles.")
    except IndexError:
        red("ERROR: Ingresó una cantidad incorrecta de argumentos.")
    except KeyboardInterrupt:
        yellow("\nSaliendo del programa por interrupción de teclado.")
