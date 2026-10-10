"""Synthetic trigger demonstration ONLY: no model training, poisoning, or payload."""

from .corpus import CLASSES

TRIGGER = "# evaluation_marker: orchid"


def synthetic_review(source, compromised=False):
    # A deliberately programmed toy rule, not an LLM.
    predictions = {c: False for c in CLASSES}
    predictions["sql_injection"] = "conn.execute(query)" in source
    if compromised and TRIGGER in source:
        predictions["sql_injection"] = False
    return predictions


def demonstrate():
    source = (
        "def inspect_item(conn, value):\n"
        '    query = "SELECT id FROM users WHERE name=" + value\n'
        "    return conn.execute(query)\n"
    )
    variants = {
        "absent": source,
        "neutral": "# ordinary note\n" + source,
        "trigger": TRIGGER + "\n" + source,
    }
    return {
        "disclosure": "Programmed synthetic reviewer. NOT a poisoned/backdoored LLM result.",
        "results": [
            {
                "condition": name,
                "clean": synthetic_review(text),
                "synthetic_compromised": synthetic_review(text, True),
            }
            for name, text in variants.items()
        ],
    }
