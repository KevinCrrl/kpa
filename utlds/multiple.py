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
    reinstalar
)

from colorama import (
    init,
    Fore
)

init(autoreset=True)

def multiarg(comando):
    comandos = {
        "instalar": instalar,
        "actualizar": actualizar_arg,
        "desinstalar": desinstalar,
        "reinstalar": reinstalar
    }
    
    print("Ingresa los paquetes a los que quieras aplicar la función seleccionada, ingresa separando solo con espacios entre nombres de paquetes, no separe con guiones o comas.")
    paquetes = input("Nombre de los paquetes: ").split()
    for argumento, funcion in comandos.items():
        if argumento == comando:
            for paquete in paquetes:
                funcion(paquete)
            break

    else:
        print(Fore.RED + "ERROR: Argumento incorrecto, el modo múltiple solo es compatible con los modos 'instalar', 'actualizar', 'desinstalar' y/o 'reinstalar'.")
