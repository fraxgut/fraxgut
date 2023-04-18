### Guía para la instalación de Gentoo (Hardened MUSL) // (BTRFS + LUKS + LVM + LTO + LLVM)
*@fraxgut* - *VPL+ACR* - *Guia_InstalarGentoo.md*

#### Descargar un sistema para la instalación
Para la instalación de Gentoo, no es necesario utilizar la imagen oficial del sistema operativo, aunque es una opción válida que se puede descargar desde su portal.
Personalmente, sugiero utilizar SystemRescueCD, ya que personalmente lo considero una herramienta confiable y efectiva para el proceso de instalación. Puedes descargarlo desde el siguiente enlace: https://www.system-rescue.org/Download/.
Antes de iniciar el proceso de instalación de Gentoo, es importante decidir qué medio se utilizará para llevar a cabo la instalación del sistema operativo. Dependiendo de las circunstancias, el medio de instalación puede ser un dispositivo externo, como un CD/DVD o un USB, la imagen del sistema descargada directamente o la conexión remota mediante herramientas como SSH.

#### Definir el medio de instalación
El **primer** caso se utiliza cuando se dispone de un equipo físico en el que se instalará el sistema operativo, es decir, cuando el usuario se encuentra en su casa u oficina, o en alguna situación similar. El **segundo** caso se utiliza cuando se trabaja con una máquina virtual, como VirtualBox, VMWare, QEMU, entre otros. Finalmente, el **tercer** caso se utiliza cuando se trabaja de forma remota, como por ejemplo, con un servidor virtual privado. En cualquiera de estos casos, el **sistema anfitrión** será el equipo desde el que se descargará el sistema operativo, mientras que el **sistema invitado** será el equipo en el que se instalará Gentoo.

##### Grabar la imagen en algún dispositivo (caso 1)
Se recomienda utilizar un dispositivo USB en lugar de un CD/DVD. Las siguientes instrucciones están dirigidas a sistemas UNIX (GNU/Linux, BSD, macOS) con GPT/UEFI. Para grabar la imagen en un dispositivo USB, sigue los siguientes pasos:
1. Renombra la imagen descargada a 'SystemRescueCD.iso'.
2. Abre la terminal (salta al paso 6 si utilizas CD/DVD).
3. Navega al directorio donde se encuentra la imagen (por ejemplo: cd Descargas).
4. Identifica el dispositivo USB que utilizarás para grabar la imagen con el comando lsblk (por ejemplo: /dev/sdc).
5. Formatea el dispositivo USB con los siguientes comandos (reemplazar "DISPOSITIVO"):
	- `sgdisk --zap-all /dev/DISPOSITIVO`
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
A partir de ahora, la guía se centrará en proporcionar los comandos necesarios para realizar la configuración del disco. En primer lugar, es necesario descubrir el nombre del disco donde se instalará el sistema operativo utilizando el comando `lsblk` o `fdisk -l`. Una vez que se ha obtenido el nombre del disco (por ejemplo, /dev/sda), se debe establecer una variable para el disco como `DRIVE=/dev/ndx`, donde ndx es el nombre del disco. Si se interrumpe la instalación por algún motivo, se puede partir desde "[x]".

Se debe realizar una limpieza total del disco utilizando los siguientes comandos:
- `cryptsetup open --type plain $DRIVE container --key-file /dev/urandom`
- `dd if=/dev/urandom of=/dev/mapper/container status=progress bs=1M`
- `cryptsetup close container`
- `sgdisk --zap-all $DRIVE`

A continuación, se debe proceder a crear la partición y encriptarla (donde "NOMBRE" es el nombre del sistema anfitrión y "xxx" es el número del disco):
- `sgdisk --clear --new=1:0:+1GiB --typecode=1:ef00 --change-name=1:EFI --new=2:0:0 --typecode=2:8300 --change-name=2:NOMBRE_xxx_sys $DRIVE`
- `cryptsetup --type luks2 --cipher aes-xts-plain64 --hash sha512 --iter-time 5000 --key-size 512 --pbkdf argon2id --use-random --verify-passphrase luksFormat /dev/disk/by-partlabel/NOMBRE_xxx_sys`
- `cryptsetup open /dev/disk/by-partlabel/NOMBRE_xxx_sys root` [x]

Posteriormente, se debe configurar el sistema LVM:
- `pvcreate /dev/mapper/root`
- `vgcreate 1984_vg1 /dev/mapper/root`
- `lvcreate -l +100%FREE NOMBRE_vg1 --name lv1`

Después de crear el sistema LVM, se debe formatear el disco para tener un sistema de archivos:
- `mkfs.vfat -F 32 -n EFI /dev/disk/by-partlabel/EFI`
- `mkfs.btrfs --force --label BTRFS /dev/mapper/NOMBRE_vg1-lv1`

