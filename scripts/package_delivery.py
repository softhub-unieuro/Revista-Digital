"""Empacota somente arquivos rastreados de um commit limpo, sem segredos ou uploads."""

import argparse
import hashlib
import json
import subprocess
import zipfile
from datetime import UTC, datetime
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]


def git(*parts):
    return subprocess.run(
        ["git", "-C", str(root), *parts], check=True, capture_output=True, text=True
    ).stdout.strip()


if git("status", "--porcelain"):
    parser.error(
        "Finalize o commit antes de gerar a entrega; o pacote deve corresponder ao código validado."
    )
files = git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
for name in files:
    path = Path(name)
    if (
        (path.name.startswith(".env") and not path.name.endswith(".example"))
        or path.suffix in {".pem", ".key", ".dump", ".sqlite3"}
        or name.startswith(("storage/", "backups/", "entregas/"))
    ):
        parser.error("Há arquivo privado no commit. Corrija o conteúdo antes de empacotar.")
args.output.parent.mkdir(parents=True, exist_ok=True)
if args.output.exists():
    parser.error("O arquivo de entrega já existe; escolha outro nome.")
commit = git("rev-parse", "HEAD")
subprocess.run(
    [
        "git",
        "-C",
        str(root),
        "archive",
        "--format=zip",
        "--prefix=unieuro-revista/",
        "HEAD",
        "-o",
        str(args.output.resolve()),
    ],
    check=True,
)
with zipfile.ZipFile(args.output, "a", compression=zipfile.ZIP_DEFLATED) as archive:
    archive.writestr(
        "unieuro-revista/ENTREGA.json",
        json.dumps(
            {
                "commit": commit,
                "created_at": datetime.now(UTC).isoformat(),
                "artifact": "Pacote Docker para homologação e futura implantação",
                "entrypoint": "docs/16-operacao-docker.md",
                "contains": "Código, assets fornecidos, Dockerfiles, lockfiles, testes e manuais. Sem senhas, certificados, banco ou PDFs enviados.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
with args.output.open("rb") as file:
    digest = hashlib.file_digest(file, "sha256").hexdigest()
args.output.with_suffix(".zip.sha256").write_text(f"{digest}  {args.output.name}\n")
print(f"Entrega criada: {args.output}\nCommit: {commit}\nSHA-256: {digest}")
