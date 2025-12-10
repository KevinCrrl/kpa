# Copyright (C) 2025 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

import subprocess as sb
from kpa.parser import datos


def git_run(comando: list):
    sb.run(comando, check=True, capture_output=True)


def clonar(paquete):
    if datos["clone_branch"]:
        url_repo = f"--branch {paquete} --single-branch {datos['url']} {paquete}"
    else:
        url_repo = f"{datos['url']}/{paquete}.git"

    if datos["proxychains4"]:
        git_run(["proxychains4", "git", "clone"] + url_repo.split())
    else:
        git_run(["git", "clone"] + url_repo.split())


def pull():
    if datos["proxychains4"]:
        git_run(["proxychains4", "git", "fetch", "origin"])
    else:
        git_run(["git", "fetch", "origin"])
    git_run(["git", "reset", "--hard", "origin/master"])
