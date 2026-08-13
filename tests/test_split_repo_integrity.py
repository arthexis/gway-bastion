from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_bash_helpers_parse():
    helpers = [
        ROOT / "scripts/gway/bastion-key-present",
        ROOT / "scripts/gway/bastion-require",
        ROOT / "scripts/gway/bastion-usb-refresh",
        ROOT / "scripts/gway/usb-git/common.sh",
        ROOT / "scripts/gway/usb-git/pre-push-main-guard.sh",
        ROOT / "scripts/gway/usb-git/usb-git",
        ROOT / "bin/gh",
        ROOT / "bin/usb-git",
        ROOT / "bin/usb-ssh",
        ROOT / "bin/usb-unlock-on",
        ROOT / "bin/usb-unlock-off",
        ROOT / "lib/usb-git/common.sh",
        ROOT / "lib/usb-git/pre-push-main-guard.sh",
    ]

    for helper in helpers:
        result = subprocess.run(["bash", "-n", str(helper)], check=False, capture_output=True, text=True)
        assert result.returncode == 0, f"{helper}: {result.stderr}"


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
