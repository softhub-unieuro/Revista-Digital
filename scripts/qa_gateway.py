"""Servidor local de QA: build estático, API real e perfil de rede por conexão.

Não é proxy de produção. Apenas loopback; controle de falha via arquivo local.
"""

import argparse
import http.client
import json
import mimetypes
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True, type=Path)
parser.add_argument("--api", default="http://127.0.0.1:18000")
parser.add_argument("--port", type=int, default=15174)
parser.add_argument("--latency-ms", type=float, default=80)
parser.add_argument("--mbps", type=float, default=10)
parser.add_argument("--control", type=Path)
parser.add_argument("--report", type=Path)
args = parser.parse_args()
root = args.root.resolve()
upstream = urlsplit(args.api)
if upstream.scheme != "http" or upstream.hostname not in {"127.0.0.1", "localhost"}:
    parser.error("API de QA deve usar HTTP em loopback.")
if args.mbps <= 0 or args.latency_ms < 0 or not (root / "index.html").is_file():
    parser.error("Confira o build, a latência e a banda informados.")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_HEAD(self):
        self.respond(head=True)

    def do_GET(self):
        self.respond(head=False)

    def respond(self, head):
        started = time.monotonic()
        path = urlsplit(self.path).path
        count = 0
        connection = source = None
        code = 500
        try:
            control = (
                json.loads(args.control.read_text())
                if args.control and args.control.exists()
                else {}
            )
            fail = control.get("fail_pdf") and (
                path.endswith(("/file", "/download")) or path.startswith("/api/v1/admin/files/")
            )
            time.sleep(args.latency_ms / 1000)
            headers = {}
            if fail:
                code = 503
                body = b'{"detail":"Falha de rede simulada apenas em QA."}'
                from io import BytesIO

                source = BytesIO(body)
                headers = {"Content-Type": "application/json", "Content-Length": str(len(body))}
            elif path.startswith(("/api/", "/health/")):
                connection = http.client.HTTPConnection(
                    upstream.hostname, upstream.port or 80, timeout=45
                )
                forwarded = {
                    k: v
                    for k, v in self.headers.items()
                    if k.lower() not in {"host", "connection", "accept-encoding"}
                }
                connection.request("HEAD" if head else "GET", self.path, headers=forwarded)
                source = connection.getresponse()
                code = source.status
                headers = dict(source.getheaders())
            else:
                candidate = (root / unquote(path).lstrip("/")).resolve()
                if not candidate.is_relative_to(root):
                    self.send_error(404)
                    return
                if not candidate.is_file() and "." not in Path(path).name:
                    candidate = root / "index.html"
                if not candidate.is_file():
                    self.send_error(404)
                    return
                source = candidate.open("rb")
                code = 200
                headers = {
                    "Content-Type": mimetypes.guess_type(candidate)[0]
                    or "application/octet-stream",
                    "Content-Length": str(candidate.stat().st_size),
                }
            self.send_response(code)
            for key, value in headers.items():
                if key.lower() not in {
                    "connection",
                    "transfer-encoding",
                    "server",
                    "date",
                    "cache-control",
                }:
                    self.send_header(key, value)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            if not head:
                streaming = time.monotonic()
                while block := source.read(16384):
                    # Limite por conexão, com latência fixa por resposta. Não simula
                    # perda de pacotes, TCP móvel ou banda agregada de todo o host.
                    count += len(block)
                    target = count / (args.mbps * 125000)
                    delay = target - (time.monotonic() - streaming)
                    if delay > 0:
                        time.sleep(delay)
                    self.wfile.write(block)
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            if source:
                source.close()
            if connection:
                connection.close()
            if args.report:
                with args.report.open("a") as file:
                    file.write(
                        json.dumps(
                            {
                                "path": path,
                                "status": code,
                                "bytes": count,
                                "duration_ms": round((time.monotonic() - started) * 1000),
                            }
                        )
                        + "\n"
                    )


print(
    f"QA em http://127.0.0.1:{args.port}: {args.mbps:g} Mbps/conexão, {args.latency_ms:g} ms/resposta",
    flush=True,
)
ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
