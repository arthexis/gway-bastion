from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_bash_helpers_parse():
    helpers = [
        ROOT / "scripts/gway/bastion-key-present",
        ROOT / "scripts/gway/bastion-require",
        ROOT / "scripts/gway/bastion-ssh-session-sound",
        ROOT / "scripts/gway/bastion-usb-refresh",
        ROOT / "bin/gh",
        ROOT / "bin/usb-ssh",
        ROOT / "bin/usb-unlock-on",
        ROOT / "bin/usb-unlock-off",
    ]

    for helper in helpers:
        result = subprocess.run(["bash", "-n", str(helper)], check=False, capture_output=True, text=True)
        assert result.returncode == 0, f"{helper}: {result.stderr}"


def test_gh_wrapper_delegates_directly_to_official_cli():
    wrapper = (ROOT / "bin/gh").read_text(encoding="utf-8")
    assert "exec /usr/bin/gh" in wrapper
    assert "usb-git" not in wrapper


def test_no_github_bastion_gate_surface_remains():
    retired_paths = [
        "bin/github-usb-bootstrap",
        "bin/install-github-usb-main-guard",
        "bin/usb-git",
        "config/templates/usb-git.env.template",
        "docs/man/man1/usb-git.1",
        "lib/usb-git/common.sh",
        "lib/usb-git/pre-push-main-guard.sh",
        "scripts/gway/usb-git/common.sh",
        "scripts/gway/usb-git/pre-push-main-guard.sh",
        "scripts/gway/usb-git/usb-git",
    ]

    for relative_path in retired_paths:
        assert not (ROOT / relative_path).exists(), relative_path

    credential_rotate = (ROOT / "bin/github-credential-rotate").read_text(encoding="utf-8")
    assert "usb-git" not in credential_rotate
    assert "bastion" not in credential_rotate.lower()


def test_no_common_token_or_private_key_material_committed():
    legacy_token = "".join(("g", "h", "p", "_"))
    fine_grained_token = "github" + "_pat_"
    private_key_marker = "-----BEGIN " + "PRIVATE KEY-----"
    suspicious = re.compile(
        rf"({re.escape(legacy_token)}|{re.escape(fine_grained_token)}|{re.escape(private_key_marker)})"
    )
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert not suspicious.search(text), str(path)


def test_bastion_refresh_layout_cleanup_is_explicit():
    helper = (ROOT / "scripts/gway/bastion-usb-refresh").read_text(encoding="utf-8")
    docs = (ROOT / "docs/usb-inventory-and-bastion-unlock.md").read_text(encoding="utf-8")

    assert "BASTION_USB_REFRESH_CLEANUP_LAYOUT" in helper
    assert 'CLEANUP_USB_LAYOUT" == "1"' in helper
    assert "--service-prestart --quiet" in helper
    assert "--apply --quiet" not in helper
    assert "BASTION_USB_REFRESH_CLEANUP_LAYOUT=1" in docs


def test_ssh_session_sound_hook_is_opt_in_and_non_blocking():
    helper = (ROOT / "scripts/gway/bastion-ssh-session-sound").read_text(encoding="utf-8")
    template = (ROOT / "config/pam.d/sshd-gway-session-sound.conf").read_text(encoding="utf-8")
    docs = (ROOT / "docs/ssh-session-sound.md").read_text(encoding="utf-8")

    assert 'PAM_TYPE:-' in helper
    assert 'open_session' in helper
    assert 'flock -n' in helper
    assert 'nohup' in helper
    assert '--event session-opened --source ssh' in helper
    assert 'session optional pam_exec.so quiet type=open_session' in template
    assert '/etc/pam.d/sshd' in docs
    assert 'does not install or activate' in docs
