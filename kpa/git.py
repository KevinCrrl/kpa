# Copyright (C) 2025-2026 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

import subprocess as sb
from kpa.parser import datos
from kpa.colorprints import yellow


def git_run(comando: list[str], verbose: bool):
    sb.run(comando, check=True, shell=False, capture_output=not verbose)


def clone(paquete: str, verbose: bool = False):
    if datos["clone_branch"]:
        url_repo = f"--branch {paquete} --single-branch {datos['url']} {paquete}"
    else:
        url_repo = f"{datos['url']}/{paquete}.git"

    git_run(["git", "clone"] + url_repo.split(), verbose)


def pull(verbose: bool = False, ignore_diff: bool = False) -> str:
    output: str = ""
    git_run(["git", "fetch", "origin"], verbose)
    if not ignore_diff:
        try:
            output = sb.run(["git", "diff", "HEAD", "origin"], check=True,
                            shell=False, capture_output=True, text=True).stdout
        except sb.CalledProcessError as e:
            yellow(f"No se pudo mostrar el diff de la actualización: {e}")
    git_run(["git", "reset", "--hard", "origin"], verbose)
    return output
