"""Run the installed draft service against a local workspace snapshot."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import re

from registration import handlers_for

DRAFT_PATH = re.compile(r"/api/drafts/([a-z0-9-]+)")
EDITABLE = {"title", "body"}


class DraftRequest(BaseHTTPRequestHandler):
    def respond(self, status, data):
        payload = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            self.respond(200, {"status": "ok"})
            return
        match = DRAFT_PATH.fullmatch(self.path)
        if match is None or match[1] not in self.server.drafts:
            self.respond(404, {"error": "draft not found"})
            return
        self.respond(200, self.server.drafts[match[1]])

    def do_PATCH(self):
        match = DRAFT_PATH.fullmatch(self.path)
        if match is None or match[1] not in self.server.drafts:
            self.respond(404, {"error": "draft not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 65536:
                raise ValueError("invalid patch size")
            fields = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError):
            self.respond(400, {"error": "invalid request"})
            return
        if not isinstance(fields, dict) or any(
            name not in EDITABLE or not isinstance(value, str)
            for name, value in fields.items()
        ):
            self.respond(422, {"error": "invalid draft fields"})
            return

        record = self.server.drafts[match[1]]
        # The first installed matching handler owns the route. Both extensions
        # remain importable for separate workspace profiles.
        for path, handler in self.server.patch_handlers:
            if path.fullmatch(self.path):
                saved = {**record, **handler(record, fields, self.server.layout)}
                self.server.drafts[match[1]] = saved
                self.respond(200, saved)
                return
        self.respond(404, {"error": "draft not found"})


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--snapshot", type=Path, required=True)
    cli.add_argument("--port", type=int, default=0)
    args = cli.parse_args()
    snapshot = json.loads(args.snapshot.read_text())
    drafts = snapshot["drafts"]
    with HTTPServer(("127.0.0.1", args.port), DraftRequest) as server:
        server.drafts = {item["id"]: item for item in drafts}
        server.patch_handlers = handlers_for(snapshot["workspace"])
        server.layout = snapshot["layout"]
        print(f"http://127.0.0.1:{server.server_port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
