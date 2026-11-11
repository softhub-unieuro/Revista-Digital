"""Backup consistente com janela de manutenção; restauração só em ambiente vazio."""

import argparse
import hashlib
import json
import os
import subprocess
import tarfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=["backup", "restore", "verify"])
parser.add_argument("--env-file", required=True, type=Path)
parser.add_argument("--project", required=True)
parser.add_argument("--context")
parser.add_argument("--directory", required=True, type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
command = (
    ["docker"]
    + (["--context", args.context] if args.context else [])
    + [
        "compose",
        "--env-file",
        str(args.env_file.resolve()),
        "-f",
        str(root / "compose.production.yaml"),
        "-p",
        args.project,
    ]
)


def run(parts, **kwargs):
    return subprocess.run(command + parts, check=True, **kwargs)


def digest(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def verify():
    manifest = json.loads((args.directory / "manifest.json").read_text())
    if manifest.get("format") != 1:
        raise SystemExit("Formato de backup não suportado.")
    for name in ["database.dump", "storage.tar.gz"]:
        path = args.directory / name
        if (
            path.is_symlink()
            or not path.is_file()
            or path.stat().st_size != manifest["files"][name]["bytes"]
            or digest(path) != manifest["files"][name]["sha256"]
        ):
            raise SystemExit(f"Backup inválido: {name}")
    with tarfile.open(args.directory / "storage.tar.gz", "r:gz") as archive:
        for entry in archive:
            path = PurePosixPath(entry.name)
            if path.is_absolute() or ".." in path.parts or not (entry.isfile() or entry.isdir()):
                raise SystemExit("Arquivo de armazenamento contém uma entrada insegura.")
    return manifest


if args.action == "verify":
    verify()
    print("Manifesto, checksums e caminhos do backup válidos.")
    raise SystemExit(0)
if args.action == "backup":
    # Pasta nova evita substituir um backup existente e permissões protegem o conteúdo.
    args.directory.mkdir(parents=True, exist_ok=False)
    args.directory.chmod(0o700)
    running = run(
        ["ps", "--services", "--filter", "status=running"],
        capture_output=True,
        text=True,
    ).stdout.split()
    paused = [name for name in ["web", "api", "worker"] if name in running]
    if "db" not in running:
        raise SystemExit("Inicie o banco antes do backup.")
    try:
        if paused:
            run(["stop", *paused])
        for name, parts in [
            (
                "database.dump",
                [
                    "exec",
                    "-T",
                    "db",
                    "sh",
                    "-c",
                    'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc --no-owner --no-acl',
                ],
            ),
            (
                "storage.tar.gz",
                [
                    "run",
                    "--rm",
                    "--no-deps",
                    "-T",
                    "--entrypoint",
                    "tar",
                    "api",
                    "-C",
                    "/storage",
                    "-czf",
                    "-",
                    ".",
                ],
            ),
        ]:
            with (args.directory / name).open("xb") as file:
                os.chmod(file.name, 0o600)
                run(parts, stdout=file)
        image_ids = run(
            ["images", "--quiet", "api", "web"], capture_output=True, text=True
        ).stdout.split()
        manifest = {
            "images": sorted(set(image_ids)),
            "format": 1,
            "created_at": datetime.now(UTC).isoformat(),
            "project": args.project,
            "files": {
                name: {
                    "bytes": (args.directory / name).stat().st_size,
                    "sha256": digest(args.directory / name),
                }
                for name in ["database.dump", "storage.tar.gz"]
            },
        }
        (args.directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        verify()
        print("Backup consistente concluído; checksums verificados.")
    finally:
        if paused:
            run(["start", *paused])
else:
    verify()
    running = run(
        ["ps", "--services", "--filter", "status=running"],
        capture_output=True,
        text=True,
    ).stdout.split()
    if any(name in running for name in ["api", "worker", "web"]):
        raise SystemExit("Restaure em outro projeto vazio, com apenas db/redis iniciados.")
    check = run(
        [
            "exec",
            "-T",
            "db",
            "sh",
            "-c",
            'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT count(*) FROM pg_tables WHERE schemaname=\'public\'"',
        ],
        capture_output=True,
        text=True,
    )
    if check.stdout.strip() != "0":
        raise SystemExit("Destino contém tabelas. Nenhum dado foi sobrescrito.")
    # O volume também deve estar vazio para evitar mistura entre versões.
    check = run(
        [
            "run",
            "--rm",
            "--no-deps",
            "-T",
            "--entrypoint",
            "find",
            "api",
            "/storage",
            "-mindepth",
            "1",
            "-print",
            "-quit",
        ],
        capture_output=True,
        text=True,
    )
    if check.stdout.strip():
        raise SystemExit("O armazenamento do destino não está vazio.")
    with (args.directory / "storage.tar.gz").open("rb") as file:
        run(
            [
                "run",
                "--rm",
                "--no-deps",
                "-T",
                "--entrypoint",
                "tar",
                "api",
                "-C",
                "/storage",
                "-xzf",
                "-",
                "--no-same-owner",
                "--no-same-permissions",
            ],
            stdin=file,
        )
    with (args.directory / "database.dump").open("rb") as file:
        run(
            [
                "exec",
                "-T",
                "db",
                "sh",
                "-c",
                'exec pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-acl --exit-on-error',
            ],
            stdin=file,
        )
    print(
        "Backup restaurado no destino vazio. Inicie a aplicação e valide a jornada e os arquivos."
    )
