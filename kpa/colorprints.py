# Copyright 2025-2026 - KevinCrrl
# SPDX-License-Identifier: GPL-3.0-or-later

from rich.console import Console

# https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
console = Console(emoji=False)


def red(text: str, end: str = "\n"):
    console.print(text, style="bright_red bold", end=end)


def yellow(text: str, end: str = "\n"):
    console.print(text, style="bright_yellow", end=end)


def blue(text: str, end: str = "\n"):
    console.print(text, style="bright_blue", end=end)


def green(text: str, end: str = "\n"):
    console.print(text, style="bright_green", end=end)


def yellow_input(text: str):
    console.print(text + " ", style="bright_yellow", end="")
    return input()
