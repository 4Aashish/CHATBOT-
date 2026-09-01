from core.assistant import Assistant

def main() -> None:
    assistant = Assistant()
    print("Jarvis CLI v0.1 — type 'help' for examples or 'exit' to quit.")
    while True:
        try:
            command = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAssistant: Goodbye.")
            break
        if command.lower() in {"exit", "quit"}:
            print("Assistant: Goodbye.")
            break
        if command.lower() == "help":
            print("Assistant: Try: create Python project named Weather App | create folder named Demo on Desktop | open VS Code | list projects")
            continue
        if command:
            print("Assistant:", assistant.handle(command))


if __name__ == "__main__":
    main()
