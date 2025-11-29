# Copyright (C) 2025 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

from colorama import init, Fore

init(autoreset=True)


def red(texto):
    print(Fore.RED + texto)


def yellow(texto):
    print(Fore.YELLOW + texto)


def blue(texto):
    print(Fore.BLUE + texto)


def green(texto):
    print(Fore.GREEN + texto)


def yellow_input(texto):
    return input(Fore.YELLOW + texto)
