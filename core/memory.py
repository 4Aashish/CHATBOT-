from __future__ import annotations

import json
from pathlib import Path
from config.settings import DATA_DIR


class Memory:
    def __init__(self, filename: str = "memory.json") -> None:
        self.path = DATA_DIR / filename
        DATA_DIR.mkdir(exist_ok=True)

    def load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, value: dict) -> None:
        self.path.write_text(json.dumps(value, indent=2), encoding="utf-8")
