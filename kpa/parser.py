# Copyright (C) 2025 KevinCrrl
# Licencia GPL 3 o superior (ver archivo LICENSE)

from xdg.BaseDirectory import xdg_config_home
from os.path import join
import json
from kpa.colorprints import red
import jsonschema
import sys

datos_kpa = {
    "visor": "kpa",  # Visor independiente de KPA
    "proxychains4": False,  # Evitar uso de proxy si no está instalado o configurado
    "root": "sudo",  # La forma más común de acceder a root es sudo, también se usa para no dejar vacío el espacio
    "ignorar": [],  # No ignorar paquetes por defecto
    "eula_detector": True,  # Activado por defecto para mejor seguridad legal
    "url": "https://aur.archlinux.org",  # URL típica del AUR
    "clone_branch": False  # Clonar directamente el repositorio, sin usar ramas como en algunos mirrors del AUR.
}

# Crear copia
datos_usuario = datos_kpa

try:
    with open(join(xdg_config_home, "kpa", "kpa.json"), "r", encoding="utf-8") as cf:
        datos_usuario = json.load(cf)
except FileNotFoundError:
    red("ERROR: Archivo de configuración 'kpa.json' no encontrado.\n")
except json.decoder.JSONDecodeError:
    red("ERROR: No se pudo obtener contenido del archivo 'kpa.json'\n")

# Validacipon extra del archivo JSON usando jsonschema

kpa_schema = {
    "type": "object",
    "properties": {
        "visor": {"type": "string"},
        "proxychains4": {"type": "boolean"},
        "root": {"type": "string"},
        "ignorar": {"type": "array", "items": {"type": "string"}},
        "eula_detector": {"type": "boolean"},
        "url": {"type": "string"},
        "clone_branch": {"type": "boolean"}
    },
    "required": []
}

try:
    jsonschema.validate(datos_usuario, kpa_schema)
except jsonschema.exceptions.ValidationError as e:
    red(f"ERROR: La validación de configuración de KPA encontró un error en tu archivo kpa.json: {e}")
    sys.exit(1)

datos = {}  # Config definitiva que se irá completando

for configuracion, valor in datos_kpa.items():
    try:
        datos[configuracion] = datos_usuario[configuracion]
    except KeyError:
        datos[configuracion] = valor
