"""Package manager command definitions and selection."""

from __future__ import annotations

from dataclasses import dataclass
import os
import platform
import shutil
from typing import Iterable


@dataclass(frozen=True)
class Manager:
    name: str
    executable: str
    commands: dict[str, tuple[str, ...]]
    priority: int = 100
    executables: dict[str, str] | None = None

    def command(self, action: str, packages: Iterable[str]) -> list[str]:
        try:
            args = self.commands[action]
        except KeyError as exc:
            raise ValueError(f"{self.name} does not support '{action}'") from exc
        executable = self.executables.get(action, self.executable) if self.executables else self.executable
        return [executable, *args, *packages]


def m(name: str, exe: str, *, install=None, remove=None, update=None, upgrade=None,
      search=None, info=None, list_=None, clean=None, priority=100) -> Manager:
    values = {
        "install": install, "remove": remove, "update": update, "upgrade": upgrade,
        "search": search, "info": info, "list": list_, "clean": clean,
    }
    return Manager(name, exe, {action: tuple(args) for action, args in values.items() if args is not None}, priority)


# Commands intentionally stay close to each manager's native CLI.
MANAGERS: dict[str, Manager] = {
    "apt": m("apt", "apt", install=("install",), remove=("remove",), update=("update",), upgrade=("upgrade",), search=("search",), info=("show",), list_=("list", "--installed"), clean=("autoremove", "--purge"), priority=10),
    "aptitude": m("aptitude", "aptitude", install=("install",), remove=("remove",), update=("update",), upgrade=("safe-upgrade",), search=("search",), info=("show",), list_=("search", "~i"), clean=("autoclean",), priority=30),
    "nala": m("nala", "nala", install=("install",), remove=("remove",), update=("update",), upgrade=("upgrade",), search=("search",), info=("show",), list_=("list", "--installed"), clean=("autoremove",), priority=25),
    "dnf": m("dnf", "dnf", install=("install",), remove=("remove",), update=("check-update",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list", "installed"), clean=("autoremove",), priority=10),
    "microdnf": m("microdnf", "microdnf", install=("install",), remove=("remove",), update=("check-update",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list", "installed"), clean=("clean", "all"), priority=25),
    "yum": m("yum", "yum", install=("install",), remove=("remove",), update=("check-update",), upgrade=("update",), search=("search",), info=("info",), list_=("list", "installed"), clean=("autoremove",), priority=20),
    "urpmi": m("urpmi", "urpmi", install=(), remove=(), update=("--auto-update",), upgrade=("--auto-select",), search=(), info=(), list_=(), clean=("--auto-orphans",), priority=25),
    "pacman": m("pacman", "pacman", install=("-S",), remove=("-Rns",), update=("-Sy",), upgrade=("-Syu",), search=("-Ss",), info=("-Si",), list_=("-Q",), clean=("-Scc",), priority=10),
    "yay": m("yay", "yay", install=("-S",), remove=("-Rns",), update=("-Sy",), upgrade=("-Syu",), search=("-Ss",), info=("-Si",), list_=("-Q",), clean=("-Scc",), priority=25),
    "paru": m("paru", "paru", install=("-S",), remove=("-Rns",), update=("-Sy",), upgrade=("-Syu",), search=("-Ss",), info=("-Si",), list_=("-Q",), clean=("-Scc",), priority=25),
    "pamac": m("pamac", "pamac", install=("install",), remove=("remove",), update=("update",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list", "--installed"), clean=("clean",), priority=25),
    "zypper": m("zypper", "zypper", install=("install",), remove=("remove",), update=("refresh",), upgrade=("update",), search=("search",), info=("info",), list_=("search", "--installed-only"), clean=("clean",), priority=10),
    "apk": m("apk", "apk", install=("add",), remove=("del",), update=("update",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("info",), clean=("cache", "clean"), priority=10),
    "opkg": m("opkg", "opkg", install=("install",), remove=("remove",), update=("update",), upgrade=("upgrade",), search=("find",), info=("info",), list_=("list-installed",), clean=("clean",), priority=20),
    "tazpkg": m("tazpkg", "tazpkg", install=("get-install",), remove=("remove",), update=("recharge",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list",), clean=("clean-cache",), priority=25),
    "pkgin": m("pkgin", "pkgin", install=("install",), remove=("remove",), update=("update",), upgrade=("upgrade",), search=("search",), info=("show",), list_=("list",), clean=("clean",), priority=20),
    "pkg_add": m("pkg_add", "pkg_add", install=(), priority=20),
    "eopkg": m("eopkg", "eopkg", install=("install",), remove=("remove",), update=("update-repo",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list-installed",), clean=("delete-cache",), priority=20),
    "swupd": m("swupd", "swupd", install=("bundle-add",), remove=("bundle-remove",), update=("check-update",), upgrade=("update",), search=("search",), info=("bundle-info",), list_=("bundle-list",), clean=("clean",), priority=20),
    "tdnf": m("tdnf", "tdnf", install=("install",), remove=("remove",), update=("check-update",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list", "installed"), clean=("clean", "all"), priority=20),
    "rpm-ostree": m("rpm-ostree", "rpm-ostree", install=("install",), remove=("uninstall",), upgrade=("upgrade",), list_=("status",), clean=("cleanup", "-m"), priority=20),
    "guix": m("guix", "guix", install=("install",), remove=("remove",), update=("pull",), upgrade=("package", "--upgrade"), search=("search",), info=("show",), list_=("package", "--list-installed"), clean=("gc",), priority=20),
    "slackpkg": m("slackpkg", "slackpkg", install=("install",), remove=("remove",), update=("update",), upgrade=("upgrade-all",), search=("search",), info=("info",), list_=("search", "installed"), clean=("clean-system",), priority=20),
    "snap": m("snap", "snap", install=("install",), remove=("remove",), update=("refresh", "--list"), upgrade=("refresh",), search=("find",), info=("info",), list_=("list",), priority=20),
    "flatpak": m("flatpak", "flatpak", install=("install", "-y"), remove=("uninstall", "-y"), update=("update", "--appstream"), upgrade=("update", "-y"), search=("search",), info=("info",), list_=("list",), clean=("uninstall", "--unused", "-y"), priority=20),
    "xbps": Manager("xbps", "xbps-install", {
        "install": (), "remove": (), "update": ("-S",), "upgrade": ("-u",),
        "search": ("-Rs",), "info": ("-R",), "list": ("-l",), "clean": ("-Oo",),
    }, priority=10, executables={
        "remove": "xbps-remove", "search": "xbps-query", "info": "xbps-query",
        "list": "xbps-query", "clean": "xbps-remove",
    }),
    "emerge": m("emerge", "emerge", install=(), remove=("--depclean",), update=("--sync",), upgrade=("--update", "--deep", "--newuse", "@world"), search=("--search",), info=("--info",), list_=("--search", "@installed"), clean=("--depclean",), priority=10),
    "pkg": m("pkg", "pkg", install=("install",), remove=("delete",), update=("update",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("info",), clean=("clean",), priority=10),
    "brew": m("brew", "brew", install=("install",), remove=("uninstall",), update=("update",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list",), clean=("cleanup",), priority=20),
    "port": m("port", "port", install=("install",), remove=("uninstall",), update=("selfupdate",), upgrade=("upgrade", "outdated"), search=("search",), info=("info",), list_=("installed",), clean=("clean", "--all"), priority=20),
    "mas": m("mas", "mas", install=("install",), remove=(), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list",), priority=30),
    "winget": m("winget", "winget", install=("install",), remove=("uninstall",), update=("source", "update"), upgrade=("upgrade", "--all"), search=("search",), info=("show",), list_=("list",), priority=10),
    "choco": m("choco", "choco", install=("install", "-y"), remove=("uninstall", "-y"), update=("outdated",), upgrade=("upgrade", "all", "-y"), search=("search",), info=("info",), list_=("list", "--local-only"), clean=("clean",), priority=20),
    "scoop": m("scoop", "scoop", install=("install",), remove=("uninstall",), update=("update",), upgrade=("update", "*"), search=("search",), info=("info",), list_=("list",), clean=("cleanup", "*"), priority=20),
    "nix": m("nix", "nix", install=("profile", "install"), remove=("profile", "remove"), update=("channel", "--update"), upgrade=("profile", "upgrade", "--all"), search=("search",), info=("search",), list_=("profile", "list"), clean=("store", "gc"), priority=20),
    "nix-env": m("nix-env", "nix-env", install=("-iA",), remove=("-e",), upgrade=("-u",), search=("-qaP",), info=("-qa",), list_=("-q",), clean=("--delete-generations", "old"), priority=35),
    "flox": m("flox", "flox", install=("install",), remove=("uninstall",), upgrade=("upgrade",), search=("search",), info=("show",), list_=("list",), clean=("delete",), priority=50),
    "npm": m("npm", "npm", install=("install", "-g"), remove=("uninstall", "-g"), update=("update", "-g"), upgrade=("update", "-g"), search=("search",), info=("view",), list_=("list", "-g", "--depth=0"), clean=("cache", "clean", "--force"), priority=50),
    "pnpm": m("pnpm", "pnpm", install=("add", "-g"), remove=("remove", "-g"), update=("update", "-g"), upgrade=("update", "-g"), search=("search",), info=("info",), list_=("list", "-g", "--depth=0"), clean=("store", "prune"), priority=45),
    "yarn": m("yarn", "yarn", install=("global", "add"), remove=("global", "remove"), update=("global", "upgrade"), upgrade=("global", "upgrade"), info=("info",), list_=("global", "list"), clean=("cache", "clean"), priority=55),
    "bun": m("bun", "bun", install=("add", "-g"), remove=("remove", "-g"), update=("update", "-g"), upgrade=("update", "-g"), info=("pm", "view"), list_=("pm", "ls", "-g"), clean=("pm", "cache", "rm"), priority=45),
    "deno": m("deno", "deno", install=("install", "--global"), remove=("uninstall",), upgrade=("upgrade",), priority=45),
    "volta": m("volta", "volta", install=("install",), remove=("uninstall",), upgrade=("install",), list_=("list",), priority=45),
    "mise": m("mise", "mise", install=("use", "--global"), remove=("uninstall",), upgrade=("upgrade",), list_=("ls",), priority=45),
    "pip": m("pip", "pip", install=("install",), remove=("uninstall", "-y"), upgrade=("install", "--upgrade"), search=(), info=("show",), list_=("list",), clean=("cache", "purge"), priority=50),
    "pipx": m("pipx", "pipx", install=("install",), remove=("uninstall",), upgrade=("upgrade",), list_=("list",), priority=45),
    "uv": m("uv", "uv", install=("tool", "install"), remove=("tool", "uninstall"), upgrade=("tool", "upgrade"), list_=("tool", "list"), clean=("cache", "clean"), priority=40),
    "pdm": m("pdm", "pdm", install=("add",), remove=("remove",), update=("update",), upgrade=("update",), search=("search",), info=("show",), list_=("list",), clean=("cache", "clear"), priority=60),
    "pixi": m("pixi", "pixi", install=("global", "install"), remove=("global", "remove"), upgrade=("global", "update"), search=("search",), list_=("global", "list"), clean=("clean",), priority=45),
    "poetry": m("poetry", "poetry", install=("add",), remove=("remove",), update=("update",), upgrade=("update",), search=("search",), info=("show",), list_=("show",), clean=("cache", "clear", "PyPI", "--all"), priority=60),
    "cargo": m("cargo", "cargo", install=("install",), remove=("uninstall",), update=("install-update",), upgrade=("install-update", "-a"), search=("search",), info=("info",), list_=("install", "--list"), priority=50),
    "cargo-binstall": m("cargo-binstall", "cargo-binstall", install=("binstall",), priority=55),
    "gem": m("gem", "gem", install=("install",), remove=("uninstall",), update=("update",), upgrade=("update",), search=("search",), info=("info",), list_=("list",), clean=("cleanup",), priority=50),
    "cpan": m("cpan", "cpan", install=("-i",), upgrade=("-u",), search=("-a",), info=("-D",), list_=("-l",), priority=60),
    "composer": m("composer", "composer", install=("global", "require"), remove=("global", "remove"), update=("global", "update"), upgrade=("global", "update"), search=("search",), info=("show",), list_=("global", "show"), clean=("clear-cache",), priority=50),
    "go": m("go", "go", install=("install",), list_=("list", "-m", "all"), priority=50),
    "dotnet": m("dotnet", "dotnet", install=("tool", "install", "--global"), remove=("tool", "uninstall", "--global"), upgrade=("tool", "update", "--global"), search=("tool", "search"), list_=("tool", "list", "--global"), priority=50),
    "luarocks": m("luarocks", "luarocks", install=("install",), remove=("remove",), upgrade=("install",), search=("search",), info=("show",), list_=("list",), clean=("purge",), priority=50),
    "cabal": m("cabal", "cabal", install=("install",), update=("update",), search=("list",), info=("info",), list_=("list", "--installed"), clean=("clean",), priority=50),
    "haxelib": m("haxelib", "haxelib", install=("install",), remove=("remove",), update=("update",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list",), priority=50),
    "opam": m("opam", "opam", install=("install",), remove=("remove",), update=("update",), upgrade=("upgrade",), search=("search",), info=("show",), list_=("list",), clean=("clean",), priority=50),
    "nimble": m("nimble", "nimble", install=("install",), remove=("uninstall",), update=("refresh",), upgrade=("upgrade",), search=("search",), list_=("list",), priority=50),
    "dart": m("dart", "dart", install=("pub", "global", "activate"), remove=("pub", "global", "deactivate"), upgrade=("pub", "global", "activate"), list_=("pub", "global", "list"), priority=50),
    "vcpkg": m("vcpkg", "vcpkg", install=("install",), remove=("remove",), update=("update",), upgrade=("upgrade",), search=("search",), info=("x-package-info",), list_=("list",), clean=("remove", "--outdated"), priority=50),
    "conan": m("conan", "conan", install=("install",), remove=("remove",), search=("search",), info=("inspect",), list_=("list",), clean=("remove", "*", "-c"), priority=50),
    "spack": m("spack", "spack", install=("install",), remove=("uninstall",), update=("repo", "update"), upgrade=("reindex",), search=("list",), info=("info",), list_=("find",), clean=("clean",), priority=50),
    "tlmgr": m("tlmgr", "tlmgr", install=("install",), remove=("remove",), update=("update",), upgrade=("update", "--self", "--all"), search=("search",), info=("info",), list_=("list", "--only-installed"), clean=("path", "remove"), priority=50),
    "raco": m("raco", "raco", install=("pkg", "install", "--auto"), remove=("pkg", "remove", "--auto"), update=("pkg", "update", "--auto"), search=("pkg", "catalog-search"), info=("pkg", "show"), list_=("pkg", "installed"), priority=50),
    "code": m("code", "code", install=("--install-extension",), remove=("--uninstall-extension",), upgrade=("--update-extensions",), list_=("--list-extensions",), priority=60),
    "conda": m("conda", "conda", install=("install",), remove=("remove",), update=("update",), upgrade=("update", "--all"), search=("search",), info=("info",), list_=("list",), clean=("clean", "--all"), priority=50),
    "mamba": m("mamba", "mamba", install=("install",), remove=("remove",), update=("update",), upgrade=("update", "--all"), search=("search",), info=("info",), list_=("list",), clean=("clean", "--all"), priority=45),
    "micromamba": m("micromamba", "micromamba", install=("install",), remove=("remove",), update=("update",), upgrade=("update", "--all"), search=("search",), info=("info",), list_=("list",), clean=("clean", "--all"), priority=45),
    "krew": m("krew", "kubectl-krew", install=("install",), remove=("uninstall",), update=("update",), upgrade=("upgrade",), search=("search",), info=("info",), list_=("list",), priority=60),
    "gh": m("gh", "gh", install=("extension", "install"), remove=("extension", "remove"), upgrade=("extension", "upgrade", "--all"), list_=("extension", "list"), priority=60),
    "code-insiders": m("code-insiders", "code-insiders", install=("--install-extension",), remove=("--uninstall-extension",), upgrade=("--update-extensions",), list_=("--list-extensions",), priority=60),
}


def available() -> dict[str, Manager]:
    return {name: manager for name, manager in MANAGERS.items() if shutil.which(manager.executable)}


def default_manager(config_default: str | None = None) -> Manager | None:
    requested = os.environ.get("GFYUPM_MANAGER") or config_default
    if requested:
        if requested not in MANAGERS:
            raise ValueError(f"unknown manager '{requested}'")
        return MANAGERS[requested]
    installed = available()
    if not installed:
        return None
    system = platform.system()
    preferred = {"Darwin": ("brew", "port"), "Windows": ("winget", "choco", "scoop")}.get(system, ())
    for name in preferred:
        if name in installed:
            return installed[name]
    return min(installed.values(), key=lambda manager: manager.priority)
