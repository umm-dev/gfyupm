# gfyupm

Go Fuck Yourself Universal Package Manager. One boring Python CLI over native package managers.

## Install

```bash
python3 -m pip install gfyupm
```

Before PyPI release, install local checkout:

```bash
python3 -m pip install .
```

Developer checks:

```bash
python3 -m pip install ".[dev]"
python3 -m pytest -q
python3 -m build
python3 -m twine check dist/*
```

## Use

```bash
gfyupm install ripgrep
gfyupm remove ripgrep
gfyupm update
gfyupm upgrade
gfyupm search ripgrep
gfyupm --manager npm install typescript
gfyupm --dry-run install ripgrep
gfyupm managers
gfyupm default apt
```

`gfyupm` uses `GFYUPM_MANAGER`, then `~/.config/gfyupm/config.toml`, then available OS-native manager. `--manager` always wins.

V1 supports 75 managers. Run `gfyupm managers` for full live registry and local availability.

Commands remain native. Use native command directly for unsupported manager-specific behavior.

## Release

See [PyPI release guide](docs/PYPI.md). Releases publish through GitHub Actions trusted publishing; no API token lives in repository.
