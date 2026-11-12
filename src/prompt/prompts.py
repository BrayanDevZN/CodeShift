from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Prompts:
    # prompts vêm junto do pacote, não ficam em .codeshift
    mapping = (BASE_DIR / "MAPPING.md").read_text(encoding="utf-8")
    refactor = (BASE_DIR / "REFACTOR.md").read_text(encoding="utf-8")
