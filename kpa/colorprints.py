# Copyright (C) 2025 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

from typer import secho, colors


def basic_print(text, color=colors.WHITE):
    secho(text, fg=color)


def red(text):
    basic_print(text, colors.RED)


def yellow(text):
    basic_print(text, colors.YELLOW)


def blue(text):
    basic_print(text, colors.BLUE)


def green(text):
    basic_print(text, colors.GREEN)


def yellow_input(text):
    secho(text, fg=colors.YELLOW)
    return input()
