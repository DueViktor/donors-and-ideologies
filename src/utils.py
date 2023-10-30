import json
from pathlib import Path


def read_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)
