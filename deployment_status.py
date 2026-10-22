#!/usr/bin/env python3
"""Read-only Bastion deployment evidence; never invokes USB/SSH helpers."""
import json
import os
import re
import sys
from pathlib import Path

SHA = re.compile(r"^[a-f0-9]{40}$")


def record(root, name):
    path = root / "deployment" / (name + ".json")
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{name} evidence is not a regular file")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"schema", "revision"}:
        raise ValueError(f"{name} evidence has invalid fields")
    if data["schema"] != 1 or not isinstance(data["revision"], str) or not SHA.fullmatch(data["revision"]):
        raise ValueError(f"{name} evidence has invalid schema/revision")
    revision = data["revision"]
    version_file = root / "releases" / revision / "REVISION"
    if version_file.is_symlink() or not version_file.is_file() or version_file.read_text().strip() != revision:
        raise ValueError(f"{name} revision is not verified")
    return revision


def status(root):
    try:
        staged = record(root, "staged")
        activated = record(root, "activated")
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError):
        return {"schema": 1, "state": "unknown", "staged_revision": None,
                "activated_revision": None, "runtime": "unknown", "evidence": "invalid"}
    if activated:
        state = "activated"
    elif staged:
        state = "staged"
    else:
        state = "unknown"
    return {"schema": 1, "state": state, "staged_revision": staged,
            "activated_revision": activated,
            "runtime": "not_applicable" if state == "staged" else "unknown",
            "evidence": "verified" if state != "unknown" else "missing"}


if __name__ == "__main__":
    root = Path(os.environ.get("BASTION_INSTALL_ROOT", "/opt/gway-bastion"))
    print(json.dumps(status(root), sort_keys=True))
    sys.exit(0 if status(root)["evidence"] != "invalid" else 2)
