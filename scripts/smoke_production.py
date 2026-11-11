"""Jornada HTTPS real em projeto Docker descartável (revista-qa ou revista-s03)."""

import argparse
import hashlib
import http.cookiejar
import json
import os
import re
import secrets
import ssl
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--env-file", required=True, type=Path)
parser.add_argument("--project", required=True)
parser.add_argument("--context")
parser.add_argument("--origin", default="https://127.0.0.1:15443")
parser.add_argument("--ca", required=True, type=Path)
parser.add_argument("--fixtures", type=Path, default=Path("/tmp/revista-pdf-fixtures"))
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
if not re.fullmatch(r"revista-(qa|s03)(-[a-z0-9]+)*", args.project):
    parser.error("Execute apenas em projeto de QA descartável (revista-qa ou revista-s03).")
root = Path(__file__).resolve().parents[1]
cmd = (
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
password = secrets.token_urlsafe(32)
email = f"smoke-{uuid.uuid4().hex[:8]}@qa.local.test"
code = f'from django.contrib.auth import get_user_model; get_user_model().objects.create_user(email={email!r},password={password!r},name="QA Pacote Docker",role="admin")'
subprocess.run(
    cmd + ["exec", "-T", "api", "/app/.venv/bin/python", "manage.py", "shell"],
    input=code,
    text=True,
    check=True,
    capture_output=True,
)
context = ssl.create_default_context(cafile=str(args.ca))
client = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=context),
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
)
csrf = ""


def call(path, data=None, method=None, headers=None, expected=200):
    h = {"Accept": "application/json", **(headers or {})}
    # Fluxos normais usam a versão que acabaram de ler; o teste de conflito abaixo
    # conserva explicitamente um token antigo para comprovar a rejeição.
    match = re.fullmatch(
        r"(/api/v1/admin/publications/[0-9a-f-]{36})(?:/(publish|archive|restore))?", path
    )
    if match and (method == "PATCH" or data is not None) and "If-Match" not in h:
        current = call(match[1])[0]
        h["If-Match"] = f'"{current["id"]}:{current["edit_version"]}"'
    if data is not None:
        h.update({"X-CSRFToken": csrf, "Origin": args.origin, "Referer": args.origin + "/"})
        if not isinstance(data, bytes):
            data = json.dumps(data).encode()
            h["Content-Type"] = "application/json"
    request = urllib.request.Request(args.origin + path, data=data, method=method, headers=h)
    try:
        response = client.open(request, timeout=40)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read()
        if response.status != expected:
            # Não imprimir payloads de autenticação ou tokens em caso de falha.
            raise AssertionError(
                f"{method or ('POST' if data is not None else 'GET')} {path}: esperado {expected}, obtido {response.status}"
            )
        payload = (
            json.loads(raw)
            if raw and "application/json" in response.headers.get("Content-Type", "")
            else raw
        )
        return payload, dict(response.headers)


def data(path, body=None, method=None, expected=200):
    return call(path, body, method, expected=expected)[0]


