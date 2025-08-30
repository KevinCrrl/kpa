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

from xdg.BaseDirectory import xdg_config_home
from os.path import join
import json
from colorama import init, Fore
import jsonschema
import sys

init(autoreset=True)

datos_kpa = {
    "visor": "kpa",  # Visor independiente de KPA
    "torsocks": False,  # Evitar uso de Tor si no está instalado o configurado
    "navegador": "firefox",  # Uno de los navegadores más usados en Linux, sin embargo, está opción es para no dejar vacío el espacio de configuración
    "root": "sudo",  # La forma más común de acceder a root es sudo, también se usa para no dejar vacío el espacio
    "ignorar": [],  # No ignorar paquetes por defecto
    "eula_detector": True  # Activado por defecto para mejor seguridad legal
}

# Crear copia

datos_usuario = datos_kpa

try:
    with open(join(xdg_config_home, "kpa", "kpa.json"), "r", encoding="utf-8") as cf:
        datos_usuario = json.load(cf)
except FileNotFoundError:
    print(Fore.RED + "ERROR: Archivo de configuración 'kpa.json' no encontrado.\n")
except json.decoder.JSONDecodeError:
    print(Fore.RED + "ERROR: No se pudo obtener contenido del archivo 'kpa.json'\n")

# Validacipon extra del archivo JSON usando jsonschema

kpa_schema = {
    "type": "object",
    "properties": {
        "visor": {"type": "string"},
        "torsocks": {"type": "boolean"},
        "navegador": {"type": "string"},
        "root": {"type": "string"},
        "ignorar": {"type": "array", "items": {"type": "string"}},
        "eula_detector": {"type": "boolean"}
    },
    "required": []
}

try:
    jsonschema.validate(datos_usuario, kpa_schema)
except jsonschema.exceptions.ValidationError as e:
    print(Fore.RED + f"ERROR: La validación de configuración de KPA encontró un error en tu archivo kpa.json: {e}")
    sys.exit(1)

datos = {}  # Config definitiva que se irá completando

for configuracion, valor in datos_kpa.items():
    try:
        datos[configuracion] = datos_usuario[configuracion]
    except KeyError:
        datos[configuracion] = valor
