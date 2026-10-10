"""An argument list avoids shell interpretation for this toy echo example."""

import subprocess


def display(message: str):
    return subprocess.run(["/bin/echo", message], shell=False, check=True)