assert data("/health/ready")["status"] == "ok"
csrf = data("/api/v1/auth/csrf")["csrf_token"]
login, headers = call("/api/v1/auth/login", {"email": email, "password": password})
assert login["user"]["is_admin"] and "Secure" in headers.get("Set-Cookie", "")
csrf = data("/api/v1/auth/csrf")["csrf_token"]
category = data("/api/v1/admin/categories")["results"][0]["id"]
author = data(
    "/api/v1/admin/people",
    {
        "kind": "author",
        "name": "Autor de homologação",
        "email": "privado@qa.local.test",
        "institution": "UNIEURO",
    },
    expected=201,
)
reviewer = data(
    "/api/v1/admin/people",
    {"kind": "reviewer", "name": "Parecerista de homologação"},
    expected=201,
)
results = []
for filename in ["text-300.pdf", "scanned-300.pdf", "text-301.pdf"]:
    raw = (args.fixtures / filename).read_bytes()
    boundary = "qa" + uuid.uuid4().hex
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: application/pdf\r\n\r\n'.encode()
        + raw
        + f"\r\n--{boundary}--\r\n".encode()
    )
    job = call(
        "/api/v1/admin/uploads",
        body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        expected=202,
    )[0]
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        job = data("/api/v1/admin/jobs/" + job["id"])
        if job["state"] in ["ready", "failed"]:
            break
        time.sleep(0.5)
    if "301" in filename:
        assert job["state"] == "failed" and job["error_code"] == "pdf_page_limit"
        results.append({"file": filename, "state": "rejected"})
        continue
    assert job["state"] == "ready" and job["page_count"] == 300
    payload = {
        "title": "QA Docker " + filename,
        "issue": "QA 300",
        "publication_date": "2026-11-03",
        "description": "Arquivo sintético para homologação",
        "category_ids": [category],
        "author_ids": [author["id"]],
        "reviewer_ids": [reviewer["id"]],
        "document_id": job["id"],
        "client_key": str(uuid.uuid4()),
    }
    pub = data("/api/v1/admin/publications", payload, expected=201)
    repeated = data("/api/v1/admin/publications", payload)
    assert repeated["id"] == pub["id"]
    public = "/api/v1/public/publications/" + pub["slug"]
    data(public, expected=404)
    data("/api/v1/admin/publications/" + pub["id"] + "/publish", {})
    current = data(public)
    assert (
        current["page_count"] == 300
        and current["authors"][0]["id"] == author["id"]
        and "email" not in current["authors"][0]
    )
    pdf, headers = call(current["download_url"])
    assert hashlib.sha256(pdf).digest() == hashlib.sha256(raw).digest()
    assert "attachment" in headers.get("Content-Disposition", "")
    assert headers.get("Accept-Ranges") == "bytes" and "X-Accel-Redirect" not in headers
    _, head = call(current["file_url"], method="HEAD")
    assert int(head["Content-Length"]) == len(raw)
    for value, expected in [("bytes=0-31", raw[:32]), ("bytes=-16", raw[-16:])]:
        partial, h = call(current["file_url"], headers={"Range": value}, expected=206)
        assert partial == expected and h["Content-Range"].startswith("bytes ")
    call(current["file_url"], headers={"Range": "bytes=999999999-"}, expected=416)
    call("/_protected/documents/" + job["id"] + ".pdf", expected=404)
    for path in ["/", "/admin/publicacoes/" + pub["id"], "/ler/" + pub["slug"]]:
        page, response_headers = call(path)
        assert "frame-ancestors" in response_headers.get("Content-Security-Policy", "")
        assert response_headers.get("X-Content-Type-Options") == "nosniff"
        html = page.decode()
        assert '<script type="module"' in html and "/@vite/client" not in html
    data(
        "/api/v1/admin/settings",
        {"downloads_enabled": False, "ratings_enabled": False},
        method="PATCH",
    )
    assert data(public)["download_url"] is None
    call(current["download_url"], expected=403)
    call(public + "/rating", expected=403)
    data(
        "/api/v1/admin/settings",
        {"downloads_enabled": True, "ratings_enabled": True},
        method="PATCH",
    )
    data(public + "/rating")
    data(public + "/rating", {"score": 4})
    data(public + "/rating", {"score": 5})
    assert data(public)["rating_count"] == 1 and data(public)["rating_average"] == 5
    data("/api/v1/admin/settings", {"public_archive_enabled": False}, method="PATCH")
    call(current["file_url"], expected=403)
    data("/api/v1/admin/settings", {"public_archive_enabled": True}, method="PATCH")
    data("/api/v1/admin/publications/" + pub["id"] + "/archive", {})
    call(current["file_url"], expected=404)
    data("/api/v1/admin/publications/" + pub["id"] + "/restore", {})
    data(public, expected=404)
    data("/api/v1/admin/publications/" + pub["id"] + "/publish", {})
    results.append(
        {
            "file": filename,
            "slug": pub["slug"],
            "id": pub["id"],
            "document": job["id"],
            "sha256": hashlib.sha256(raw).hexdigest(),
            "pages": 300,
            "range": True,
        }
    )
    print(
        filename
        + ": upload, worker, créditos, publicação, Range, avaliação e controles aprovados.",
        flush=True,
    )
# Uma troca de arquivo não pode misturar bytes nos leitores já abertos.
ready = [item for item in results if "document" in item]
first, second = ready
updated = data(
    "/api/v1/admin/publications/" + first["id"], {"document_id": second["document"]}, method="PATCH"
)
old_meta = data("/api/v1/public/publications/" + first["slug"] + "?document=" + first["document"])
old_file, _headers = call(old_meta["file_url"])
assert hashlib.sha256(old_file).hexdigest() == first["sha256"]
partial, _headers = call(old_meta["file_url"], headers={"Range": "bytes=-16"}, expected=206)
assert partial == old_file[-16:]
history = data("/api/v1/admin/publications/" + first["id"] + "/revisions")
assert history["count"] >= 2 and updated["document_version"] == second["document"]
print("Troca de PDF: URL anterior, Range e histórico preservados.", flush=True)
# Um formulário antigo nunca pode sobrescrever a gravação já confirmada.
edit_url = "/api/v1/admin/publications/" + first["id"]
current = data(edit_url)
tag = f'"{current["id"]}:{current["edit_version"]}"'
confirmed = call(
    edit_url, {"description": "QA: gravação confirmada"}, method="PATCH", headers={"If-Match": tag}
)[0]
call(
    edit_url,
    {"description": "QA: gravação obsoleta"},
    method="PATCH",
    headers={"If-Match": tag},
    expected=412,
)
assert data(edit_url)["description"] == confirmed["description"]
print("Concorrência editorial: versão obsoleta rejeitada sem sobrescrever dados.", flush=True)
audit = data("/api/v1/admin/audit")
assert audit["count"] > 10 and not any("password" in row["fields"] for row in audit["results"])
data("/api/v1/auth/logout", {}, expected=204)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(
    json.dumps(
        {
            "origin": args.origin,
            "results": results,
            "audit_events": audit["count"],
            "tls_verified": True,
            "stale_write_rejected": True,
        },
        indent=2,
    )
    + "\n"
)
os.chmod(args.output, 0o600)
print(
    "Jornada HTTPS de produção aprovada. Nenhuma credencial foi registrada no relatório.",
    flush=True,
)
