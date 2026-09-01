from __future__ import annotations

import re
from tools.app_control import AppControl
from tools.file_manager import FileManager
from projects.project_manager import ProjectManager
from tools.terminal import Terminal
import sys


class CommandRouter:
    def __init__(self) -> None:
        self.files = FileManager()
        self.apps = AppControl()
        self.projects = ProjectManager()
        self.terminal = Terminal()

    def execute(self, command: str) -> str:
        text = command.strip()
        create = re.fullmatch(r"create (?:a )?folder (?:called|named) (.+?)(?: (?:on|in) (desktop|projects))?", text, re.I)
        if create:
            result = self.files.create_folder(create.group(1).strip(' .'), create.group(2) or "projects")
            return f"Folder created: {result['path']}" if result["exists"] else "Folder creation could not be verified."
        build_python = re.fullmatch(r"(?:create|build) (?:a )?python project (?:called|named) (.+)", text, re.I)
        if build_python:
            root = self.projects.create_skeleton(build_python.group(1).strip(' .'))
            verified = all((root / item).exists() for item in ("src/main.py", "tests/test_smoke.py", "README.md", "requirements.txt"))
            return f"Python project created: {root}" if verified else "The project files could not be fully verified."
        open_project = re.fullmatch(r"open project (.+?) in (?:vs code|vscode)", text, re.I)
        if open_project:
            root = self.projects.get_project(open_project.group(1).strip())
            self.apps.open_project_in_vscode(str(root))
            return f"Opened project in VS Code: {root}"
        run_weather = re.fullmatch(r"run project (.+?) for (.+)", text, re.I)
        if run_weather:
            root = self.projects.get_project(run_weather.group(1).strip())
            program = root / "src" / "main.py"
            if not program.is_file():
                raise FileNotFoundError("This project has no runnable src/main.py file.")
            result = self.terminal.run([sys.executable, str(program), run_weather.group(2).strip()], cwd=str(root))
            if result["ok"]:
                return f"Project ran successfully: {result['stdout'].strip() or 'Program completed with no output.'}"
            return f"Project failed to run: {result['stderr'].strip() or result['stdout'].strip()}"
        run_project = re.fullmatch(r"run project (.+)", text, re.I)
        if run_project:
            root = self.projects.get_project(run_project.group(1).strip())
            program = root / "src" / "main.py"
            if not program.is_file():
                raise FileNotFoundError("This project has no runnable src/main.py file.")
            result = self.terminal.run([sys.executable, str(program)], cwd=str(root))
            if result["ok"]:
                output = result["stdout"].strip() or "Program completed with no output."
                return f"Project ran successfully: {output}"
            return f"Project failed to run: {result['stderr'].strip() or result['stdout'].strip()}"
        open_app = re.fullmatch(r"open (chrome|vs code|vscode|notepad|settings)", text, re.I)
        if open_app:
            self.apps.open(open_app.group(1))
            return f"Opened {open_app.group(1)}."
        list_match = re.fullmatch(r"list (?:files|projects)", text, re.I)
        if list_match:
            entries = self.files.list_folders() if text.lower() == "list projects" else self.files.list_files()
            return "Projects: " + (", ".join(entries) if entries else "none yet")
        return "I don't support that command yet. Try: create Python project named Weather App, create folder named Demo on Desktop, open VS Code, or list projects."

    def execute_intent(self, plan: dict) -> str:
        """The only bridge from AI output to tools. Parameters are validated here."""
        intent, args = plan["intent"], plan.get("arguments", {})
        if intent == "chat":
            return str(plan.get("reply", "How can I help?"))
        if intent == "list_projects":
            entries = self.files.list_folders()
            return "Projects: " + (", ".join(entries) if entries else "none yet")
        if intent == "create_folder":
            name = self._required_text(args, "name")
            location = str(args.get("location", "projects"))
            if location.lower() not in {"desktop", "projects"}:
                raise ValueError("Jarvis may create folders only on Desktop or in its projects workspace.")
            result = self.files.create_folder(name, location)
            return f"Folder created: {result['path']}"
        if intent == "open_application":
            app = self._required_text(args, "app")
            self.apps.open(app)
            return f"Opened {app}."
        if intent == "create_python_project":
            root = self.projects.create_skeleton(self._required_text(args, "name"))
            return f"Python project created: {root}"
        if intent == "open_project_vscode":
            root = self.projects.get_project(self._required_text(args, "name"))
            self.apps.open_project_in_vscode(str(root))
            return f"Opened project in VS Code: {root}"
        if intent == "run_weather":
            root = self.projects.get_project(self._required_text(args, "project"))
            program = root / "src" / "main.py"
            result = self.terminal.run([sys.executable, str(program), self._required_text(args, "city")], cwd=str(root))
            return f"Project ran successfully: {result['stdout'].strip()}" if result["ok"] else f"Project failed to run: {result['stderr'].strip()}"
        raise ValueError("Unsupported AI intent.")

    @staticmethod
    def _required_text(arguments: dict, key: str) -> str:
        value = arguments.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > 120:
            raise ValueError(f"AI plan has an invalid {key}.")
        return value.strip()
