"""
Verified setup commands for Arch Linux packages, sourced from official docs.
These take HIGHEST PRIORITY over AI-generated env_steps.

Sources:
  - Arch Wiki:   https://wiki.archlinux.org/
  - Official docs linked per section
"""

KNOWN_STEPS: dict[str, list[str]] = {

    # ══ SPICETIFY ════════════════════════════════════════════════════════════
    # https://spicetify.app/docs/advanced-usage/installation/#arch-linux
    "spicetify-cli": [
        "sudo chmod a+wr /opt/spotify",
        "sudo chmod a+wr /opt/spotify/Apps -R",
        "curl -fsSL https://raw.githubusercontent.com/spicetify/marketplace/main/resources/install.sh | sh",
    ],
    "spicetify": [
        "sudo chmod a+wr /opt/spotify",
        "sudo chmod a+wr /opt/spotify/Apps -R",
        "curl -fsSL https://raw.githubusercontent.com/spicetify/marketplace/main/resources/install.sh | sh",
    ],

    # ══ DOCKER ═══════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Docker
    "docker": [
        "sudo systemctl enable --now docker",
        "sudo usermod -aG docker $USER",
        'echo "Log out and back in for the group change to take effect."',
    ],
    "docker-compose": [],  # No extra steps; uses docker daemon

    # ══ QEMU / KVM ═══════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/QEMU
    "qemu-full": [
        "sudo modprobe kvm",
        "sudo usermod -aG kvm,libvirt $USER",
        "sudo systemctl enable --now libvirtd",
        "sudo virsh net-autostart default",
        "sudo virsh net-start default",
    ],
    "qemu-desktop": [
        "sudo modprobe kvm",
        "sudo usermod -aG kvm,libvirt $USER",
        "sudo systemctl enable --now libvirtd",
        "sudo virsh net-autostart default",
    ],
    "libvirt": [
        "sudo systemctl enable --now libvirtd",
        "sudo usermod -aG libvirt $USER",
    ],
    "virt-manager": [],

    # ══ VIRTUALBOX ════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/VirtualBox
    "virtualbox": [
        "sudo modprobe vboxdrv",
        "sudo usermod -aG vboxusers $USER",
    ],
    "virtualbox-host-modules-arch": [
        "sudo modprobe vboxdrv",
    ],

    # ══ NETWORKING ════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/NetworkManager
    "networkmanager": [
        "sudo systemctl enable --now NetworkManager",
    ],
    "iwd": [
        "sudo systemctl enable --now iwd",
    ],
    # https://wiki.archlinux.org/title/WireGuard
    "wireguard-tools": [
        "sudo modprobe wireguard",
    ],
    # https://wiki.archlinux.org/title/OpenVPN
    "openvpn": [
        "sudo systemctl enable --now openvpn-client@<config-name>",
    ],

    # ══ FIREWALL ══════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Uncomplicated_Firewall
    "ufw": [
        "sudo systemctl enable --now ufw",
        "sudo ufw default deny incoming",
        "sudo ufw default allow outgoing",
        "sudo ufw allow ssh",
        "sudo ufw enable",
    ],
    # https://wiki.archlinux.org/title/Nftables
    "nftables": [
        "sudo systemctl enable --now nftables",
    ],
    # https://wiki.archlinux.org/title/Fail2ban
    "fail2ban": [
        "sudo systemctl enable --now fail2ban",
    ],

    # ══ SSH ═══════════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/OpenSSH
    "openssh": [
        "sudo systemctl enable --now sshd",
    ],

    # ══ AUDIO ═════════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/PipeWire
    "pipewire": [
        "systemctl --user enable --now pipewire pipewire-pulse wireplumber",
    ],
    "pipewire-pulse": [
        "systemctl --user enable --now pipewire pipewire-pulse wireplumber",
    ],
    "wireplumber": [
        "systemctl --user enable --now wireplumber",
    ],
    # https://wiki.archlinux.org/title/PulseAudio
    "pulseaudio": [
        "systemctl --user enable --now pulseaudio",
    ],
    # https://wiki.archlinux.org/title/JACK_Audio_Connection_Kit
    "jack2": [
        "sudo usermod -aG audio $USER",
    ],
    "realtime-privileges": [
        "sudo usermod -aG realtime $USER",
    ],
    # EasyEffects — no mandatory post-install steps
    "easyeffects": [],

    # ══ BLUETOOTH ════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Bluetooth
    "bluez": [
        "sudo systemctl enable --now bluetooth",
    ],
    "bluez-utils": [
        "sudo systemctl enable --now bluetooth",
    ],

    # ══ PRINTING ════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/CUPS
    "cups": [
        "sudo systemctl enable --now cups",
        "sudo usermod -aG lp $USER",
    ],
    "cups-pdf": [],

    # ══ DATABASES ════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/PostgreSQL
    "postgresql": [
        "sudo -u postgres initdb --locale=en_US.UTF-8 -D /var/lib/postgres/data",
        "sudo systemctl enable --now postgresql",
    ],
    # https://wiki.archlinux.org/title/MariaDB
    "mariadb": [
        "sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql",
        "sudo systemctl enable --now mariadb",
        "sudo mysql_secure_installation",
    ],
    # https://wiki.archlinux.org/title/MySQL
    "mysql": [
        "sudo mysqld --initialize --user=mysql",
        "sudo systemctl enable --now mysqld",
    ],
    # https://wiki.archlinux.org/title/Redis
    "redis": [
        "sudo systemctl enable --now redis",
    ],
    # https://wiki.archlinux.org/title/MongoDB
    "mongodb": [
        "sudo systemctl enable --now mongodb",
    ],
    "mongodb-bin": [
        "sudo systemctl enable --now mongodb",
    ],
    # https://wiki.archlinux.org/title/Memcached
    "memcached": [
        "sudo systemctl enable --now memcached",
    ],

    # ══ WEB SERVERS ═══════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Nginx
    "nginx": [
        "sudo systemctl enable --now nginx",
    ],
    "nginx-mainline": [
        "sudo systemctl enable --now nginx",
    ],
    # https://wiki.archlinux.org/title/Apache_HTTP_Server
    "apache": [
        "sudo systemctl enable --now httpd",
    ],
    # https://caddyserver.com/docs/install#arch-linux
    "caddy": [
        "sudo systemctl enable --now caddy",
    ],

    # ══ DEVELOPMENT ENVIRONMENT ═══════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Pyenv
    "pyenv": [
        'echo \'export PYENV_ROOT="$HOME/.pyenv"\' >> ~/.bashrc',
        'echo \'[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"\' >> ~/.bashrc',
        'echo \'eval "$(pyenv init -)"\' >> ~/.bashrc',
        "source ~/.bashrc",
    ],
    # https://wiki.archlinux.org/title/Node.js
    "nvm": [
        'echo \'source /usr/share/nvm/init-nvm.sh\' >> ~/.bashrc',
        "source ~/.bashrc",
    ],
    # https://www.rust-lang.org/tools/install
    "rust": [],  # rustup manages PATH automatically
    "rustup": [
        "rustup default stable",
    ],
    # https://wiki.archlinux.org/title/Go
    "go": [
        'echo \'export GOPATH="$HOME/go"\' >> ~/.bashrc',
        'echo \'export PATH="$PATH:$GOPATH/bin"\' >> ~/.bashrc',
        "source ~/.bashrc",
    ],
    # https://wiki.archlinux.org/title/Java
    "jdk-openjdk": [
        "sudo archlinux-java set java-21-openjdk",
    ],
    "jre-openjdk": [
        "sudo archlinux-java set java-21-openjdk",
    ],
    "jdk17-openjdk": [
        "sudo archlinux-java set java-17-openjdk",
    ],
    "jdk11-openjdk": [
        "sudo archlinux-java set java-11-openjdk",
    ],
    "jdk8-openjdk": [
        "sudo archlinux-java set java-8-openjdk",
    ],
    # https://wiki.archlinux.org/title/Ruby#RVM
    "rvm": [
        "source /etc/profile.d/rvm.sh",
        "rvm install ruby --default",
    ],
    # https://wiki.archlinux.org/title/PHP
    "php": [
        "sudo systemctl enable --now php-fpm",
    ],
    "composer": [],

    # ══ VERSION CONTROL ═══════════════════════════════════════════════════════
    "git": [],  # No post-install steps; git config is personal
    "git-lfs": [
        "git lfs install",
    ],

    # ══ FLATPAK ═══════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Flatpak
    "flatpak": [
        "flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo",
    ],

    # ══ GAMING ════════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Steam
    "steam": [],
    # https://wiki.archlinux.org/title/GameMode
    "gamemode": [
        "sudo usermod -aG gamemode $USER",
    ],
    # https://wiki.archlinux.org/title/Wine
    "wine": [
        "sudo pacman -S --needed wine-gecko wine-mono",
    ],
    "proton-ge-custom": [],
    # https://wiki.archlinux.org/title/Lutris
    "lutris": [],

    # ══ GPU DRIVERS ═══════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/NVIDIA
    "nvidia": [
        "sudo mkinitcpio -P",
        'echo "Reboot required for NVIDIA driver to load."',
    ],
    "nvidia-open": [
        "sudo mkinitcpio -P",
        'echo "Reboot required for NVIDIA driver to load."',
    ],
    # https://wiki.archlinux.org/title/AMDGPU
    "xf86-video-amdgpu": [],
    "mesa": [],
    "vulkan-radeon": [],
    "vulkan-intel": [],

    # ══ DISPLAY / WAYLAND ════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Sway
    "sway": [],
    # https://wiki.archlinux.org/title/Hyprland
    "hyprland": [],
    # https://wiki.archlinux.org/title/Xorg
    "xorg-server": [],
    "xorg-xinit": [],
    # https://wiki.archlinux.org/title/GNOME
    "gnome": [
        "sudo systemctl enable gdm",
    ],
    # https://wiki.archlinux.org/title/KDE
    "plasma": [
        "sudo systemctl enable sddm",
    ],

    # ══ POWER MANAGEMENT ══════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/TLP
    "tlp": [
        "sudo systemctl enable --now tlp",
        "sudo systemctl mask systemd-rfkill.service systemd-rfkill.socket",
    ],
    # https://wiki.archlinux.org/title/Power_management#Suspend_and_hibernate
    "acpid": [
        "sudo systemctl enable --now acpid",
    ],
    "thermald": [
        "sudo systemctl enable --now thermald",
    ],

    # ══ SYSTEM TOOLS ═════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Avahi
    "avahi": [
        "sudo systemctl enable --now avahi-daemon",
    ],
    # https://wiki.archlinux.org/title/Cron
    "cronie": [
        "sudo systemctl enable --now cronie",
    ],
    # https://wiki.archlinux.org/title/NTP
    "ntp": [
        "sudo systemctl enable --now ntpd",
    ],
    "systemd-timesyncd": [
        "sudo systemctl enable --now systemd-timesyncd",
        "sudo timedatectl set-ntp true",
    ],
    # https://wiki.archlinux.org/title/Fwupd
    "fwupd": [
        "sudo fwupdmgr refresh",
        "sudo fwupdmgr update",
    ],
    # https://wiki.archlinux.org/title/Smartmontools
    "smartmontools": [
        "sudo systemctl enable --now smartd",
    ],

    # ══ CONTAINERS / ORCHESTRATION ════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Podman
    "podman": [
        "sudo usermod -aG podman $USER",
    ],
    # https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/
    "kubectl": [],
    "minikube": [
        "minikube start --driver=docker",
    ],

    # ══ PACKAGE MANAGERS / RUNTIMES ═══════════════════════════════════════════
    "pip": [],
    "npm": [],
    "nodejs": [],
    "yarn": [],
    "pnpm": [],
    "bun-bin": [],
    "deno": [],

    # ══ MEDIA ═════════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Music_Player_Daemon
    "mpd": [
        "mkdir -p ~/.config/mpd ~/.local/share/mpd",
        "touch ~/.local/share/mpd/database",
        "systemctl --user enable --now mpd",
    ],
    # https://wiki.archlinux.org/title/Jellyfin
    "jellyfin": [
        "sudo systemctl enable --now jellyfin",
    ],
    "plex-media-server": [
        "sudo systemctl enable --now plexmediaserver",
    ],

    # ══ CLOUD CLI TOOLS ═══════════════════════════════════════════════════════
    "aws-cli": [],  # Configure with: aws configure (personal, skip)
    "google-cloud-cli": [
        "gcloud init",
    ],
    "azure-cli": [
        "az login",
    ],
    "terraform": [],
    "ansible": [],

    # ══ SECURITY ═════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/GnuPG
    "gnupg": [],
    # https://wiki.archlinux.org/title/Pass
    "pass": [],
    # https://wiki.archlinux.org/title/KeePass
    "keepassxc": [],
    # https://wiki.archlinux.org/title/ClamAV
    "clamav": [
        "sudo freshclam",
        "sudo systemctl enable --now clamav-freshclam",
    ],
    # https://wiki.archlinux.org/title/AppArmor
    "apparmor": [
        "sudo systemctl enable --now apparmor",
    ],

    # ══ MONITORING ════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Prometheus
    "prometheus": [
        "sudo systemctl enable --now prometheus",
    ],
    "grafana": [
        "sudo systemctl enable --now grafana",
    ],
    "node_exporter": [
        "sudo systemctl enable --now node_exporter",
    ],

    # ══ FONTS & INPUT ═════════════════════════════════════════════════════════
    "ibus": [
        'echo \'export GTK_IM_MODULE=ibus\' >> ~/.bashrc',
        'echo \'export QT_IM_MODULE=ibus\' >> ~/.bashrc',
        'echo \'export XMODIFIERS=@im=ibus\' >> ~/.bashrc',
        "ibus-daemon -drx &",
    ],
    "fcitx5": [
        'echo \'export GTK_IM_MODULE=fcitx\' >> ~/.bashrc',
        'echo \'export QT_IM_MODULE=fcitx\' >> ~/.bashrc',
        'echo \'export XMODIFIERS=@im=fcitx\' >> ~/.bashrc',
    ],

    # ══ CLI TOOLS (no post-install steps needed) ══════════════════════════════
    "fzf": [],
    "ripgrep": [],
    "fd": [],
    "bat": [],
    "eza": [],
    "zoxide": [
        'echo \'eval "$(zoxide init bash)"\' >> ~/.bashrc',
    ],
    "starship": [
        'echo \'eval "$(starship init bash)"\' >> ~/.bashrc',
    ],
    "atuin": [
        'echo \'eval "$(atuin init bash)"\' >> ~/.bashrc',
    ],
    "zsh": [
        "chsh -s $(which zsh)",
    ],
    "fish": [
        "chsh -s $(which fish)",
    ],
    "neovim": [],
    "tmux": [],
    "zellij": [],

    # ══ VERCEL / NPM GLOBALS ══════════════════════════════════════════════════
    "vercel": [
        "npm install -g vercel",
    ],

    # ══ LANGUAGE SERVERS & EDITORS ════════════════════════════════════════════
    "code": [],             # VS Code — runs as-is
    "vscodium": [],
    "neovim": [],
    "helix": [],
    "emacs": [],
    "vim": [],
    "micro": [],
    "lite-xl": [],
    "lapce": [],
    "kakoune": [],

    # ══ BUILD TOOLS ═══════════════════════════════════════════════════════════
    "cmake": [],
    "ninja": [],
    "meson": [],
    "make": [],
    "gcc": [],
    "clang": [],
    "llvm": [],
    "base-devel": [],

    # ══ PYTHON ECOSYSTEM ══════════════════════════════════════════════════════
    "python": [],
    "python-pip": [],
    "python-pipx": [],
    "python-virtualenv": [],
    "uv": [],                # Astral's fast Python package manager
    "python-poetry": [],
    "jupyter": [],
    "ipython": [],

    # ══ MACHINE LEARNING / DATA SCIENCE ═══════════════════════════════════════
    # https://wiki.archlinux.org/title/GPGPU#CUDA
    "cuda": [
        "sudo modprobe nvidia_uvm",
        'echo "nvidia_uvm" | sudo tee /etc/modules-load.d/nvidia.conf',
    ],
    "cudnn": [],
    "python-pytorch-cuda": [],
    "python-tensorflow": [],
    "python-numpy": [],
    "python-pandas": [],
    "ollama": [
        "sudo systemctl enable --now ollama",
    ],

    # ══ MESSAGING / COMMUNICATION ════════════════════════════════════════════
    "telegram-desktop": [],
    "discord": [],
    "signal-desktop": [],
    "slack-desktop": [],
    "element-desktop": [],
    "thunderbird": [],
    "mutt": [],
    "neomutt": [],

    # ══ BROWSERS ══════════════════════════════════════════════════════════════
    "firefox": [],
    "chromium": [],
    "google-chrome": [],
    "brave-bin": [],
    "librewolf-bin": [],
    "vivaldi": [],
    "qutebrowser": [],

    # ══ TORRENT / P2P ══════════════════════════════════════════════════════════
    "transmission-cli": [
        "sudo systemctl enable --now transmission",
    ],
    "transmission-gtk": [],
    "qbittorrent": [],
    "deluge": [],

    # ══ VPN ═══════════════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Mullvad
    "mullvad-vpn": [
        "sudo systemctl enable --now mullvad-daemon",
    ],
    "nordvpn-bin": [
        "sudo systemctl enable --now nordvpnd",
        "sudo usermod -aG nordvpn $USER",
    ],
    "protonvpn": [],
    # https://wiki.archlinux.org/title/OpenConnect
    "openconnect": [],
    # https://wiki.archlinux.org/title/StrongSwan
    "strongswan": [
        "sudo systemctl enable --now strongswan",
    ],

    # ══ FILE SYNC / BACKUP ════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Syncthing
    "syncthing": [
        "systemctl --user enable --now syncthing",
    ],
    # https://wiki.archlinux.org/title/Restic
    "restic": [],
    # https://wiki.archlinux.org/title/BorgBackup
    "borg": [],
    "borgmatic": [
        "sudo systemctl enable --now borgmatic.timer",
    ],
    # https://wiki.archlinux.org/title/Rclone
    "rclone": [],
    "rsync": [],
    "timeshift": [
        "sudo systemctl enable --now cronie",
    ],

    # ══ DISPLAY MANAGERS ══════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/GDM
    "gdm": [
        "sudo systemctl enable gdm",
    ],
    # https://wiki.archlinux.org/title/SDDM
    "sddm": [
        "sudo systemctl enable sddm",
    ],
    # https://wiki.archlinux.org/title/LightDM
    "lightdm": [
        "sudo systemctl enable lightdm",
    ],
    "lightdm-gtk-greeter": [],
    # https://wiki.archlinux.org/title/Ly
    "ly": [
        "sudo systemctl enable ly",
    ],
    # greetd
    "greetd": [
        "sudo systemctl enable greetd",
    ],
    "tuigreet": [],

    # ══ DESKTOP ENVIRONMENTS ══════════════════════════════════════════════════
    "xfce4": [],
    "lxde": [],
    "lxqt": [],
    "mate": [],
    "cinnamon": [],
    "budgie-desktop": [],
    "deepin": [],
    "pantheon": [],
    "gnome-shell": [],
    "plasma-meta": [
        "sudo systemctl enable sddm",
    ],

    # ══ COMPOSITOR / WM ═══════════════════════════════════════════════════════
    "i3-wm": [],
    "i3-gaps": [],
    "openbox": [],
    "bspwm": [],
    "dwm": [],
    "qtile": [],
    "awesome": [],
    "xmonad": [],
    "river": [],
    "wayfire": [],
    "niri": [],

    # ══ WAYLAND UTILITIES ═════════════════════════════════════════════════════
    "xdg-desktop-portal-hyprland": [],
    "xdg-desktop-portal-wlr": [],
    "xdg-desktop-portal-gtk": [],
    "waybar": [],
    "eww": [],
    "ags": [],
    "wofi": [],
    "rofi-wayland": [],
    "rofi": [],
    "dunst": [],
    "mako": [],
    "swww": [],
    "swaybg": [],
    "swaylock": [],
    "swayidle": [],
    "wlogout": [],
    "hyprlock": [],
    "hypridle": [],
    "hyprpaper": [],
    "grim": [],
    "slurp": [],
    "wl-clipboard": [],
    "cliphist": [],
    "kanshi": [],

    # ══ TERMINAL EMULATORS ════════════════════════════════════════════════════
    "kitty": [],
    "alacritty": [],
    "wezterm": [],
    "foot": [],
    "ghostty": [],
    "contour": [],
    "rio": [],
    "st": [],
    "urxvt": [],
    "xterm": [],

    # ══ FILE MANAGERS ═════════════════════════════════════════════════════════
    "yazi": [],
    "ranger": [],
    "lf": [],
    "nnn": [],
    "thunar": [],
    "nautilus": [],
    "dolphin": [],
    "pcmanfm": [],
    "nemo": [],

    # ══ MEDIA PLAYERS ═════════════════════════════════════════════════════════
    "mpv": [],
    "vlc": [],
    "celluloid": [],
    "rhythmbox": [],
    "strawberry": [],
    "cmus": [],
    "ncmpcpp": [],
    "moc": [],

    # ══ IMAGE / GRAPHICS ══════════════════════════════════════════════════════
    "gimp": [],
    "inkscape": [],
    "krita": [],
    "blender": [],
    "darktable": [],
    "rawtherapee": [],
    "feh": [],
    "imv": [],
    "sxiv": [],
    "nsxiv": [],
    "eog": [],
    "gwenview": [],

    # ══ OFFICE ════════════════════════════════════════════════════════════════
    "libreoffice-fresh": [],
    "libreoffice-still": [],
    "onlyoffice-bin": [],
    "obsidian": [],
    "logseq-desktop-bin": [],
    "zotero-bin": [],

    # ══ PASSWORD MANAGERS ═════════════════════════════════════════════════════
    "bitwarden": [],
    "bitwarden-cli": [],
    "1password": [],
    "1password-cli": [],
    "keepass": [],

    # ══ SCREEN RECORDING / STREAMING ══════════════════════════════════════════
    "obs-studio": [],
    "obs-vkcapture": [],
    "ffmpeg": [],
    "simplescreenrecorder": [],
    "wf-recorder": [],

    # ══ SCREENSHOT TOOLS ══════════════════════════════════════════════════════
    "flameshot": [],
    "scrot": [],
    "maim": [],

    # ══ NOTIFICATION & APPLET ═════════════════════════════════════════════════
    "libnotify": [],
    "xfce4-notifyd": [],

    # ══ FONTS ═════════════════════════════════════════════════════════════════
    "noto-fonts": [],
    "noto-fonts-cjk": [],
    "noto-fonts-emoji": [],
    "ttf-jetbrains-mono-nerd": [],
    "ttf-firacode-nerd": [],
    "adobe-source-han-sans-cn-fonts": [],

    # ══ EMBEDDED / HARDWARE DEV ═══════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Arduino
    "arduino": [
        "sudo usermod -aG uucp,lock $USER",
        "sudo systemctl enable --now avrdude",
    ],
    "arduino-cli": [
        "sudo usermod -aG uucp $USER",
    ],
    # https://wiki.archlinux.org/title/PlatformIO
    "platformio": [
        "sudo usermod -aG uucp $USER",
        "sudo usermod -aG dialout $USER",
    ],
    # https://wiki.archlinux.org/title/OpenOCD
    "openocd": [
        "sudo usermod -aG uucp $USER",
    ],
    # https://wiki.archlinux.org/title/Raspberry_Pi
    "rpi-imager": [],
    "avrdude": [],
    "stlink": [],
    "picotool": [
        "sudo udevadm control --reload-rules",
        "sudo udevadm trigger",
    ],

    # ══ SERIAL / USB / FTDI ═══════════════════════════════════════════════════
    "minicom": [
        "sudo usermod -aG uucp $USER",
    ],
    "screen": [],
    "tio": [
        "sudo usermod -aG uucp $USER",
    ],
    "picocom": [
        "sudo usermod -aG uucp $USER",
    ],
    "cu": [
        "sudo usermod -aG uucp $USER",
    ],

    # ══ NETWORK ANALYSIS ══════════════════════════════════════════════════════
    "wireshark-qt": [
        "sudo usermod -aG wireshark $USER",
    ],
    "nmap": [],
    "netcat": [],
    "tcpdump": [],
    "mtr": [],
    "iperf3": [],
    "iproute2": [],

    # ══ PROXY / TUNNEL ════════════════════════════════════════════════════════
    "traefik": [
        "sudo systemctl enable --now traefik",
    ],
    "haproxy": [
        "sudo systemctl enable --now haproxy",
    ],
    "frp": [],
    "cloudflared": [
        "sudo systemctl enable --now cloudflared",
    ],
    "tailscale": [
        "sudo systemctl enable --now tailscaled",
        "sudo tailscale up",
    ],

    # ══ CI / CD ═══════════════════════════════════════════════════════════════
    "gitlab-runner": [
        "sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner",
        "sudo systemctl enable --now gitlab-runner",
    ],
    "act": [],           # Run GitHub Actions locally
    "nektos-act-bin": [],

    # ══ ANDROID DEVELOPMENT ═══════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Android
    "android-tools": [
        "sudo usermod -aG adbusers $USER",
    ],
    "android-studio": [
        "sudo usermod -aG adbusers $USER",
    ],
    "android-udev": [
        "sudo udevadm control --reload-rules",
        "sudo udevadm trigger",
    ],

    # ══ GAME TOOLS ════════════════════════════════════════════════════════════
    "mangohud": [],
    "goverlay": [],
    "heroic-games-launcher-bin": [],
    "bottles": [],
    "pegasus-frontend": [],
    "retroarch": [],
    "pcsx2": [],
    "rpcs3-bin": [],
    "duckstation-qt-bin": [],
    "cemu": [],

    # ══ WINE HELPERS ══════════════════════════════════════════════════════════
    "winetricks": [],
    "wine-staging": [
        "sudo pacman -S --needed wine-gecko wine-mono",
    ],

    # ══ INPUT DEVICES ═════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Libinput
    "libinput": [],
    # https://wiki.archlinux.org/title/Xpadneo
    "xpadneo-dkms": [
        "sudo modprobe xpadneo",
    ],
    "xone-dkms": [
        "sudo modprobe xone",
    ],
    # https://wiki.archlinux.org/title/Piper
    "piper": [],
    "ratbagd": [
        "sudo systemctl enable --now ratbagd",
    ],

    # ══ SMART HOME / IOT ══════════════════════════════════════════════════════
    # https://www.home-assistant.io/installation/linux
    "home-assistant": [
        "sudo systemctl enable --now home-assistant",
    ],
    "mosquitto": [
        "sudo systemctl enable --now mosquitto",
    ],
    "node-red": [
        "sudo systemctl enable --now node-red",
    ],

    # ══ LANGUAGE-SPECIFIC SERVERS (LSP) ═══════════════════════════════════════
    "python-lsp-server": [],
    "rust-analyzer": [],
    "clangd": [],
    "gopls": [],
    "lua-language-server": [],
    "typescript-language-server": [],
    "bash-language-server": [],
    "yaml-language-server": [],
    "vscode-css-languageserver": [],
    "vscode-html-languageserver": [],
    "vscode-json-languageserver": [],

    # ══ GIT TOOLS ═════════════════════════════════════════════════════════════
    "lazygit": [],
    "gitui": [],
    "tig": [],
    "gh": [],         # GitHub CLI
    "glab": [],       # GitLab CLI
    "delta": [],
    "difftastic": [],
    "git-crypt": [],
    "git-secret": [],

    # ══ INFRASTRUCTURE / IaC ══════════════════════════════════════════════════
    "helm": [],
    "k9s": [],
    "kind": [],
    "k3s": [
        "sudo systemctl enable --now k3s",
    ],
    "flux-bin": [],
    "argocd-bin": [],
    "pulumi-bin": [],
    "terragrunt": [],
    "packer": [],
    "vagrant": [],

    # ══ SEARCH / OBSERVABILITY ════════════════════════════════════════════════
    "elasticsearch": [
        "sudo systemctl enable --now elasticsearch",
    ],
    "kibana": [
        "sudo systemctl enable --now kibana",
    ],
    "loki": [
        "sudo systemctl enable --now loki",
    ],
    "tempo": [
        "sudo systemctl enable --now tempo",
    ],
    "vector": [
        "sudo systemctl enable --now vector",
    ],
    "influxdb": [
        "sudo systemctl enable --now influxdb",
    ],
    "telegraf": [
        "sudo systemctl enable --now telegraf",
    ],

    # ══ MESSAGE QUEUES ════════════════════════════════════════════════════════
    "rabbitmq": [
        "sudo systemctl enable --now rabbitmq",
        "sudo rabbitmq-plugins enable rabbitmq_management",
    ],
    "kafka": [
        "sudo systemctl enable --now zookeeper",
        "sudo systemctl enable --now kafka",
    ],
    "nats-server": [
        "sudo systemctl enable --now nats",
    ],

    # ══ ACCESSIBILITY ═════════════════════════════════════════════════════════
    "orca": [],
    "espeak-ng": [],
    "festival": [],
    "brltty": [
        "sudo systemctl enable --now brltty",
        "sudo usermod -aG brlapi $USER",
    ],

    # ══ VIRTUALIZATION MISC ═══════════════════════════════════════════════════
    "lxc": [
        "sudo systemctl enable --now lxc",
        "sudo usermod -aG lxd $USER",
    ],
    "lxd": [
        "sudo systemctl enable --now lxd",
        "sudo usermod -aG lxd $USER",
        "lxd init --minimal",
    ],
    "incus": [
        "sudo systemctl enable --now incus",
        "sudo usermod -aG incus-admin $USER",
    ],
    "distrobox": [],

    # ══ MISC ARCH-SPECIFIC ════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/Pacman/Tips_and_tricks
    "reflector": [
        "sudo reflector --country 'India,US,GB' --age 24 --protocol https --sort rate --save /etc/pacman.d/mirrorlist",
        "sudo systemctl enable --now reflector.timer",
    ],
    "pkgfile": [
        "sudo pkgfile --update",
    ],
    # https://wiki.archlinux.org/title/DKMS
    "dkms": [],
    # https://wiki.archlinux.org/title/Systemd/Journal
    "systemd": [],
    # https://wiki.archlinux.org/title/Snap
    "snapd": [
        "sudo systemctl enable --now snapd.socket",
        "sudo ln -s /var/lib/snapd/snap /snap",
    ],

    # ══ CLOUD STORAGE ═════════════════════════════════════════════════════════
    "megasync": [
        "sudo systemctl enable --now megasync",
    ],
    "dropbox": [
        "systemctl --user enable --now dropbox",
    ],
    "insync": [
        "systemctl --user enable --now insync",
    ],

    # ══ AUTHENTICATION ════════════════════════════════════════════════════════
    # https://wiki.archlinux.org/title/YubiKey
    "yubikey-manager": [
        "sudo systemctl enable --now pcscd",
        "sudo usermod -aG pcscd $USER",
    ],
    "pcsclite": [
        "sudo systemctl enable --now pcscd",
    ],
    "libfido2": [],
    # https://wiki.archlinux.org/title/Polkit
    "polkit": [],
    "polkit-gnome": [],

    # ══ PRINTING EXTRAS ═══════════════════════════════════════════════════════
    "hplip": [
        "sudo systemctl enable --now cups",
        "hp-setup -i",
    ],
    "epson-inkjet-printer-escpr": [
        "sudo systemctl enable --now cups",
    ],
    "brother-dcp1510": [
        "sudo systemctl enable --now cups",
    ],
    "sane": [
        "sudo usermod -aG scanner $USER",
    ],
    "sane-backends": [
        "sudo usermod -aG scanner $USER",
    ],

    # ══ SCREEN SHARING / REMOTE ═══════════════════════════════════════════════
    "xrdp": [
        "sudo systemctl enable --now xrdp",
        "sudo usermod -aG tsusers $USER",
    ],
    "remmina": [],
    "x11vnc": [],
    "tigervnc": [],
    "wayvnc": [],
    "rustdesk-bin": [],
    "anydesk-bin": [
        "sudo systemctl enable --now anydesk",
    ],
    "teamviewer": [
        "sudo systemctl enable --now teamviewerd",
    ],

    # ══ SPELL CHECK / DICT ════════════════════════════════════════════════════
    "aspell": [],
    "aspell-en": [],
    "hunspell": [],
    "hunspell-en_us": [],

    # ══ DOCUMENTATION TOOLS ═══════════════════════════════════════════════════
    "pandoc-cli": [],
    "texlive-core": [],
    "texlive-latexextra": [],
    "mkdocs": [],
    "hugo": [],

    # ══ SCIENTIFIC / RESEARCH ═════════════════════════════════════════════════
    "octave": [],
    "r": [],
    "julia": [],
    "gnuplot": [],
    "paraview": [],
}


