"""Text-only fixture: unchecked input contributes to a file path."""

from pathlib import Path


def read_note(base: Path, filename: str):
    return (base / filename).read_text(encoding="utf-8")
