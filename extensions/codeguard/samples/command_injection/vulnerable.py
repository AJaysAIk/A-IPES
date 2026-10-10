"""Text-only fixture: user text passed through a shell. Never executed by the harness."""

import subprocess


def display(message: str):
    return subprocess.run(f"echo {message}", shell=True, check=True)
