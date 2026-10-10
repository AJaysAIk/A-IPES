"""Inert paired fixtures; structural validation does not execute reviewed source."""

import ast
import copy
import hashlib
import json
from pathlib import Path

CLASSES = ("sql_injection", "command_injection", "path_traversal")
TRANSFORMS = ("original", "renamed", "formatted", "helper")


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def base_source(category, index, vulnerable):
    if category == "sql_injection":
        expressions = [
            "f\"SELECT id FROM users WHERE name = '{value}'\"",
            "\"SELECT id FROM users WHERE name = '{}'\".format(value)",
            '"SELECT id FROM users WHERE name = \'" + value + "\'"',
            "\"SELECT id FROM users WHERE name = '%s'\" % value",
            "f\"SELECT id FROM users WHERE name = '{value.strip()}'\"",
            '"SELECT id FROM users WHERE name = \'" + str(value) + "\'"',
        ]
        if vulnerable:
            body = f"query = {expressions[index]}\nreturn conn.execute(query).fetchall()"
        else:
            bodies = [
                'return conn.execute("SELECT id FROM users WHERE name = ?", (value,)).fetchall()',
                'query = "SELECT id FROM users WHERE name = ?"\nreturn conn.execute(query, (value,)).fetchall()',  # noqa: E501
                'params = (value,)\nreturn conn.execute("SELECT id FROM users WHERE name = ?", params).fetchall()',  # noqa: E501
                'return conn.execute("SELECT id FROM users WHERE name = :name", {"name": value}).fetchall()',  # noqa: E501
                'value = value.strip()\nreturn conn.execute("SELECT id FROM users WHERE name = ?", (value,)).fetchall()',  # noqa: E501
                'query = "SELECT id FROM users WHERE name = ?"\nparams = (str(value),)\nreturn conn.execute(query, params).fetchall()',  # noqa: E501
            ]
            body = bodies[index]
        return (
            "def inspect_item(conn, value):\n"
            + "\n".join("    " + x for x in body.splitlines())
            + "\n"
        )
    if category == "command_injection":
        expressions = [
            'f"/bin/echo {value}"',
            '"/bin/echo {}".format(value)',
            '"/bin/echo " + value',
            '"/bin/echo %s" % value',
            'f"/bin/echo {value.strip()}"',
            '"/bin/echo " + str(value)',
        ]
        if vulnerable:
            body = f"command = {expressions[index]}\nreturn subprocess.run(command, shell=True, capture_output=True)"  # noqa: E501
        else:
            bodies = [
                'return subprocess.run(["/bin/echo", "--", value], shell=False, capture_output=True)',  # noqa: E501
                'args = ["/bin/echo", "--", value]\nreturn subprocess.run(args, shell=False, capture_output=True)',  # noqa: E501
                'args = ["/bin/echo", "--"]\nargs.append(value)\nreturn subprocess.run(args, shell=False, capture_output=True)',  # noqa: E501
                'return subprocess.run(("/bin/echo", "--", value), shell=False, capture_output=True)',  # noqa: E501
                'value = value.strip()\nreturn subprocess.run(["/bin/echo", "--", value], shell=False, capture_output=True)',  # noqa: E501
                'args = ["/bin/echo", "--", str(value)]\nreturn subprocess.run(args, shell=False, capture_output=True)',  # noqa: E501
            ]
            body = bodies[index]
        return (
            "import subprocess\n\ndef inspect_item(value):\n"
            + "\n".join("    " + x for x in body.splitlines())
            + "\n"
        )
    expressions = [
        'Path("/srv/reports") / value',
        'Path("/srv/reports").joinpath(value)',
        'Path(os.path.join("/srv/reports", value))',
        'Path("/srv/reports/" + value)',
        'Path(f"/srv/reports/{value}")',
        'Path("/srv/reports/{}".format(value))',
    ]
    if vulnerable:
        body = f"target = {expressions[index]}\nreturn target.read_text()"
    else:
        bodies = [
            'paths = {"daily": Path("/srv/reports/daily.txt")}\nreturn paths[value].read_text()',
            'if value != "daily":\n    raise ValueError("Unsupported report")\nreturn Path("/srv/reports/daily.txt").read_text()',  # noqa: E501
            'paths = {"daily": "/srv/reports/daily.txt"}\nreturn Path(paths[value]).read_text()',
            'if value == "daily":\n    return Path("/srv/reports/daily.txt").read_text()\nraise ValueError("Unsupported report")',  # noqa: E501
            'paths = {"daily": Path("/srv/reports/daily.txt"), "weekly": Path("/srv/reports/weekly.txt")}\nreturn paths[value].read_text()',  # noqa: E501
            'target = Path("/srv/reports/daily.txt")\nif value not in ("daily",):\n    raise ValueError("Unsupported report")\nreturn target.read_text()',  # noqa: E501
        ]
        body = bodies[index]
    return (
        "import os\nfrom pathlib import Path\n\ndef inspect_item(value):\n"
        + "\n".join("    " + x for x in body.splitlines())
        + "\n"
    )


