import json
from pathlib import Path
from unittest.mock import patch

from deployment_status import status

SHA = "a" * 40
OTHER = "b" * 40


def setup(tmp_path, revision):
    folder = tmp_path / "releases" / revision
    folder.mkdir(parents=True)
    (folder / "REVISION").write_text(revision + "\n")
    return folder


def write(tmp_path, name, revision):
    dest = tmp_path / "deployment"
    dest.mkdir(exist_ok=True)
    (dest / (name + ".json")).write_text(json.dumps({"schema": 1, "revision": revision}))


def test_missing(tmp_path):
    assert status(tmp_path)["state"] == "unknown"
    assert status(tmp_path)["evidence"] == "missing"


def test_staged_is_not_active(tmp_path):
    setup(tmp_path, SHA)
    write(tmp_path, "staged", SHA)
    result = status(tmp_path)
    assert result["state"] == "staged"
    assert result["activated_revision"] is None
    assert result["runtime"] == "not_applicable"


def test_activated(tmp_path):
    setup(tmp_path, SHA)
    setup(tmp_path, OTHER)
    write(tmp_path, "staged", OTHER)
    write(tmp_path, "activated", SHA)
    result = status(tmp_path)
    assert result["state"] == "activated"
    assert result["activated_revision"] == SHA
    assert result["runtime"] == "unknown"


def test_malformed_fails_closed(tmp_path):
    (tmp_path / "deployment").mkdir()
    (tmp_path / "deployment" / "staged.json").write_text('{"schema": 1, "revision": "bogus"}')
    assert status(tmp_path)["evidence"] == "invalid"


def test_unverified_revision_fails_closed(tmp_path):
    write(tmp_path, "staged", SHA)
    assert status(tmp_path)["state"] == "unknown"
    assert status(tmp_path)["evidence"] == "invalid"


def test_symlink_evidence_rejected(tmp_path):
    (tmp_path / "deployment").mkdir()
    (tmp_path / "deployment" / "staged.json").symlink_to(tmp_path / "elsewhere")
    assert status(tmp_path)["evidence"] == "invalid"
