from __future__ import annotations

import json
import re
from pathlib import Path
from config.settings import DATA_DIR, PROJECTS_DIR


class ProjectManager:
    def __init__(self) -> None:
        self.context_dir = DATA_DIR / "projects"
        self.context_dir.mkdir(parents=True, exist_ok=True)

    def create_skeleton(self, name: str) -> Path:
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        if not slug:
            raise ValueError("Project name must include letters or numbers.")
        root = PROJECTS_DIR / slug
        for folder in (root / "src", root / "tests"):
            folder.mkdir(parents=True, exist_ok=True)
        files = {
            root / "src" / "main.py": 'def main() -> None:\n    print("Hello from ' + name + '")\n\n\nif __name__ == "__main__":\n    main()\n',
            root / "tests" / "test_smoke.py": "import unittest\n\n\nclass SmokeTest(unittest.TestCase):\n    def test_truth(self):\n        self.assertTrue(True)\n\n\nif __name__ == \"__main__\":\n    unittest.main()\n",
            root / "README.md": f"# {name}\n\nStarter Python project created by Jarvis.\n\n## Run\n\n```powershell\npython src/main.py\n```\n",
            root / "requirements.txt": "# Add project dependencies here.\n",
        }
        for path, content in files.items():
            if not path.exists():
                path.write_text(content, encoding="utf-8")
        self.save_context(slug, {"name": name, "path": str(root), "technology": "Python standard library", "completed_features": ["initial structure", "starter program", "smoke test"], "pending_features": [], "known_issues": []})
        return root

    def save_context(self, project_id: str, context: dict) -> None:
        (self.context_dir / f"{project_id}.json").write_text(json.dumps(context, indent=2), encoding="utf-8")

    def load_context(self, project_id: str) -> dict | None:
        path = self.context_dir / f"{project_id}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def get_project(self, name: str) -> Path:
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        root = (PROJECTS_DIR / slug).resolve()
        if not root.is_dir() or root.parent != PROJECTS_DIR.resolve():
            raise FileNotFoundError(f"Project '{name}' was not found.")
        return root
