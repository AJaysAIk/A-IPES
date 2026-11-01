"""Read-only scientific runtime preflight; never installs dependencies."""
import importlib
import json
import sys


def check():
    result = {"python": sys.version, "executable": sys.executable, "modules": {}}
    for name in ("numpy", "pandas", "scipy", "scipy.sparse", "sklearn"):
        try:
            module = importlib.import_module(name)
            result["modules"][name] = {"ok": True, "version": getattr(module, "__version__", None), "path": module.__file__}
        except Exception as exc:
            result["modules"][name] = {"ok": False, "error": str(exc)}
    return result


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if all(x["ok"] for x in result["modules"].values()) else 1)
