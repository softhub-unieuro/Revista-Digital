import hashlib
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def archive(tmp_path, entry="documents/revista.pdf", symbolic=False):
    (tmp_path / "database.dump").write_bytes(b"test archive header")
    with tarfile.open(tmp_path / "storage.tar.gz", "w:gz") as output:
        info = tarfile.TarInfo(entry)
        if symbolic:
            info.type = tarfile.SYMTYPE
            info.linkname = "/etc/passwd"
            output.addfile(info)
        else:
            info.size = 4
            output.addfile(info, io.BytesIO(b"test"))
    files = {
        name: {
            "bytes": (tmp_path / name).stat().st_size,
            "sha256": hashlib.sha256((tmp_path / name).read_bytes()).hexdigest(),
        }
        for name in ["database.dump", "storage.tar.gz"]
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"format": 1, "files": files}))


def verify(tmp_path):
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/production_backup.py"),
            "verify",
            "--env-file",
            str(tmp_path / "unused.env"),
            "--project",
            "verification-only",
            "--directory",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )


def test_backup_verifier_detects_corruption(tmp_path):
    archive(tmp_path)
    assert verify(tmp_path).returncode == 0
    (tmp_path / "database.dump").write_bytes(b"modified")
    assert verify(tmp_path).returncode != 0


@pytest.mark.parametrize(
    ("entry", "symbolic"), [("../outside.txt", False), ("safe-looking-link", True)]
)
def test_restore_rejects_unsafe_archive_paths(tmp_path, entry, symbolic):
    archive(tmp_path, entry, symbolic)
    result = verify(tmp_path)
    assert result.returncode != 0 and "insegura" in result.stderr
