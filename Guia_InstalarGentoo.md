## Guía para la instalación de Gentoo (BTRFS + LUKS)
*@fraxgut* - *VPL+ACR* - *Guia_InstalarGentoo.md*
#### Descargar un sistema para la instalación
Para la instalación de Gentoo, no es necesario utilizar la imagen del sistema operativo, aunque es una opción válida que se puede descargar desde el sitio web oficial.
Sin embargo, en este caso particular, se sugiere utilizar SystemRescueCD, ya que personalmente lo considero una herramienta confiable y efectiva para el proceso de instalación. Puedes descargarlo desde el siguiente enlace: https://www.system-rescue.org/Download/.
Antes de iniciar el proceso de instalación de Gentoo, es importante decidir qué medio se utilizará para llevar a cabo la instalación del sistema operativo. Dependiendo de las circunstancias, el medio de instalación puede ser un dispositivo externo, como un CD/DVD o un USB, la imagen del sistema descargada directamente o la conexión remota mediante herramientas como SSH.
#### Definir el medio de instalación
El primer caso se utiliza cuando se dispone de un equipo físico en el que se instalará el sistema operativo, es decir, cuando el usuario se encuentra en su casa u oficina, o en alguna situación similar. El segundo caso se utiliza cuando se trabaja con una máquina virtual, como VirtualBox, VMWare, QEMU, entre otros. Finalmente, el tercer caso se utiliza cuando se trabaja de forma remota, como por ejemplo, con un servidor virtual privado. En cualquiera de estos casos, el sistema anfitrión será el equipo desde el que se descargará el sistema operativo, mientras que el sistema invitado será el equipo en el que se instalará Gentoo.
##### Grabar la imagen en algún dispositivo (caso 1)
Se recomienda utilizar un dispositivo USB en lugar de un CD/DVD. Las siguientes instrucciones están dirigidas a sistemas UNIX (GNU/Linux, BSD, macOS) con GPT/UEFI. Para grabar la imagen en un dispositivo USB, sigue los siguientes pasos:
Renombra la imagen descargada a 'SystemRescueCD.iso'.
Abre la terminal (salta al paso 6 si utilizas CD/DVD).
Navega al directorio donde se encuentra la imagen (por ejemplo: cd Descargas).
Identifica el dispositivo USB que utilizarás para grabar la imagen con el comando lsblk (por ejemplo: /dev/sdc).
Formatea el dispositivo USB con los siguientes comandos:
- `sgdisk --zap-all`
- `sgdisk --clear --new 1:0:0 --typecode=2:8200 --change-name=1:LiveUSB /dev/DISPOSITIVO`
- `mkfs.fat -F 32 -n LiveUSB /dev/disk/by-partlabel/LiveUSB`
Aplica los siguientes comandos:
- `isohybrid SystemRescueCD.iso`
- `dd if=SystemRescueCD.iso of=/dev/DISPOSITIVO bs=8192k; sync`
Desconecta el dispositivo USB (Nota: se puede utilizar una herramienta como UUI para automatizar todo este proceso o para MBR/BIOS).
Nota para usuarios de Windows: Se puede utilizar la herramienta Rufus (https://rufus.ie/es/) para realizar una grabación simple en un dispositivo USB. En caso de utilizar un CD/DVD, se deben utilizar las herramientas del sistema.
Una vez grabada la imagen en el dispositivo USB, conéctalo al sistema invitado e inicia SystemRescueCD.
##### Utilización de una máquina virtual (caso 2)
El proceso es sencillo: descarga la imagen, ingrésala en tu software de virtualización preferido y, simplemente, inicia el sistema.
##### Conexión remota (caso 3)
Si prefieres no realizar el proceso de instalación tú mismo, comunícate con tu proveedor para que pueda insertar la imagen que necesitas en tu sistema. Él se encargará de realizar el caso 1 o caso 2 por ti.
