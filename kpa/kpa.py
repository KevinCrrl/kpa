# Copyright 2025-2026 - KevinCrrl
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from os import geteuid, makedirs
from os.path import exists

from kpa.colorprints import yellow
from kpa.funciones import RUTA, cli


@cli.callback()
def json_help():
    """
    KevinCrrl Python AUR Helper

    KPA es software libre, puedes redistribuirlo y/o modificarlo bajo los
    términos de la licencia General Public License versión 3 o cualquier
    versión posterior.

    Recuerde crear el archivo kpa.json para configurar kpa correctamente,
    vea en https://KevinCrrl.github.io/KevinCrrl/documentacion/kpa.html un
    ejemplo de como debería ser el archivo."""


def main():
    if geteuid() == 0:
        yellow(
            "ATENCIÓN: No se debe usar KPA con permisos root, los comandos que \
lo requieran se gestionan internamente."
        )
        print("Vuelva a ejecutar KPA como usuario no-root.")
        sys.exit(1)

    # Verificación de rutas

    if not exists(RUTA):
        print("Creando ruta para KPA...\n")
        makedirs(RUTA, exist_ok=True)

    cli()


if __name__ == "__main__":
    main()
