## Guía para la instalación de Gentoo (Hardened MUSL) // (BTRFS + LUKS + LVM)
*@fraxgut* - *VPL+ACR* - *Guia_InstalarGentoo.md*

#### Descargar un sistema para la instalación
Para la instalación de Gentoo, no es necesario utilizar la imagen del sistema operativo, aunque es una opción válida que se puede descargar desde el sitio web oficial.
Sin embargo, en este caso particular, se sugiere utilizar SystemRescueCD, ya que personalmente lo considero una herramienta confiable y efectiva para el proceso de instalación. Puedes descargarlo desde el siguiente enlace: https://www.system-rescue.org/Download/.
Antes de iniciar el proceso de instalación de Gentoo, es importante decidir qué medio se utilizará para llevar a cabo la instalación del sistema operativo. Dependiendo de las circunstancias, el medio de instalación puede ser un dispositivo externo, como un CD/DVD o un USB, la imagen del sistema descargada directamente o la conexión remota mediante herramientas como SSH.

#### Definir el medio de instalación
El **primer** caso se utiliza cuando se dispone de un equipo físico en el que se instalará el sistema operativo, es decir, cuando el usuario se encuentra en su casa u oficina, o en alguna situación similar. El **segundo** caso se utiliza cuando se trabaja con una máquina virtual, como VirtualBox, VMWare, QEMU, entre otros. Finalmente, el **tercer** caso se utiliza cuando se trabaja de forma remota, como por ejemplo, con un servidor virtual privado. En cualquiera de estos casos, el **sistema anfitrión** será el equipo desde el que se descargará el sistema operativo, mientras que el **sistema invitado** será el equipo en el que se instalará Gentoo.

##### Grabar la imagen en algún dispositivo (caso 1)
Se recomienda utilizar un dispositivo USB en lugar de un CD/DVD. Las siguientes instrucciones están dirigidas a sistemas UNIX (GNU/Linux, BSD, macOS) con GPT/UEFI. Para grabar la imagen en un dispositivo USB, sigue los siguientes pasos:
1. Renombra la imagen descargada a 'SystemRescueCD.iso'.
2. Abre la terminal (salta al paso 6 si utilizas CD/DVD).
3. Navega al directorio donde se encuentra la imagen (por ejemplo: cd Descargas).
4. Identifica el dispositivo USB que utilizarás para grabar la imagen con el comando lsblk (por ejemplo: /dev/sdc).
5. Formatea el dispositivo USB con los siguientes comandos:
	- `sgdisk --zap-all`
	- `sgdisk --clear --new 1:0:0 --typecode=2:8200 --change-name=1:LiveUSB /dev/DISPOSITIVO`
	- `mkfs.fat -F 32 -n LiveUSB /dev/disk/by-partlabel/LiveUSB`
6. Aplica los siguientes comandos:
	- `isohybrid SystemRescueCD.iso`
	- `dd if=SystemRescueCD.iso of=/dev/DISPOSITIVO bs=8192k; sync`
7. Desconecta el dispositivo USB (Nota: se puede utilizar una herramienta como UUI para automatizar todo este proceso o para MBR/BIOS).

