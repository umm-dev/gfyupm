"""Boring CLI for gfyupm."""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys

from . import __version__
from .config import read_default, write_default
from .managers import MANAGERS, available, default_manager

ACTIONS = ("install", "remove", "update", "upgrade", "search", "info", "list", "clean")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gfyupm", description="Boring universal package manager.")
    p.add_argument("--manager", "-m", choices=sorted(MANAGERS), help="manager to use")
    p.add_argument("--dry-run", "-n", action="store_true", help="print command without running it")
    p.add_argument("--version", action="version", version=f"gfyupm {__version__}")
    sub = p.add_subparsers(dest="action", required=True)
    for action in ACTIONS:
        command = sub.add_parser(action)
        command.add_argument("packages", nargs="*", metavar="PACKAGE")
    sub.add_parser("managers", help="show installed package managers")
    default = sub.add_parser("default", help="show or set default manager")
    default.add_argument("manager", nargs="?", choices=sorted(MANAGERS))
    return p


def resolve(name: str | None):
    if name:
        return MANAGERS[name]
    return default_manager(read_default())


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.action == "managers":
        installed = available()
        for name in sorted(MANAGERS):
            print(f"{name}\t{'installed' if name in installed else 'missing'}")
        return 0
    if args.action == "default":
        if args.manager:
            write_default(args.manager)
            print(args.manager)
            return 0
        manager = resolve(None)
        if manager is None:
            print("no supported package manager found", file=sys.stderr)
            return 1
        print(manager.name)
        return 0
    manager = resolve(args.manager)
    if manager is None:
        print("no supported package manager found; use --manager", file=sys.stderr)
        return 1
    packages = args.packages
    if args.action in {"install", "remove", "search", "info"} and not packages:
        parser().error(f"{args.action} needs PACKAGE")
    try:
        command = manager.command(args.action, packages)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    if args.dry_run:
        print(shlex.join(command))
        return 0
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
