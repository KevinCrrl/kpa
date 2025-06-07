# KPA: KevinCrrl Python AUR helper

This is a simple project to automate the cloning of PKGBUILDs and building from them using the AUR (Arch User Repository), since the classic way of installing packages from the AUR is manual. However, since it is usually a complex process, these programs are created. Nevertheless, a helper can be risky as it executes the PKGBUILD without human intervention. It can also hide outputs or even replace classic tools like makepkg, since there can be malicious commands in the PKGBUILD that can be executed by requesting root permissions from the user. Additionally, it breaks the classic activity of using the native tools of the Arch Linux system.

## Differences of this AUR helper

- kpa automates and shows the output of the native Arch tools, the Linux environment, and version control.

- It has several simple commands:

  -I: Install  
  -A: Update  
  -D: Uninstall  
  -C: Consult information in a browser  
  -R: Reinstall  

You can run `kpa -h` for more information.

- User confirmation: Before using makepkg, the user is shown the PKGBUILD so they can read it and decide within the program's console interface whether to continue or cancel.

- Pure Python: kpa follows a minimalist philosophy; therefore, it does not use AUR databases, unnecessary version control, or configurations unrelated to user freedom. kpa only follows its goal to automate and be useful. That is why it uses its own folders to store cloned AUR repositories, in order to traverse them for updates, verify their existence, and compare PKGBUILDs. It also uses its own lightweight JSON configuration method to give the user freedom on how they want to use their AUR helper without compromising the weight or portability of the program.

- Few dependencies: kpa depends on Python’s standard libraries and the external library `colorama`, which should not be a heavy burden, since Python comes preinstalled in most Linux systems, and `python-colorama` is in Pacman's extra repository. Lastly, for automation, it only uses programs that are part of GNU coreutils that come in every Arch installation (such as `rm`, `mv`, and `cat`, which are used in kpa). It also uses only what is necessary for building AUR packages, i.e., Git and makepkg, which according to the Arch Wiki are already included by default in the Pacman package. Additionally, if the precompiled version is downloaded from the releases section or from the AUR, neither Python nor python-colorama will be needed.

## Example of ~/aur/kpa.json

This file allows KPA to know which programs to use to view and display (or even edit, if an editor is chosen) PKGBUILDs, through the "visor" variable. You can use console viewers like cat or bat, and even editors like nano or vim to customize the PKGBUILD. The "navegador" variable is used to open the AUR package page when using the -C argument. If any of these variables are undefined or the programs are not actually installed, KPA will display a warning. It's important to have this file and edit it correctly, so the following example is provided:

![~/aur/kpa.json file](docs/json.png)

