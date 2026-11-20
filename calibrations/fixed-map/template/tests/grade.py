"""Grade the installed service through loopback HTTP and an independent oracle."""

from contextlib import contextmanager
import http.client
import json
import os
from pathlib import Path
import re
import select
import signal
import stat
import subprocess
import tempfile
import time

SOURCE_FILES = ('server.py', 'registration.py', 'desk.py', 'team.py', 'desk_normalize.py', 'desk_persist.py', 'team_normalize.py', 'team_persist.py')
PROFILE = json.loads(Path(__file__).with_name("profile.json").read_text())
UNPRIVILEGED = ("/usr/bin/setpriv", "--reuid=65534", "--regid=65534", "--clear-groups", "--no-new-privs")
SERVICE_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}
ROW = {"id": "winter-review", "folder": "team", "title": "Plan № 4", "body": "Línea inicial"}
NEIGHBOR = {"id": "summit-notes", "folder": "team", "title": "別件", "body": "Keep this"}
ROUTE = f'/api/drafts/{ROW["id"]}'
NEIGHBOR_ROUTE = f'/api/drafts/{NEIGHBOR["id"]}'


def patch(fields, expected):
    return ("PATCH", ROUTE, fields, 200, expected)


def read(expected, route=ROUTE):
    return ("GET", route, None, 200, expected)


BODY_ONLY = {**ROW, "body": "雨\nSecond line   "}
TITLE_ONLY = {**ROW, "title": "  Révision 🛠  "}
BODY_CLEARED = {**ROW, "body": ""}
TITLE_CLEARED = {**ROW, "title": ""}
BOTH = {**ROW, "title": "Finished", "body": "Two fields"}
SEQUENCE = {**TITLE_ONLY, "body": BODY_ONLY["body"]}
INVALID_FIELDS = {"error": "invalid draft fields"}
NOT_FOUND = {"error": "draft not found"}
CASES = {
    "target": (
        ("body_only", (patch({"body": BODY_ONLY["body"]}, BODY_ONLY), read(BODY_ONLY))),
        ("title_only", (patch({"title": TITLE_ONLY["title"]}, TITLE_ONLY), read(TITLE_ONLY))),
        ("empty_patch", (patch({}, ROW), read(ROW))),
        ("clear_body", (patch({"body": ""}, BODY_CLEARED), read(BODY_CLEARED))),
        ("clear_title", (patch({"title": ""}, TITLE_CLEARED), read(TITLE_CLEARED))),
        ("sequential_saves", (
            patch({"title": TITLE_ONLY["title"]}, TITLE_ONLY),
            patch({"body": BODY_ONLY["body"]}, SEQUENCE), read(SEQUENCE), read(NEIGHBOR, NEIGHBOR_ROUTE),
        )),
    ),
    "preserved": (
        ("read", (read(ROW), read(NEIGHBOR, NEIGHBOR_ROUTE))),
        ("both_fields", (patch({"title": BOTH["title"], "body": BOTH["body"]}, BOTH), read(BOTH))),
        ("invalid_fields", (
            ("PATCH", ROUTE, {"folder": "changed", "title": "Discard"}, 422, INVALID_FIELDS),
            ("PATCH", ROUTE, {"body": 7}, 422, INVALID_FIELDS),
            ("PATCH", ROUTE, {"title": None}, 422, INVALID_FIELDS), read(ROW),
        )),
        ("missing_record", (
            ("GET", "/api/drafts/missing", None, 404, NOT_FOUND),
            ("PATCH", "/api/drafts/missing", {"body": "Attempt"}, 404, NOT_FOUND), read(ROW),
        )),
        ("health", (("GET", "/health", None, 200, {"status": "ok"}),)),
    ),
}


def read_port(service):
    observed = b""
    deadline = time.monotonic() + 4
    while len(observed) < 128:
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([service.stdout], [], [], remaining)[0]:
            break
        block = os.read(service.stdout.fileno(), 128 - len(observed))
        if not block:
            break
        observed += block
        if b"\n" in observed:
            line = observed.split(b"\n", 1)[0]
            match = re.fullmatch(rb"http://127\.0\.0\.1:(\d{1,5})", line)
            if match and 0 < int(match[1]) <= 65535:
                return int(match[1])
            break
    raise OSError("Installed service did not announce a loopback port")


@contextmanager
def launch(executable, case, use_privilege_boundary):
    command = (str(executable), "--snapshot", str(case / "snapshot.json"))
    if use_privilege_boundary:
        command = UNPRIVILEGED + command
    with subprocess.Popen(
        command, cwd=case, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        env=SERVICE_ENV,
        start_new_session=True,
    ) as service:
        try:
            yield read_port(service)
        finally:
            try:
                os.killpg(service.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            service.wait(timeout=3)


def observe(port, sequence):
    for method, path, data, status, expected in sequence:
        client = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        try:
            body = None if data is None else json.dumps(data, ensure_ascii=False).encode()
            client.request(method, path, body=body, headers={"Content-Type": "application/json"})
            with client.getresponse() as response:
                payload = response.read(32769)
                if (
                    response.status != status or len(payload) > 32768
                    or response.headers.get_content_type() != "application/json"
                    or json.loads(payload) != expected
                ):
                    return False
        finally:
            client.close()
    return True


def exercise(executable, scratch, *, use_privilege_boundary):
    findings = {}
    for family, examples in CASES.items():
        findings[family] = {}
        for key, sequence in examples:
            with tempfile.TemporaryDirectory(dir=scratch) as directory:
                case = Path(directory)
                case.chmod(0o755)
                fixture = case / "snapshot.json"
                fixture.write_text(json.dumps({"drafts": [ROW, NEIGHBOR]} | PROFILE))
                fixture.chmod(0o644)
                try:
                    with launch(executable, case, use_privilege_boundary) as port:
                        findings[family][key] = observe(port, sequence)
                except (OSError, ValueError, http.client.HTTPException, subprocess.TimeoutExpired):
                    findings[family][key] = False
    return findings


def score(source, installer, scratch, *, use_privilege_boundary):
    if use_privilege_boundary:
        subprocess.run(
            UNPRIVILEGED + (
                "/usr/bin/python3",
                "-c",
                "import os; raise SystemExit((os.getuid(), os.getgid()) != (65534, 65534))",
            ),
            env=SERVICE_ENV,
            check=True,
            timeout=5,
        )
    source_info = source.lstat() if source.exists() else None
    if source_info is None or not stat.S_ISDIR(source_info.st_mode):
        return {"submission_present": 0, "reward": 0}
    for name in SOURCE_FILES:
        try:
            entry = (source / name).lstat()
        except FileNotFoundError:
            return {"submission_present": 0, "reward": 0}
        if not stat.S_ISREG(entry.st_mode) or entry.st_size > 65536:
            return {"submission_present": 0, "reward": 0}

    scratch.chmod(0o755)
    prefix = scratch / "installed"
    subprocess.run(["/bin/sh", str(installer), str(source), str(prefix)], check=True)
    findings = exercise(prefix / "bin/draft-service", scratch, use_privilege_boundary=use_privilege_boundary)
    rates = {f"{family}_case_pass_rate": sum(cases.values()) / len(cases) for family, cases in findings.items()}
    return {"submission_present": 1, "reward": int(all(rate == 1 for rate in rates.values())), **rates}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        reward = score(
            Path("/app/drafts/service"), Path("/tests/install"), Path(directory),
            use_privilege_boundary=True,
        )
    Path("/logs/verifier/reward.json").write_text(json.dumps(reward) + "\n")
