# KPA: KevinCrrl Python Aur helper

Este es un proyecto simple para automatizar la clonación de PKGBUILD y construcción a pertir de ellos usando el AUR (Arch User Repository), ya que la forma clásica de instalar paquetes desde el AUR es de manera manual, sin embargo ya que suele ser un proceso complejo, se crean estos programas, sin embargo, un helper puede ser riesgoso ya que ejecuta el PKGBUILD sin intervención humana, además que puede ocultar las salidas o incluso reemplazar herramientas clásicas como makepkg, pues en los PKGBUILD pueden haber comandos maliciosos que se pueden ejecutar pidiendo permisos root al usuario, además que rompe la actividad clásica de usar las herramientas propias del sistema Arch Linux.

## Diferencias de este AUR helper

- kpa automatiza y muestra las salidas de las herramientas propias de Arch, el entorno Linux y el control de versiones.

- Tiene tres comandos simples: -I, -A, -D, para instalar, actualizar y desinstalar en el orden dado respectivamente, además que puede intentar actualizar todos los paquetes con "-A todo".

- Confirmación del usuario: Antes de usar makepkg, se le muestra al usuario el PKGBUILD para que lo pueda leer y decidir dentro de la interfaz de consola del programa si quiere continuar o cancelar.

- Python puro: kpa sigue una filosofía minimalista, por ello no usa bases de datos del AUR, archivos de versiones en JSON o configuraciones innecesarias, kpa solo sigue su objetivo de automatizar y ser útil, por ello usa sus propias carpetas para almacenar los repositorios del AUR clonados, para poder recorrerlos en actualizaciones, verificar su existencia y comparar PKGBUILDs.

- Sin tantas dependencias: kpa depende de las librerías propias de Python y la libreía externa colorama, lo cual no debe ser un gran peso, ya que Python viene instalado en la mayorpia de sistemas Linux, y python-colorama está en el extra de Pacman, por último para la automatización solo se usan programas que forman parte de las coreutils de GNU que vienen en toda instalación de Arch (como rm, mv y cat, que son usadas en kpa), además se usa solo lo suficiente para la construcción de paquetes del AUR, o sea, Git y makepkg que según la Wiki de Arch ya viene por defecto en el paquete Pacman. Además si se descarga la versión ya compilada desde la zona de releases o desde el AUR, no se necesitará tener ni Python ni python-colorama.

# KPA: KevinCrrl Python AUR helper

This is a simple project to automate cloning and building PKGBUILDs from them using the AUR (Arch User Repository). The classic way to install packages from the AUR is manually. However, since it is usually a complex process, these programs are created. However, a helper can be risky since it executes the PKGBUILD without human intervention. It can also hide the output or even replace classic tools like makepkg. PKGBUILDs can contain malicious commands that can be executed by requesting root permissions from the user. It also breaks the classic process of using the Arch Linux system's own tools.

## Differences of this AUR helper

- kpa automates and displays the output of Arch's own tools, the Linux environment, and version control.

- It has three simple commands: -I, -A, -D, to install, update, and uninstall in the given order, respectively. You can also attempt to update all packages with "-A all."

- User confirmation: Before using makepkg, the user is shown the PKGBUILD so they can read it and decide within the program's console interface whether to continue or cancel.

- Pure Python: kpa follows a minimalist philosophy, so it doesn't use AUR databases, JSON version files, or unnecessary configurations. kpa only pursues its goal of being automated and useful. Therefore, it uses its own folders to store cloned AUR repositories, so it can traverse them during updates, verify their existence, and compare PKGBUILDs.

- Not too many dependencies: kpa depends on Python's own libraries and the external colorama library, which shouldn't be a big burden since Python comes installed on most Linux systems, and python-colorama is in the Pacman extra. Finally, for automation, only programs that are part of the GNU coreutils that come with every Arch installation are used (such as rm, mv, and cat, which are used in kpa). Additionally, it only uses enough for building AUR packages, that is, Git and makepkg, which according to the Arch Wiki is already included by default in the Pacman package. Furthermore, if you download the pre-compiled version from the releases area or from the AUR, you won't need to have either Python or python-colorama.
