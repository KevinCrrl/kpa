# Copyright (C) 2025 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

import subprocess as sb
from kpa.parser import datos


def git_run(comando: list, verbose):
    sb.run(comando, check=True, capture_output=not verbose)


def clone(paquete, verbose=False):
    if datos["clone_branch"]:
        url_repo = f"--branch {paquete} --single-branch {datos['url']} {paquete}"
    else:
        url_repo = f"{datos['url']}/{paquete}.git"

    git_run(["git", "clone"] + url_repo.split(), verbose)


def pull(verbose=False):
    git_run(["git", "fetch", "origin"], verbose)
    git_run(["git", "reset", "--hard", "origin/master"], verbose)
