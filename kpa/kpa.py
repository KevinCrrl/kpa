"""
    Copyright (C) 2025-2026 KevinCrrl

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

from os.path import exists
from os import geteuid, makedirs
import sys
from kpa.colorprints import yellow
from kpa.funciones import cli, RUTA


@cli.callback()
def json_help():
    """
KevinCrrl Python AUR Helper

KPA es software libre, puedes usarlo y redistribuirlo bajo los
términos de la licencia General Public License versión 3 o
cualquier versión posterior.

Recuerde crear el archivo kpa.json para configurar kpa correctamente,
vea en https://KevinCrrl.github.io/KevinCrrl/documentacion/kpa.html un
ejemplo de como debería ser el archivo."""


def main():
    if geteuid() == 0:
        yellow("ATENCIÓN: No se debe usar KPA con permisos root, los comandos que \
lo requieran se gestionan internamente.")
        print("Vuelva a ejecutar KPA como usuario no-root.")
        sys.exit(1)

    # Verificación de rutas

    if not exists(RUTA):
        print("Creando ruta para KPA...\n")
        makedirs(RUTA, exist_ok=True)

    cli()


if __name__ == "__main__":
    main()
