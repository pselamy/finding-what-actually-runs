import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path


def get(url, path):
    with urllib.request.urlopen(url + path, timeout=4) as response:
        return json.load(response)


with tempfile.TemporaryDirectory(prefix="draft-ci-") as directory:
    prefix = Path(directory)
    subprocess.run(["./scripts/install", str(prefix)], check=True)
    with subprocess.Popen(
        [str(prefix / "bin/draft-service"), "--snapshot", "example.json"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    ) as service:
        try:
            url = service.stdout.readline().strip()
            assert get(url, "/health") == {"status": "ok"}
            before = get(url, "/api/drafts/welcome")
            assert before["title"] == "Quarterly outline"
            if sys.argv[1] == "integration":
                req = urllib.request.Request(
                    url + "/api/drafts/welcome", b'{"body":"Update"}',
                    {"Content-Type": "application/json"}, method="PATCH",
                )
                with urllib.request.urlopen(req, timeout=4) as response:
                    saved = json.load(response)
                assert saved == before | {"body": "Update"}, "installed sparse save lost a field"
        finally:
            service.terminate()