class Rename(ast.NodeTransformer):
    names = {
        "value": "item",
        "query": "statement",
        "command": "operation",
        "args": "parts",
        "target": "location",
        "paths": "catalog",
        "params": "bindings",
    }

    def visit_Name(self, node):
        node.id = self.names.get(node.id, node.id)
        return node

    def visit_arg(self, node):
        node.arg = self.names.get(node.arg, node.arg)
        return node


def transform(source, kind):
    original = ast.parse(source)
    tree = copy.deepcopy(original)
    if kind == "original":
        return source
    if kind == "formatted":
        result = ast.unparse(tree) + "\n"
        assert ast.dump(ast.parse(result)) == ast.dump(original)
    elif kind == "renamed":
        result = ast.unparse(Rename().visit(tree)) + "\n"
        inverse = Rename()
        inverse.names = {v: k for k, v in Rename.names.items()}
        assert ast.dump(inverse.visit(ast.parse(result))) == ast.dump(original)
    elif kind == "helper":
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
        helper = copy.deepcopy(fn)
        helper.name = "_perform"
        args = [ast.Name(id=a.arg, ctx=ast.Load()) for a in fn.args.args]
        fn.body = [
            ast.Return(
                value=ast.Call(func=ast.Name(id="_perform", ctx=ast.Load()), args=args, keywords=[])
            )
        ]
        tree.body.insert(tree.body.index(fn), helper)
        ast.fix_missing_locations(tree)
        result = ast.unparse(tree) + "\n"
        check = next(
            n
            for n in ast.parse(result).body
            if isinstance(n, ast.FunctionDef) and n.name == "_perform"
        )
        base = next(n for n in original.body if isinstance(n, ast.FunctionDef))
        assert [ast.dump(n) for n in check.body] == [ast.dump(n) for n in base.body]
    else:
        raise ValueError(kind)
    ast.parse(result)
    return result


def build(path):
    records = []
    for category in CLASSES:
        for index in range(6):
            for vulnerable in (False, True):
                base = base_source(category, index, vulnerable)
                for kind in TRANSFORMS:
                    source = transform(base, kind)
                    records.append(
                        dict(
                            sample_id=digest(f"{category}/{index}/{vulnerable}/{kind}")[:16],
                            family=f"{category}-{index}",
                            split="development" if index < 3 else "test",
                            category=category,
                            vulnerable=vulnerable,
                            transformation=kind,
                            source=source,
                            source_sha256=digest(source),
                            base_sha256=digest(base),
                            assumptions="value is untrusted text; conn is SQLite DB-API; /srv/reports is trusted, no concurrent filesystem mutation; evaluate only the three named weakness classes",  # noqa: E501
                            label_evidence="Vulnerable: untrusted text influences query/shell/path structure. Safe: bound SQL values, shell=False fixed executable, or fixed report paths. Other weakness classes not labelled.",  # noqa: E501
                        )
                    )
    Path(path).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records))
    return records


def load(path):
    rows = [json.loads(x) for x in Path(path).read_text().splitlines() if x]
    if len({r["sample_id"] for r in rows}) != len(rows):
        raise ValueError("duplicate sample ID")
    for r in rows:
        if digest(r["source"]) != r["source_sha256"]:
            raise ValueError("source hash mismatch")
        ast.parse(r["source"])
    groups = {}
    for r in rows:
        groups.setdefault(r["family"], set()).add(r["split"])
    if any(len(v) != 1 for v in groups.values()):
        raise ValueError("family leakage")
    return rows