*Nota para usuarios de Windows: Se puede utilizar la herramienta Rufus (https://rufus.ie/es/) para realizar una grabación simple en un dispositivo USB. En caso de utilizar un CD/DVD, se deben utilizar las herramientas del sistema.*
Una vez grabada la imagen en el dispositivo USB, conéctalo al sistema invitado e inicia SystemRescueCD.

##### Utilización de una máquina virtual (caso 2)
El proceso es sencillo: descarga la imagen, ingrésala en tu software de virtualización preferido y, simplemente, inicia el sistema.

##### Conexión remota (caso 3)
Si prefieres no realizar el proceso de instalación tú mismo, comunícate con tu proveedor para que pueda insertar la imagen que necesitas en tu sistema. Él se encargará de realizar el caso 1 o caso 2 por ti.

#### Primeros pasos
Los primeros pasos consisten en realizar una conexión a internet exitosa, establecer una contraseña segura para el usuario administrador y asegurar el sistema mediante la configuración de SSH, si es necesario.

SystemRescueCD viene con NetworkManager preinstalado, lo que permite utilizar las herramientas que proporciona este programa. En primer lugar, debes abrir la terminal para comenzar con la instalación, en caso de que el sistema se haya iniciado en un escritorio y no en un terminal virtual. Aquí se realizarán la mayoría de los comandos, en el caso de que no se trabaje con SSH. De todas formas, es fundamental conectarse a internet. Esto es automático en la mayoría de los casos en los que se utiliza una red cableada, no obstante, algunos servidores virtuales requieren una configuración manual.

Para una configuración rápida, utiliza el comando `nmtui`, donde el proceso de configuración debería ser bastante intuitivo. Si es necesario, se pueden especificar manualmente la dirección IP y los servidores DNS.Luego, utiliza el comando `ping 9.9.9.9` para verificar que la conexión a internet haya sido exitosa. 

Es importante cambiar la clave del administrador mediante el comando passwd para evitar conexiones no autorizadas. Se recomienda utilizar un generador de contraseñas o elegir cinco palabras al azar y mezclarlas, siempre utilizando una variación de mayúsculas con minúsculas. También se pueden utilizar números y símbolos para hacer la contraseña más segura. Lo ideal es que la contraseña sea tan robusta como sea posible, siempre y cuando se pueda recordar fácilmente.

Finalmente, si lo deseas, puedes configurar SSH para realizar el proceso de instalación desde otra computadora. Esto es especialmente útil en caso de utilizar una terminal virtual, para poder copiar y pegar los comandos necesarios sin necesidad de introducirlos manualmente. Para esto, utiliza el comando `vim /etc/ssh/sshd_config` (o tu editor de texto preferido, se utilizará vim en esta guía) para editar el documento. Lo interesante aquí es:

- Descomentar el puerto 22 `#Port 22` → `Port 22`
- Descomentar `#ListenAddress` y colocar la dirección IP correspondiente, por ejemplo: `ListenAddress 192.168.5.50`
- Descomentar `#PasswordAuthentication yes` → `PasswordAuthentication yes`

Ahora existen dos alternativas, la primera es cerrar el documento y desactivar IpTables con `systemctl stop iptables`, ya que está en conflicto con SSH. Para mayor seguridad, se pueden realizar configuraciones manuales para filtrar el puerto 22, aunque esto no es necesario en la mayoría de los casos. De todas formas, si se desea, se pueden utilizar los siguientes comandos:

- `LOIF=lo`
- `SSHPORT=22`
- `iptables -A INPUT -i $LOIF -j ACCEPT`
- `iptables -A OUTPUT -o $LOIF -j ACCEPT`
- `iptables -A INPUT -p tcp -m tcp --dport $SSHPORT -j ACCEPT`
- `iptables -A OUTPUT -p tcp --sport $SSHPORT -m state --state ESTABLISHED -j ACCEPT`
- `iptables -P INPUT DROP`
- `iptables -P OUTPUT DROP`

Arregla la fecha con `ntpd -q -g` y luego realiza la conexión a SSH en tu sistema anfitrión con `ssh root@ip`, reemplazando "ip" con tu dirección IP correspondiente.

#### Configuración del disco
A partir de ahora, la guía se centrará en proporcionar los comandos necesarios para realizar la configuración del disco. En primer lugar, es necesario descubrir el nombre del disco donde se instalará el sistema operativo utilizando el comando `lsblk` o `fdisk -l`. Una vez que se ha obtenido el nombre del disco (por ejemplo, /dev/sda), se debe establecer una variable para el disco como `DRIVE=/dev/ndx`, donde ndx es el nombre del disco.

Se debe realizar una limpieza total del disco utilizando los siguientes comandos:
- `cryptsetup open --type plain $DRIVE container --key-file /dev/urandom`
- `dd if=/dev/urandom of=/dev/mapper/container status=progress bs=1M`
- `cryptsetup close container`
- `sgdisk --zap-all $DRIVE`

A continuación, se debe proceder a crear la partición y encriptarla (donde "NOMBRE" es el nombre del sistema anfitrión y "xxx" es el número del disco):
- `sgdisk --clear --new=1:0:+1GiB --typecode=1:ef00 --change-name=1:EFI --new=2:0:0 --typecode=2:8300 --change-name=2:NOMBRE_xxx_sys $DRIVE`
- `cryptsetup --type luks2 --cipher aes-xts-plain64 --hash sha512 --iter-time 5000 --key-size 512 --pbkdf argon2id --use-random --verify-passphrase luksFormat /dev/disk/by-partlabel/NOMBRE_xxx_sys`
- `cryptsetup open /dev/disk/by-partlabel/NOMBRE_xxx_sys root`

Posteriormente, se debe configurar el sistema LVM:
- `pvcreate /dev/mapper/root`
- `vgcreate 1984_vg1 /dev/mapper/root`
- `lvcreate -l +100%FREE NOMBRE_vg1 --name lv1`

Después de crear el sistema LVM, se procede a formatear el disco para tener un sistema de archivos:
- `mkfs.vfat -F 32 -n EFI /dev/disk/by-partlabel/EFI`
- `mkfs.btrfs --force --label BTRFS /dev/mapper/NOMBRE_vg1-lv1`

Una vez que se ha formateado el disco, se deben establecer los subvolúmenes de BTRFS junto con el montaje:
- `o=defaults,x-mount.mkdir`
- `o_btrfs=$o,commit=120,compress=lzo,rw,space_cache,ssd,noatime,nodev,nosuid`
- `o_boot=defaults,nosuid,nodev,noatime,fmask=0022,dmask=0022,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro`
- `mkdir -p /mnt/gentoo`
- `mount -t btrfs LABEL=BTRFS /mnt/gentoo`
- `btrfs subvolume create /mnt/gentoo/@`
- `btrfs subvolume create /mnt/gentoo/@home`
- `btrfs subvolume create /mnt/gentoo/@snapshots`
- `umount -R /mnt/gentoo`
- `mount -t btrfs -o $o_btrfs,subvol=@ LABEL=BTRFS /mnt/gentoo`
- `mkdir /mnt/gentoo/home`
- `mkdir /mnt/gentoo/.snapshots`
- `mkdir /mnt/gentoo/tmp`
- `mkdir -p /mnt/gentoo/boot/efi`
- `mkdir -p /mnt/gentoo/var/cache`
- `mount -t btrfs -o $o_btrfs,subvol=@home LABEL=BTRFS /mnt/gentoo/home`
- `mount -t btrfs -o $o_btrfs,subvol=@snapshots LABEL=BTRFS /mnt/gentoo/.snapshots`
- `mount -o $o_boot LABEL=EFI /mnt/gentoo/boot`
- `btrfs subvolume create /mnt/gentoo/var/tmp`
- `btrfs subvolume create /mnt/gentoo/var/swap`
- `btrfs subvolume create /mnt/gentoo/opt`
- `btrfs subvolume create /mnt/gentoo/srv`
- `chmod 1777 /mnt/gentoo/tmp`
- `chmod 1777 /mnt/gentoo/var/tmp`

Finalmente, creamos el archivo de intercambio "swapfile". Primero hay que definir de que tamaño será el archivo, pues este puede variar sistema a sistema dependiendo de la cantidad RAM. La regla de oro dice "2 x RAM". Sin embargo, se puede tomar la siguiente tabla como referencia:

| Tamaño RAM | Tamaño del "swapfile" (Sin Hibernar) | Tamaño del "swapfile" (Con Hibernar) |
|------------|--------------------------------------|--------------------------------------|
| 256MB      | 256MB                                | 512MB                                |
| 512MB      | 512MB                                | 1GB                                  |
| 1GB        | 1GB                                  | 2GB                                  |
| 2GB        | 1GB                                  | 3GB                                  |
| 3GB        | 2GB                                  | 5GB                                  |
| 4GB        | 2GB                                  | 6GB                                  |
| 6GB        | 2GB                                  | 8GB                                  |
| 8GB        | 3GB                                  | 11GB                                 |
| 12GB       | 3GB                                  | 15GB                                 |
| 16GB       | 4GB                                  | 20GB                                 |
| 24GB       | 5GB                                  | 29GB                                 |
| 32GB       | 6GB                                  | 38GB                                 |
| 64GB       | 8GB                                  | 72GB                                 |
| 128GB      | 11GB                                 | 139GB                                |

Finalmente, una vez definido el tamaño se aplican los siguientes comandos (no olvidar cambiar "CANTIDADGB" por el número correspondiente):
- `truncate -s 0 /mnt/gentoo/var/swap/swapfile`
- `chattr +C /mnt/gentoo/var/swap/swapfile`
- `btrfs property set /mnt/gentoo/var/swap/swapfile compression none`
- `chmod 600 /mnt/gentoo/var/swap/swapfile`
- `dd if=/dev/urandom of=/mnt/gentoo/var/swap/swapfile bs=1G count=CANTIDADGB status=progress`
- `mkswap /var/swap/swapfile`
- `swapon /var/swap/swapfile`
