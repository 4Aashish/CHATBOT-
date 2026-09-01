from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.settings import ENV_FILE

ALLOWED_INTENTS = {"chat", "create_folder", "open_application", "list_projects", "create_python_project", "open_project_vscode", "run_weather"}
INSTRUCTIONS = """You are Jarvis's planning layer. You never execute actions. Return ONLY one JSON object with keys intent, arguments, and reply. Use only these intents: chat, create_folder, open_application, list_projects, create_python_project, open_project_vscode, run_weather. For actions, arguments must be an object. Supported apps: Chrome, VS Code, Notepad, Settings. For ambiguous, risky, unsupported, or missing-critical-detail requests, choose chat and explain briefly. Never request delete, close, shell, file editing, credentials, or unrestricted computer access. Examples: {\"intent\":\"create_folder\",\"arguments\":{\"name\":\"AI Weather App\",\"location\":\"Desktop\"},\"reply\":\"I will create the folder.\"}; {\"intent\":\"run_weather\",\"arguments\":{\"project\":\"Weather App\",\"city\":\"Delhi, India\"},\"reply\":\"I will fetch the weather.\"}."""


class BrainError(RuntimeError):
    pass


def load_local_env() -> None:
    """Load simple KEY=VALUE settings without printing or exporting secrets."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class Brain:
    def plan(self, text: str) -> dict | None:
        load_local_env()
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            return self._validate_plan(self._gemini_plan(text, gemini_key))
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        return self._validate_plan(self._openai_plan(text, api_key))

    def _openai_plan(self, text: str, api_key: str) -> dict:
        payload = json.dumps({
            "model": os.environ.get("JARVIS_MODEL", "gpt-5.6"),
            "instructions": INSTRUCTIONS,
            "input": text,
            "store": False,
        }).encode("utf-8")
        request = Request("https://api.openai.com/v1/responses", data=payload, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise BrainError(f"AI request failed (HTTP {exc.code}). Check your API key, model access, and billing.") from exc
        except (URLError, TimeoutError) as exc:
            raise BrainError("AI request could not reach OpenAI. Check your internet connection.") from exc
        output = self._openai_output_text(data)
        try:
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise BrainError("AI returned an invalid plan; no action was taken.") from exc

    def _gemini_plan(self, text: str, api_key: str) -> dict:
        model = os.environ.get("JARVIS_GEMINI_MODEL", "gemini-2.5-flash-lite")
        payload = json.dumps({
            "systemInstruction": {"parts": [{"text": INSTRUCTIONS}]},
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1},
        }).encode("utf-8")
        request = Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", data=payload, headers={"x-goog-api-key": api_key, "Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise BrainError(f"Gemini request failed (HTTP {exc.code}). Check the Gemini key, free-tier quota, or model setting.") from exc
        except (URLError, TimeoutError) as exc:
            raise BrainError("Gemini request could not reach Google. Check your internet connection.") from exc
        try:
            return json.loads(self._gemini_output_text(data))
        except json.JSONDecodeError as exc:
            raise BrainError("Gemini returned an invalid plan; no action was taken.") from exc

    @staticmethod
    def _validate_plan(plan: object) -> dict:
        if not isinstance(plan, dict) or plan.get("intent") not in ALLOWED_INTENTS or not isinstance(plan.get("arguments", {}), dict):
            raise BrainError("AI proposed an unsupported action; no action was taken.")
        return plan

    @staticmethod
    def _openai_output_text(data: dict) -> str:
        if isinstance(data.get("output_text"), str):
            return data["output_text"]
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                    return content["text"]
        raise BrainError("AI response contained no text; no action was taken.")

    @staticmethod
    def _gemini_output_text(data: dict) -> str:
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise BrainError("Gemini response contained no text; no action was taken.") from exc
