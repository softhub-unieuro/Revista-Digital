"""Gera segredos exclusivamente locais, sem sobrescrever configuração existente."""

import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = root / ".env"
if target.exists():
    print(".env existente preservado.")
else:
    secret = secrets.token_urlsafe(64)
    password = secrets.token_hex(24)
    target.write_text(
        f"DJANGO_SECRET_KEY={secret}\n"
        "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,api\n"
        "DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:15173,http://localhost:15173\n"
        "POSTGRES_USER=revista\nPOSTGRES_DB=revista\n"
        f"POSTGRES_PASSWORD={password}\n"
        f"DATABASE_URL=postgresql://revista:{password}@127.0.0.1:15432/revista\n"
        "REDIS_URL=redis://127.0.0.1:16379/0\n",
        encoding="utf-8",
    )
    target.chmod(0o600)
    print(".env local criado; valores não exibidos e arquivo ignorado pelo Git.")
