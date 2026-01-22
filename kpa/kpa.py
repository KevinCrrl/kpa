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

from os.path import (
    exists,
    join
)
from os import (
    geteuid,
    makedirs
)
from kpa.colorprints import *
from kpa.funciones import cli
from xdg.BaseDirectory import xdg_cache_home
import sys

if geteuid() == 0:
    yellow("ATENCIÓN: No se debe usar KPA con permisos root, los comandos que lo requieran se gestionan internamente.")
    print("Vuelva a ejecutar KPA como usuario no-root.")
    sys.exit(1)

# Verificación de rutas

RUTA = join(xdg_cache_home, "kpa")

if not exists(RUTA):
    print("Creando ruta para KPA...\n")
    makedirs(RUTA, exist_ok=True)


def main():
    try:
        cli()
    except KeyboardInterrupt:
        yellow("\nSaliendo del programa por interrupción de teclado.")
