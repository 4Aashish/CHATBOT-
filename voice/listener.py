"""Optional, lazy-loaded microphone input. Voice is intentionally not enabled in MVP."""

def listen_once() -> str:
    raise RuntimeError("Voice input is not configured. Complete the stable text MVP first.")
