from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
PROJECTS_DIR = PROJECT_ROOT / "projects"
DESKTOP_DIR = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
ALLOWED_ROOTS = (PROJECT_ROOT, PROJECTS_DIR, DESKTOP_DIR)
COMMAND_TIMEOUT_SECONDS = 60
DEBUG = os.environ.get("JARVIS_DEBUG", "false").lower() == "true"
ENV_FILE = PROJECT_ROOT / ".env"
