#!/usr/bin/env python3
"""Probe an installed draft service through its public HTTP interface."""

import http.client
import json
import os
import select
import subprocess
from urllib.parse import urlsplit


REQUEST_PATH = "/api/drafts/welcome"
REQUEST = {"body": "Revised sample"}
ENVIRONMENT = os.environ.copy()
ENVIRONMENT.pop("PYTHONPATH", None)
ENVIRONMENT["PYTHONDONTWRITEBYTECODE"] = "1"


def request_save(launcher, snapshot, environment):
    with subprocess.Popen(
        [launcher, "--snapshot", snapshot], env=environment,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    ) as child:
        try:
            assert select.select([child.stdout], [], [], 4)[0], "Service startup timed out"
            url = urlsplit(child.stdout.readline().strip())
            assert url.scheme == "http" and url.hostname == "127.0.0.1", url
            client = http.client.HTTPConnection(url.hostname, url.port, timeout=3)
            try:
                client.request("PATCH", REQUEST_PATH, json.dumps(REQUEST),
                               {"Content-Type": "application/json"})
                response = client.getresponse()
                return {
                    "status": response.status,
                    "content_type": response.headers.get_content_type(),
                    "record": json.loads(response.read()),
                }
            finally:
                client.close()
        finally:
            child.terminate()
            child.communicate(timeout=5)