Una vez que se ha formateado el disco, se deben establecer los subvolúmenes de BTRFS junto con el montaje:
- `o=defaults,x-mount.mkdir` [x]
- `o_btrfs=$o,commit=120,compress=lzo,rw,space_cache,ssd,noatime,nodev,nosuid` [x]
- `o_boot=defaults,nosuid,nodev,noatime,fmask=0022,dmask=0022,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro` [x]
- `mkdir -p /mnt/gentoo` [x]
- `mount -t btrfs LABEL=BTRFS /mnt/gentoo`
- `btrfs subvolume create /mnt/gentoo/@`
- `btrfs subvolume create /mnt/gentoo/@home`
- `btrfs subvolume create /mnt/gentoo/@snapshots`
- `umount -R /mnt/gentoo`
- `mount -t btrfs -o $o_btrfs,subvol=@ LABEL=BTRFS /mnt/gentoo`[x]
- `mkdir /mnt/gentoo/home`
- `mkdir /mnt/gentoo/.snapshots`
- `mkdir /mnt/gentoo/tmp`
- `mkdir -p /mnt/gentoo/boot/efi`
- `mkdir -p /mnt/gentoo/var/cache`
- `mount -t btrfs -o $o_btrfs,subvol=@home LABEL=BTRFS /mnt/gentoo/home` [x]
- `mount -t btrfs -o $o_btrfs,subvol=@snapshots LABEL=BTRFS /mnt/gentoo/.snapshots` [x]
- `mount -o $o_boot LABEL=EFI /mnt/gentoo/boot` [x]
- `btrfs subvolume create /mnt/gentoo/var/tmp`
- `btrfs subvolume create /mnt/gentoo/var/swap`
- `btrfs subvolume create /mnt/gentoo/opt`
- `btrfs subvolume create /mnt/gentoo/srv`
- `chmod 1777 /mnt/gentoo/tmp`
- `chmod 1777 /mnt/gentoo/var/tmp`

Para crear el archivo de intercambio "swapfile", es necesario definir previamente el tamaño que se requiere, el cual puede variar según la cantidad de RAM instalada en el sistema. La regla general es utilizar "2 veces la cantidad de RAM", pero también puedes usar la siguiente tabla como referencia:

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

Una vez definido el tamaño del archivo, se aplican los siguientes comandos (asegúrate de reemplazar "CANTIDADGB" con el número correspondiente):
- `truncate -s 0 /mnt/gentoo/var/swap/swapfile`
- `chattr +C /mnt/gentoo/var/swap/swapfile`
- `btrfs property set /mnt/gentoo/var/swap/swapfile compression none`
- `chmod 600 /mnt/gentoo/var/swap/swapfile`

Luego, ejecuta **uno** de los siguientes comandos:
1. `dd if=/dev/urandom of=/mnt/gentoo/var/swap/swapfile bs=1G count=CANTIDADGB status=progress`
2. `dd if=/dev/urandom of=/mnt/gentoo/var/swap/swapfile bs=1M count=CANTIDADMB status=progress`

Para activar el archivo de intercambio, ejecuta los siguientes comandos:
- `mkswap -L swapfile /mnt/gentoo/var/swap/swapfile`
- `swapon /mnt/gentoo/var/swap/swapfile` [x]
- `cd /mnt/gentoo` [x]

#### Instalación de Gentoo
##### Descarga de Gentoo
En este paso se determina la versión de Gentoo que se instalará. Si bien esta guía está enfocada en la variante de Hardened MUSL, cualquier versión debería servir. Cabe mencionar que para esta variante, no se establece una zona horaria ni una localización, por lo que no se cubrirán en esta guía. Para comenzar, busca el enlace de la variante que deseas en esta página: https://www.gentoo.org/downloads/. Luego, reemplaza en "GENTOO_LINK" el enlace correspondiente.
- `GENTOO_LINK=https://bouncer.gentoo.org/fetch/root/all/releases/amd64/autobuilds/20230409T163155Z/stage3-amd64-musl-hardened-20230409T163155Z.tar.xz`
- `wget $GENTOO_LINK`

A continuación, asegurémonos de que el archivo sea seguro:
- `wget -O - https://qa-reports.gentoo.org/output/service-keys.gpg | gpg --import`
- `openssl dgst -r -sha512 archivo.tar.xz` *(reemplaza "archivo" con la variante de Gentoo descargada)*
- `openssl dgst -r -whirlpool archivo.tar.xz`

Luego, extrae el archivo:
- `tar xpvf archivo.tar.xz --xattrs-include='*.*' --numeric-owner`
- `rm archivo.tar.xz`

Después, establece los repositorios y traslada la configuración DNS:
- `mkdir --parents /mnt/gentoo/etc/portage/repos.conf`
- `cp /mnt/gentoo/usr/share/portage/config/repos.conf /mnt/gentoo/etc/portage/repos.conf/gentoo.conf`
- `cp --dereference /etc/resolv.conf /mnt/gentoo/etc/`

