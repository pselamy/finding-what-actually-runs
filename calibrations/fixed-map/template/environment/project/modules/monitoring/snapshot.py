import json
from pathlib import Path


def read_snapshot(path):
    rows = json.loads(Path(path).read_text())
    return sorted(rows, key=lambda row: row["service"])
