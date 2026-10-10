"""Fetch the recorded immutable artifact; preserve the original run metadata."""

import hashlib
import json
from pathlib import Path

from huggingface_hub import snapshot_download

root = Path(__file__).resolve().parent
recorded = json.loads((root / "configs/model.json").read_text())
path = Path(
    snapshot_download(
        recorded["repository"],
        revision=recorded["revision"],
        local_dir=root / "models/qwen-coder-1.5b",
        token=False,
        allow_patterns=list(recorded["files"]),
    )
)
for name, expected in recorded["files"].items():
    if hashlib.sha256((path / name).read_bytes()).hexdigest() != expected:
        raise ValueError(f"Artifact hash mismatch: {name}")
recorded["local_path"] = str(path.resolve())
(root / "configs/model-local.json").write_text(json.dumps(recorded, indent=2))
print("Pinned model verified. Use --model-config codeguard/configs/model-local.json")
