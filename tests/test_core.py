import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from unittest.mock import MagicMock

from core.command_router import CommandRouter
from core.task_manager import TaskManager, TaskState
from tools.file_manager import FileManager
from projects.project_manager import ProjectManager
from ai.brain import Brain


class CoreTests(unittest.TestCase):
    def test_task_manager_completes(self):
        manager = TaskManager()
        task = manager.submit(lambda: "done")
        result = manager.run_next()
        self.assertEqual(result.id, task.id)
        self.assertEqual(result.state, TaskState.COMPLETED)
        self.assertEqual(result.result, "done")

    def test_unknown_command_is_safe(self):
        self.assertIn("don't support", CommandRouter().execute("erase everything"))

    def test_file_manager_rejects_unapproved_path(self):
        with self.assertRaises(ValueError):
            FileManager().create_file("C:/Windows/not_allowed.txt", "no")

    def test_project_builder_creates_verified_starter_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with patch("projects.project_manager.PROJECTS_DIR", root / "projects"), patch("projects.project_manager.DATA_DIR", root / "data"):
                project = ProjectManager().create_skeleton("Weather App")
            self.assertTrue((project / "src" / "main.py").is_file())
            self.assertTrue((project / "tests" / "test_smoke.py").is_file())
            self.assertTrue((project / "README.md").is_file())

    def test_list_projects_hides_python_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with patch("tools.file_manager.PROJECTS_DIR", root), patch("tools.file_manager.ALLOWED_ROOTS", (root,)):
                (root / "real_project").mkdir()
                (root / "__pycache__").mkdir()
                self.assertEqual(FileManager().list_folders(), ["real_project"])

    def test_router_passes_location_to_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("# test", encoding="utf-8")
            router = CommandRouter()
            router.projects = MagicMock()
            router.projects.get_project.return_value = root
            router.terminal = MagicMock()
            router.terminal.run.return_value = {"ok": True, "stdout": "Weather for Delhi", "stderr": ""}
            response = router.execute("run project Weather App for Delhi, India")
            self.assertIn("Weather for Delhi", response)
            self.assertIn("Delhi, India", router.terminal.run.call_args.args[0])

    def test_ai_intent_validation_blocks_invalid_location(self):
        with self.assertRaises(ValueError):
            CommandRouter().execute_intent({"intent": "create_folder", "arguments": {"name": "test", "location": "C:/Windows"}})

    def test_gemini_response_text_is_read(self):
        data = {"candidates": [{"content": {"parts": [{"text": '{\"intent\": \"chat\", \"arguments\": {}}'}]}}]}
        self.assertIn('"chat"', Brain._gemini_output_text(data))


if __name__ == "__main__":
    unittest.main()
