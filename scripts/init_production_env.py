"""Cria configuração privada de implantação; não altera arquivos existentes."""

import argparse
import os
import secrets
from pathlib import Path
from urllib.parse import urlparse

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, default=Path(".env.production"))
parser.add_argument("--origin", required=True, help="Origem HTTPS final, sem caminho")
parser.add_argument("--tls-dir", type=Path, default=Path("deploy/certs"))
parser.add_argument("--http-bind", default="127.0.0.1:15080")
parser.add_argument("--https-bind", default="127.0.0.1:15443")
args = parser.parse_args()
origin = args.origin.rstrip("/")
url = urlparse(origin)
if (
    url.scheme != "https"
    or not url.hostname
    or url.path
    or url.query
    or url.fragment
    or url.username
    or url.password
):
    parser.error("Use uma origem HTTPS sem caminho, credenciais ou parâmetros.")
if not all(c.isalnum() or c in ".-:" for c in url.netloc):
    parser.error("O domínio informado não é válido.")
for bind in [args.http_bind, args.https_bind]:
    if not all(c.isdigit() or c in ".:" for c in bind):
        parser.error("Bindings devem usar endereço IPv4 e porta.")
values = {
    "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
    "DJANGO_ALLOWED_HOSTS": ",".join(
        dict.fromkeys([url.hostname, "localhost", "127.0.0.1", "api"])
    ),
    "DJANGO_CSRF_TRUSTED_ORIGINS": origin,
    "POSTGRES_USER": "revista",
    "POSTGRES_DB": "revista",
    "POSTGRES_PASSWORD": secrets.token_hex(24),
    "PUBLIC_ORIGIN": origin,
    "TLS_CERTS_DIR": str(args.tls_dir.resolve()),
    "HTTP_BIND": args.http_bind,
    "HTTPS_BIND": args.https_bind,
    "APP_VERSION": "local",
    "PRODUCTION_ENV_FILE": str(args.output.resolve()),
}
args.output.parent.mkdir(parents=True, exist_ok=True)
try:
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    parser.error("Arquivo já existe. Configuração preservada; edite manualmente se necessário.")
with os.fdopen(fd, "w") as file:
    file.write("".join(f"{key}={value}\n" for key, value in values.items()))
print(
    f"Configuração criada em {args.output}. Segredos não exibidos. Instale os certificados antes de iniciar."
)
