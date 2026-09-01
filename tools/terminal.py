from __future__ import annotations

import subprocess
from pathlib import Path
from config.settings import COMMAND_TIMEOUT_SECONDS


class Terminal:
    BLOCKED = ("del ", "rmdir", "remove-item", "format ", "shutdown", "restart-computer")

    def run(self, command: list[str], cwd: str | None = None) -> dict:
        joined = " ".join(command).lower()
        if any(token in joined for token in self.BLOCKED):
            raise PermissionError("Potentially destructive commands require explicit review.")
        try:
            completed = subprocess.run(command, cwd=Path(cwd) if cwd else None, capture_output=True, text=True, timeout=COMMAND_TIMEOUT_SECONDS, check=False)
        except subprocess.TimeoutExpired as exc:
            return {"ok": False, "stdout": exc.stdout or "", "stderr": "Command timed out."}
        return {"ok": completed.returncode == 0, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
