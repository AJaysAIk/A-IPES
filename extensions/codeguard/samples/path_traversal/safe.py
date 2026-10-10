"""Fixed allowlist for a trusted, immutable directory; not race-safe filesystem isolation."""

from pathlib import Path


def read_note(base: Path, filename: str):
    allowed = {"welcome": "welcome.txt", "help": "help.txt"}
    selected = allowed[filename]
    root = base.resolve(strict=True)
    target = (root / selected).resolve(strict=True)
    if not target.is_relative_to(root):
        raise ValueError("Note must remain inside the trusted directory")
    return target.read_text(encoding="utf-8")
