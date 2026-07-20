# gfyupm

Go Fuck Yourself Universal Package Manager. One boring Python CLI over native package managers.

## Install

```bash
python3 -m pip install .
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
