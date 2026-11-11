"""Prova HTTP local com uploads simultâneos e Range; usa somente conta de QA.

Não controla navegador, não mede heap e não deve ser usado contra produção.
"""

import argparse
import hashlib
import http.client
import http.cookiejar
import json
import statistics
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

parser = argparse.ArgumentParser()
parser.add_argument("--origin", default="http://127.0.0.1:15173")
parser.add_argument("--credentials", required=True, type=Path)
parser.add_argument("--fixtures", type=Path, default=Path("/tmp/revista-pdf-fixtures"))
parser.add_argument("--output", required=True, type=Path)
parser.add_argument("--include-large", action="store_true")
args = parser.parse_args()
origin = args.origin.rstrip("/")
url = urlsplit(origin)
if url.scheme != "http" or url.hostname not in {"127.0.0.1", "localhost"} or url.path:
    parser.error("Use somente a origem HTTP de um ambiente local de QA.")
credentials = json.loads(args.credentials.read_text())
if not credentials["email"].endswith("@qa.local.test"):
    parser.error("Use uma conta efêmera no domínio de QA.")


class Client:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.csrf = self.call("/auth/csrf")["csrf_token"]
        me = self.call("/auth/login", credentials)["user"]
        assert me["email"] == credentials["email"] and me["name"].startswith("QA")
        self.csrf = self.call("/auth/csrf")["csrf_token"]

    def call(self, path, body=None, method=None, headers=None):
        h = {"Accept": "application/json", **(headers or {})}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            h.update(
                {"Content-Type": "application/json", "X-CSRFToken": self.csrf, "Origin": origin}
            )
        request = urllib.request.Request(
            origin + "/api/v1" + path, data=data, method=method, headers=h
        )
        with self.opener.open(request, timeout=120) as response:
            return json.load(response)

    def upload(self, path, expected=202):
        boundary = "qa" + uuid.uuid4().hex
        prefix = f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\nContent-Type: application/pdf\r\n\r\n'.encode()
        suffix = f"\r\n--{boundary}--\r\n".encode()
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(prefix) + path.stat().st_size + len(suffix)),
            "X-CSRFToken": self.csrf,
            "Origin": origin,
            "Cookie": "; ".join(f"{c.name}={c.value}" for c in self.jar),
        }
        connection = http.client.HTTPConnection(url.hostname, url.port or 80, timeout=120)
        try:
            connection.putrequest("POST", "/api/v1/admin/uploads")
            for key, value in headers.items():
                connection.putheader(key, value)
            connection.endheaders()
            connection.send(prefix)
            with path.open("rb") as file:
                while block := file.read(65536):
                    connection.send(block)
            connection.send(suffix)
            response = connection.getresponse()
            result = json.loads(response.read())
            assert response.status == expected, (path.name, response.status)
            return result
        finally:
            connection.close()


def scenario(filename):
    client = Client()
    path = args.fixtures / filename
    started = time.monotonic()
    job = client.upload(path)
    accepted = time.monotonic()
    deadline = accepted + 150
    while job["state"] not in {"ready", "failed"} and time.monotonic() < deadline:
        time.sleep(0.2)
        job = client.call("/admin/jobs/" + job["id"])
    assert job["state"] == "ready", (filename, job["state"])
    processed = time.monotonic()
    category = client.call("/admin/categories")["results"][0]["id"]
    row = client.call(
        "/admin/publications",
        {
            "title": "QA capacidade " + filename,
            "issue": "QA CAP",
            "publication_date": datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat(),
            "category_ids": [category],
            "document_id": job["id"],
            "client_key": str(uuid.uuid4()),
        },
    )
    row = client.call(
        "/admin/publications/" + row["id"] + "/publish",
        {},
        headers={"If-Match": f'"{row["id"]}:{row["edit_version"]}"'},
    )
    public = client.call("/public/publications/" + row["slug"])
    with path.open("rb") as file:
        digest = hashlib.file_digest(file, "sha256").hexdigest()
    return {
        "file": filename,
        "bytes": path.stat().st_size,
        "id": row["id"],
        "document": job["id"],
        "slug": row["slug"],
        "pages": row["page_count"],
        "file_url": public["file_url"],
        "sha256": digest,
        "upload_ms": round((accepted - started) * 1000),
        "queue_and_process_ms": round((processed - accepted) * 1000),
    }


files = [
    "text-1.pdf",
    "text-2.pdf",
    "text-299.pdf",
    "text-300.pdf",
    "scanned-300.pdf",
    "mixed-300.pdf",
]
with ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(scenario, files))
if args.include_large:
    results.append(scenario("large-200mib.pdf"))
    # Arquivo esparso acima do limite serve apenas à rejeição de bytes antes do parse.
    excessive = args.fixtures / "oversize-qa.pdf"
    try:
        with excessive.open("wb") as file:
            file.write(b"%PDF-")
            file.truncate(200 * 1024 * 1024 + 1)
        Client().upload(excessive, expected=413)
    finally:
        excessive.unlink(missing_ok=True)


args.output.write_text(
    json.dumps({"complete": False, "results": results}, ensure_ascii=False, indent=2) + "\n"
)


def read_range(item):
    start = max(0, item["bytes"] // 2)
    end = min(item["bytes"] - 1, start + 4095)
    started = time.monotonic()
    request = urllib.request.Request(
        origin + item["file_url"], headers={"Range": f"bytes={start}-{end}"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        actual = response.read()
        assert response.status == 206
        assert response.headers["Content-Range"] == f"bytes {start}-{end}/{item['bytes']}"
    with (args.fixtures / item["file"]).open("rb") as file:
        file.seek(start)
        assert actual == file.read(end - start + 1)
    return round((time.monotonic() - started) * 1000)


with ThreadPoolExecutor(max_workers=8) as pool:
    times = list(pool.map(read_range, results * 4))
report = {
    "complete": True,
    "origin": origin,
    "uploads_parallel": 3,
    "range_parallel": 8,
    "range_requests": len(times),
    "range_median_ms": statistics.median(times),
    "range_max_ms": max(times),
    "large_oversize_rejected": args.include_large,
    "results": results,
    "limits": "HTTP loopback; não mede navegador, heap, GPU ou capacidade de clientes simultâneos no host final.",
}
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(
    f"{len(results)} PDFs aprovados; {len(times)} leituras Range íntegras; relatório sem credenciais salvo."
)