Monta algunos directorios adicionales:
- `mount -t proc /proc /mnt/gentoo/proc` [x]
- `mount -R /sys /mnt/gentoo/sys` [x]
- `mount --make-rslave /mnt/gentoo/sys` [x]
- `mount -R /dev /mnt/gentoo/dev` [x]
- `mount --make-rslave /mnt/gentoo/dev` [x]
- `mount -B /run /mnt/gentoo/run` [x]
- `mount --make-slave /mnt/gentoo/run` [x]
- `test -L /dev/shm && rm /dev/shm && mkdir /dev/shm` [x]
- `mount -t tmpfs -o nosuid,nodev,noexec shm /dev/shm` [x]
- `chmod 1777 /dev/shm /run/shm` [x] *(si /run/shm no existe, no es ningún problema)*

Es importante revisar el archivo "make.conf" para configurar algunas variables básicas. Este archivo se puede modificar posteriormente según sea necesario. Por ahora, solo es necesario hacer algunos cambios básicos. Abre el archivo "make.conf" con vim (modifica la variable "NTHREADS" a gusto):
- `vim /mnt/gentoo/etc/portage/make.conf`

```
# DEFAULT VARIABLES
# Compilation
#COMMON_FLAGS="-O2 -pipe"
#CFLAGS="${COMMON_FLAGS}"
#CXXFLAGS="${COMMON_FLAGS}"
#FCFLAGS="${COMMON_FLAGS}"
#FFLAGS="${COMMON_FLAGS}"
#CHOST="x86_64-gentoo-linux-musl"

# Language
#LC_MESSAGES=C

# CUSTOM VARIABLES
# Compilation
NTHREADS="${nproc}"
COMMON_FLAGS="-march=native -O2 -pipe"
CFLAGS="${COMMON_FLAGS}"
CXXFLAGS="${COMMON_FLAGS}"
FCFLAGS="${COMMON_FLAGS}"
FFLAGS="${COMMON_FLAGS}"
CHOST="x86_64-gentoo-linux-musl"
MAKEOPTS="-j${NTHREADS}"
EMERGE_DEFAULT_OPTS="--jobs ${NTHREADS} --load-average ${NTHREADS}"
#PORTAGE_SCHEDULING_POLICY="idle"
PORTAGE_NICENESS="19"
PORTAGE_IONICE_COMMAND="/usr/local/bin/io-priority \${PID}"

# Language
LC_MESSAGES=C
```

Hay que crear el archivo "io-priority" con `vim /mnt/gentoo/usr/local/bin/io-priority`:
```
#!/bin/bash
PID=${1}
ionice -c 3 -p ${PID}
chrt -p -i 0 ${PID}
```

Finalmente, ejecutamos `chmod +x /usr/local/bin/io-priority` para poder ejecutar la secuencia.

##### Entrando a Gentoo
Para entrar al sistema operativo Gentoo, ejecuta los siguientes comandos:
- `chroot /mnt/gentoo /bin/bash` [x]
- `source /etc/profile` [x]
- `export PS1="(chroot) ${PS1}"` [x]

Luego, debes sincronizar los paquetes para el gestor "Portage" y establecer el repositorio de musl. Pero primero, debes elegir un servidor y asegurarte de que el perfil correcto esté seleccionado:
- `emerge-webrsync`
- `emerge --sync`
- `eselect profile list`
- `eselect profile set --force "x"` *(reemplaza x con el perfil de Hardened MUSL, o el de tu elección)*
- `emerge app-eselect/eselect-repository dev-vcs/git app-portage/mirrorselect app-portage/cpuid2cpuflags`
- `eselect repository enable musl`
- `mirrorselect -i -o >> /etc/portage/make.conf` *(selecciona los servidores que más te acomoden)*
- `emerge --sync`
- `emerge -uvDN @world`
- `emerge --depclean`
- `emerge app-editors/neovim` *(opcional: se puede seguir usando nano)*

En este punto, se puede realizar una revisión del archivo /etc/portage/make.conf, si se desea. Es importante fijar las banderas USE necesarias para tu dispositivo. El documento que se mostrará a continuación es solo un ejemplo en particular y no debe ser imitado en su totalidad. Para obtener más información, visita la página https://wiki.gentoo.org/wiki//etc/portage/make.conf para posibles cambios. A continuación se presentan los comandos para este sistema en particular:
- `echo "CPU_FLAGS_X86="$(cpuid2cpuflags)"" >> /etc/portage/make.conf`
- `vim /etc/portage/make.conf`
```
PLACEHOLDER
```

#### Enlaces de interés
https://wiki.gentoo.org/wiki/Handbook:AMD64/Full/Installation
https://wiki.gentoo.org/wiki/Project:Musl
https://leo3418.github.io/collections/gentoo-config-luks2-grub-systemd/packages.html
https://github.com/InBetweenNames/gentooLTO
https://github.com/clang-musl-overlay/clang-musl-overlay

