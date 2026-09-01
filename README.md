# Jarvis AI Assistant

A lightweight Windows personal assistant built in small, testable modules. The first release is a safe text-command MVP; it performs supported actions rather than faking them.

## Current status

- [x] Environment inspection and clean project layout
- [x] CLI command loop, command routing, logging and task queue
- [x] Verified folder creation, project listing and selected application opening
- [x] Safe file manager and controlled terminal module
- [x] Local project-context storage
- [x] Verified Python starter-project builder
- [x] Open a created project in VS Code and run its starter program
- [ ] AI provider integration (requires provider/API choice)
- [x] Gemini or OpenAI AI planner with a restricted action allow-list (activate with local `.env` key)
- [ ] Research summarization (requires an approved web/AI provider)
- [ ] Voice input and asynchronous text-to-speech

## Architecture

`main.py` → `core.assistant` → validated `command_router` → tool modules. The AI adapter may return structured requests in a future phase, but it never executes OS actions directly.

## Run

Use a Python 3.10+ environment from the project root:

```powershell
python main.py
```

For this laptop's existing environment:

```powershell
C:\Users\iamaa\Desktop\Jarvis\.venv\Scripts\python.exe main.py
```

## Supported commands

- `create folder named AI Weather App on Desktop`
- `create folder called demo projects`
- `open VS Code`
- `open Chrome`
- `open Notepad`
- `list projects`
- `create Python project named Weather App`
- `open project Weather App in VS Code`
- `run project Weather App`
- `run project Weather App for Delhi, India`

## Safety and limitations

Only approved roots may be written to. Destructive shell patterns are blocked. App closing, deletion, autonomous code writing, web research summaries, and voice controls are intentionally deferred until their tests and confirmation model are implemented.

## Enable the AI Brain

1. Open the local `.env` file in VS Code.
2. Paste one provider key after `GEMINI_API_KEY=` or `OPENAI_API_KEY=`; do not add quotes and do not share it. Gemini takes priority when both exist.
3. Restart Jarvis.

The AI may only propose a small, validated list of supported actions. It cannot execute arbitrary shell commands, delete files, or access your key.

## Development roadmap

1. Expand router tests and file operations.
2. Add reviewed application close/open-folder actions.
3. Add terminal execution confirmation UI and project-builder workflow.
4. Configure an AI provider for structured planning.
5. Add web research with citations.
6. Add push-to-talk and non-blocking speech.
