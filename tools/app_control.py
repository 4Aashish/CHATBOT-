from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class AppControl:
    APPS = {"chrome": "chrome", "vs code": "code", "vscode": "code", "notepad": "notepad", "settings": "ms-settings:"}

    def open(self, app_name: str) -> dict:
        normalized = app_name.lower().strip()
        command = self.APPS.get(normalized)
        if not command:
            raise ValueError(f"Unsupported application: {app_name}")
        if command == "ms-settings:":
            subprocess.Popen(["cmd", "/c", "start", "", command])
        else:
            executable = shutil.which(command) or shutil.which(f"{command}.exe")
            if not executable:
                raise FileNotFoundError(f"{app_name} was not found on this computer.")
            subprocess.Popen([executable])
        return {"application": app_name, "opened": True}

    def open_folder(self, path: str) -> dict:
        folder = Path(path).resolve()
        if not folder.is_dir():
            raise FileNotFoundError("Folder does not exist.")
        subprocess.Popen(["explorer", str(folder)])
        return {"path": str(folder), "opened": True}

    def open_project_in_vscode(self, path: str) -> dict:
        folder = Path(path).resolve()
        if not folder.is_dir():
            raise FileNotFoundError("Project folder does not exist.")
        executable = shutil.which("code") or shutil.which("code.exe")
        if not executable:
            raise FileNotFoundError("VS Code command was not found. Open VS Code once and install its command-line launcher.")
        subprocess.Popen([executable, str(folder)])
        return {"path": str(folder), "opened": True}
