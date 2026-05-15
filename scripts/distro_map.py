"""Cross-reference distro names between different sources (DistroWatch, Repology, Phoronix)."""

DISTRO_NAME_ALIASES: dict[str, dict[str, str]] = {
    "ubuntu": {"repology": "ubuntu_24_04", "phoronix": "Ubuntu"},
    "linux-mint": {"repology": "mx_25", "phoronix": "Linux Mint"},
    "debian": {"repology": "debian_12", "phoronix": "Debian"},
    "fedora": {"repology": "fedora_44", "phoronix": "Fedora"},
    "arch": {"repology": "arch", "phoronix": "Arch Linux"},
    "manjaro": {"repology": "manjaro_stable", "phoronix": "Manjaro"},
    "pop": {"repology": None, "phoronix": "Pop!_OS"},
    "opensuse": {"repology": "opensuse_tumbleweed", "phoronix": "openSUSE"},
    "nixos": {"repology": "nix_unstable", "phoronix": "NixOS"},
    "gentoo": {"repology": "gentoo", "phoronix": "Gentoo"},
    "void": {"repology": "void_x86_64", "phoronix": "Void Linux"},
    "slackware": {"repology": "slackware_current", "phoronix": "Slackware"},
    "elementary": {"repology": None, "phoronix": "elementary OS"},
    "zorin": {"repology": None, "phoronix": "Zorin OS"},
    "kali": {"repology": "kali_rolling", "phoronix": "Kali Linux"},
    "endeavouros": {"repology": None, "phoronix": "EndeavourOS"},
    "solus": {"repology": "solus", "phoronix": "Solus"},
    "alpine": {"repology": "alpine_edge", "phoronix": "Alpine Linux"},
    "mx": {"repology": "mx_25", "phoronix": "MX Linux"},
    "garuda": {"repology": None, "phoronix": "Garuda Linux"},
    "devuan": {"repology": "devuan_unstable", "phoronix": "Devuan"},
    "artix": {"repology": "artix", "phoronix": "Artix Linux"},
    "freebsd": {"repology": "freebsd", "phoronix": None},
    "puppy": {"repology": None, "phoronix": None},
    "tails": {"repology": "tails_stable", "phoronix": "Tails"},
    "alma": {"repology": "almalinux_9", "phoronix": "AlmaLinux"},
    "parrot": {"repology": "parrot", "phoronix": "Parrot OS"},
    "centos": {"repology": "centos_stream_9", "phoronix": "CentOS"},
    "kubuntu": {"repology": None, "phoronix": "Kubuntu"},
    "pclinuxos": {"repology": "pclinuxos", "phoronix": None},
    "mx-linux": {"repology": None, "phoronix": "MX Linux"},
    "arch-linux": {"repology": None, "phoronix": "Arch Linux"},
    "pop-os": {"repology": None, "phoronix": "Pop!_OS"},
    "zorin-os": {"repology": None, "phoronix": "Zorin OS"},
    "endeavouros": {"repology": None, "phoronix": "EndeavourOS"},
    "garuda-linux": {"repology": None, "phoronix": "Garuda Linux"},
    "opensuse-tumbleweed": {"repology": None, "phoronix": "openSUSE Tumbleweed"},
    "nobara-project": {"repology": None, "phoronix": "Nobara"},
    "nobara": {"repology": None, "phoronix": "Nobara"},
}


def repology_repo_for(slug: str) -> str | None:
    aliases = DISTRO_NAME_ALIASES.get(slug)
    if aliases:
        return aliases.get("repology")
    return None


def phoronix_name_for(slug: str) -> str | None:
    aliases = DISTRO_NAME_ALIASES.get(slug)
    if aliases:
        return aliases.get("phoronix")
    return None
