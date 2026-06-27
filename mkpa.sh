#!/bin/sh

# Copyright 2026 - KevinCrrl
# SPDX-License-Identifier: GPL-3.0-or-later

# Este script fue diseñado para POSIX sh puro.
# No solo para interpretes modernos.

set -e # Salir en caso de error

# Verificar ruta XDG, si no existe, usar $HOME/.cache
if [ -n "${XDG_CACHE_HOME}" ]; then
    CACHE="${XDG_CACHE_HOME}/kpa"
else
    CACHE="${HOME}/.cache/kpa"
fi

show_help () {
    cat << "EOF"
Mini KPA: Script de instalación y reinstalación de KPA y pkgbuild-parser
MKPA no es un AUR helper como KPA, solo instala KPA por primera vez y lo
reinstala en caso de actualizaciones mayores del sistema que causen problemas.

install: Instala KPA y pkgbuild-parser si no lo están.
fix: Reinstala KPA y pkgbuild-parser en caso de actualización de las rutas del sistema.
help: Muestra este menú de ayuda.

MKPA es software libre, puede redistribuirlo y/o modificarlo bajo los términos de
la licencia GNU General Public License Version 3 o cualquier versión posterior.
EOF
}

show_version() {
    echo "Mini KPA Versión 1.0.0"
    echo "Use mkpa --help para ver las opciones disponibles."
}

pkgbuild () {
    # Función para ir a la carpeta del paquete, mostrar el PKGBUILD
    # y consultar al usuario si desea realizar la construcción
    package=$1

    cd "${package}"
    cat PKGBUILD
    confirm="n"
    printf "\n\e[38;5;11m¿Desea continuar con la construcción? (s/n)\e[38;5;7m "
    read -r confirm

    if [ "${confirm}" = "s" ]; then
        makepkg -sfi --noconfirm
    fi
}

install_kpa() {
    if [ ! -d "${CACHE}" ]; then
        echo "Creando carpeta de caché..."
        mkdir "${CACHE}"
    else
        echo "La carpeta de caché ya existe! No se intentará crearla."
    fi

    cd "${CACHE}"

    # Intentar clonar el paquete, si ya existe una carpeta, se avisa al usuario
    # y se intenta una reinstalación en vez de instalar desde cero.

    git clone https://aur.archlinux.org/python-pkgbuild-parser.git || \
    (echo "python-pkgbuild-parser ya está clonado!" && echo "Realizando reinstalación!" && sleep 2)

    pkgbuild python-pkgbuild-parser

    cd ..

    git clone https://aur.archlinux.org/kpa.git || \
    (echo "KPA ya está clonado!" && echo "Realizando reinstalación!" && sleep 2)

    pkgbuild kpa
}

case "$1" in
    install)
        install_kpa
        ;;
    fix)
        if [ -d "${CACHE}" ]; then
            cd "${CACHE}"
            if [ -d "python-pkgbuild-parser" ] && [ -d "kpa" ]; then
                pkgbuild python-pkgbuild-parser
                cd ..
                pkgbuild kpa
            else
                echo "Las rutas de los programas no existen, no se puede realizar la reinstalación!"
            fi
        else
            echo "La ruta de caché no existe! Posiblemente KPA no está instalado."
            echo "Realizando instalación desde cero..."
            install
        fi
        ;;
    help)
        show_help
        ;;
    version)
        show_version
        ;;
    *)
        echo "Argumento no válido, vea el menú de ayuda:"
        echo
        show_help
        exit 1
esac