def get_known_steps(pkg_name: str) -> list[str] | None:
    """Return verified steps for a package, or None if not in the KB."""
    if pkg_name in KNOWN_STEPS:
        return KNOWN_STEPS[pkg_name]
    lower = pkg_name.lower()
    for key, steps in KNOWN_STEPS.items():
        if key.lower() == lower:
            return steps
    return None


def build_kb_context(packages: list) -> str:
    """
    Build a context block of verified setup steps for packages found in the KB.
    This is fed to the AI as grounding so it generates accurate env_steps.

    Returns an empty string if no packages are in the KB.
    """
    lines: list[str] = []
    for p in packages:
        steps = get_known_steps(p.name)
        if steps is None:
            continue
        lines.append(f"### {p.name}")
        if steps:
            lines.append("Verified post-install commands (from official docs):")
            for cmd in steps:
                lines.append(f"  $ {cmd}")
        else:
            lines.append("No post-install steps required.")
        lines.append("")
    return "\n".join(lines).strip()


def apply_known_steps(packages: list, current_steps: list[str]) -> list[str]:
    """
    Fallback merge used when doc-grounded AI call is skipped.
    If ALL packages are in KB: use only verified steps.
    Otherwise: prepend KB steps, then AI steps, deduplicated.
    """
    known: list[str] = []
    has_unknown = False

    for p in packages:
        steps = get_known_steps(p.name)
        if steps is None:
            has_unknown = True
        else:
            known.extend(steps)

    if not has_unknown:
        return known

    seen: set[str] = set()
    merged: list[str] = []
    for cmd in known + current_steps:
        if cmd not in seen:
            seen.add(cmd)
            merged.append(cmd)
    return merged
