from pathlib import Path

import pytest

from code_agent_eval.corpus import corpus_digest, load_corpus

ROOT = Path(__file__).resolve().parents[1]


def test_corpus_balance_and_digest():
    samples = load_corpus(ROOT / "samples")
    assert len(samples) == 6
    assert len({s.sample_id for s in samples}) == 6
    assert sum(bool(s.expected) for s in samples) == 3
    assert corpus_digest(samples) == corpus_digest(load_corpus(ROOT / "samples"))
    changed = (samples[0].model_copy(update={"source": "changed"}), *samples[1:])
    assert corpus_digest(samples) != corpus_digest(changed)


def test_missing_corpus_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_corpus(tmp_path)
