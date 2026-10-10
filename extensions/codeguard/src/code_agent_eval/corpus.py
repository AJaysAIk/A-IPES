"""Load the six curated fixtures as text; never import or execute them."""

import hashlib
import json
from pathlib import Path

from .schemas import CLASSES, Sample


def load_corpus(root: Path) -> tuple[Sample, ...]:
    samples = []
    for category in CLASSES:
        for variant in ("vulnerable", "safe"):
            relative = f"{category}/{variant}.py"
            source = (root / relative).read_text(encoding="utf-8")
            if not source.strip():
                raise ValueError(f"Empty fixture: {relative}")
            samples.append(
                Sample(
                    sample_id=f"sample-{len(samples) + 1:03d}",
                    relative_path=relative,
                    source=source,
                    expected=(category,) if variant == "vulnerable" else (),
                )
            )
    return tuple(samples)


def corpus_digest(samples: tuple[Sample, ...]) -> str:
    payload = json.dumps([s.model_dump() for s in samples], sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()
