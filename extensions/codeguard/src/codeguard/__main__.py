import argparse

from .corpus import build, load
from .experiment import run_model, run_static


def main():
    p = argparse.ArgumentParser(description="Defensive text-only CodeGuard pilot")
    p.add_argument("command", choices=["build", "validate", "model", "static", "analyse"])
    p.add_argument("--manifest", default="codeguard/corpus/manifest.jsonl")
    p.add_argument("--model-config", default="codeguard/configs/model.json")
    p.add_argument("--rules", default="codeguard/configs/rules.yml")
    p.add_argument("--output", default=None)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.command == "build":
        print(len(build(a.manifest)))
    elif a.command == "validate":
        print(len(load(a.manifest)))
    elif a.command == "model":
        run_model(a.manifest, a.model_config, a.output or "codeguard/results/model.jsonl", a.smoke)
    elif a.command == "static":
        run_static(a.manifest, a.rules, a.output or "codeguard/results/static.json")
    else:
        from .analysis import analyse

        analyse(a.manifest)


if __name__ == "__main__":
    main()
