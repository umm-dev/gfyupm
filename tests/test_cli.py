from gfyupm.cli import main


def test_explicit_manager_dry_run(capsys):
    assert main(["--manager", "apt", "--dry-run", "install", "ripgrep"]) == 0
    assert capsys.readouterr().out == "sudo apt install ripgrep\n"


def test_global_npm_command(capsys):
    assert main(["-m", "npm", "-n", "remove", "typescript"]) == 0
    assert capsys.readouterr().out == "npm uninstall -g typescript\n"


def test_unsupported_action(capsys):
    assert main(["-m", "go", "-n", "remove", "tool"]) == 2
    assert "go does not support 'remove'" in capsys.readouterr().err


def test_manager_specific_command(capsys):
    assert main(["-m", "flatpak", "-n", "install", "org.gnome.Builder"]) == 0
    assert capsys.readouterr().out == "flatpak install -y org.gnome.Builder\n"


def test_root_does_not_prefix_sudo(monkeypatch, capsys):
    monkeypatch.setattr("gfyupm.cli.os.geteuid", lambda: 0)
    assert main(["-m", "apt", "-n", "install", "ripgrep"]) == 0
    assert capsys.readouterr().out == "apt install ripgrep\n"
