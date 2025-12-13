# KPA: KevinCrrl Python Aur helper

## PKGBUILD disponible en el AUR

[Versión estable en AUR](https://aur.archlinux.org/packages/kpa-bin)

### Documentación para la versión más reciente y estable

[Documentación para la versión Stable](https://kevincrrl.github.io/KevinCrrl/documentacion/kpa.html)

## Pasos para usar en desarrollo

Para escribir código para KPA, primero se debe entender que a partir de la versión 2.0.0 se comporta como un paquete y no como un script simple, por ello se recomienda crear un entorno virtual para usar pip e instalar dependencias sin romper dependencias externas del sistema.

Una vez dentro del entorno, instale lo necesario con el requirements.txt, por ejemplo, usando pip:

```
(entorno) $ pip install -r requirements.txt
```

con eso puede instalar KPA en su entorno en modo editable (que es lo recomendado si se van a realizar cambios en el código y se desea evitar desinstalar y reinstalar el paquete cada vez que se va a probar:

```
(entorno) $ pip install -e .
```

Una vez instalado se puede probar si funciona con:

```
(entorno) $ kpa -h
```

Ahora con KPA instalado en modo editable cada cambio realizado en el código se podrá reflejar en el uso de la cli sin necesidad de reejecutar pip.
