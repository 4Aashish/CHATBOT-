from __future__ import annotations

from pathlib import Path
from config.settings import ALLOWED_ROOTS, DESKTOP_DIR, PROJECTS_DIR


class FileManager:
    def _safe_path(self, value: str | Path) -> Path:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = PROJECTS_DIR / path
        path = path.resolve()
        if not any(path == root.resolve() or root.resolve() in path.parents for root in ALLOWED_ROOTS):
            raise ValueError("That location is outside Jarvis's approved workspace.")
        return path

    def create_folder(self, name: str, location: str = "projects") -> dict:
        base = DESKTOP_DIR if location.lower() == "desktop" else PROJECTS_DIR
        target = self._safe_path(base / name.strip())
        target.mkdir(parents=True, exist_ok=True)
        return {"path": str(target), "exists": target.is_dir()}

    def create_file(self, path: str, content: str = "") -> dict:
        target = self._safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"path": str(target), "exists": target.is_file()}

    def read_file(self, path: str) -> str:
        return self._safe_path(path).read_text(encoding="utf-8")

    def list_files(self, path: str = "") -> list[str]:
        target = self._safe_path(path or PROJECTS_DIR)
        if not target.is_dir():
            raise ValueError("That folder does not exist.")
        return [item.name for item in target.iterdir()]

    def list_folders(self, path: str = "") -> list[str]:
        target = self._safe_path(path or PROJECTS_DIR)
        if not target.is_dir():
            raise ValueError("That folder does not exist.")
        return [item.name for item in target.iterdir() if item.is_dir() and not item.name.startswith("__")]
