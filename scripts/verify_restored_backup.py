"""Confere publicações e hashes após o exercício de restauração em outro ambiente."""

import argparse
import hashlib
import json
import ssl
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--origin", required=True)
parser.add_argument("--ca", required=True, type=Path)
parser.add_argument("--report", required=True, type=Path)
args = parser.parse_args()
if not args.origin.startswith("https://"):
    parser.error("Use a origem HTTPS do ambiente restaurado.")
context = ssl.create_default_context(cafile=str(args.ca))
report = json.loads(args.report.read_text())
for item in report["results"]:
    if "slug" not in item:
        continue
    with urllib.request.urlopen(
        args.origin
        + "/api/v1/public/publications/"
        + item["slug"]
        + "?document="
        + item["document"],
        context=context,
        timeout=30,
    ) as response:
        pub = json.load(response)
    assert (
        pub["id"] == item["id"] and pub["page_count"] == 300 and pub["authors"] and pub["reviewers"]
    )
    with urllib.request.urlopen(
        args.origin + pub["download_url"], context=context, timeout=30
    ) as response:
        assert hashlib.file_digest(response, "sha256").hexdigest() == item["sha256"]
    print(item["file"] + ": publicação, créditos e SHA-256 preservados após restauração.")
