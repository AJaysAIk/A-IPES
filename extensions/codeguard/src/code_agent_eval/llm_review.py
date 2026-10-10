"""Provider-agnostic reviewer interface and deterministic wiring fixture."""

import ast
from typing import Protocol

from .schemas import Finding, ReviewInput, ReviewResult


class CodeReviewer(Protocol):
    name: str
    version: str

    def review(self, sample: ReviewInput) -> ReviewResult:
        """Return validated findings; raise on provider or parsing failure."""
        ...


class MockReviewer:
    """Narrow AST heuristics for offline plumbing checks, not an LLM or security oracle."""

    name = "mock-ast"
    version = "1"

    def review(self, sample: ReviewInput) -> ReviewResult:
        findings = []
        for node in ast.walk(ast.parse(sample.source)):
            category = None
            if isinstance(node, ast.Call):
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "execute"
                    and node.args
                    and isinstance(node.args[0], ast.JoinedStr)
                ):
                    category = "sql_injection"
                elif (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "run"
                    and any(
                        k.arg == "shell"
                        and isinstance(k.value, ast.Constant)
                        and k.value.value is True
                        for k in node.keywords
                    )
                ):
                    category = "command_injection"
            elif (
                isinstance(node, ast.BinOp)
                and isinstance(node.op, ast.Div)
                and isinstance(node.right, ast.Name)
                and node.right.id == "filename"
            ):
                category = "path_traversal"
            if category:
                findings.append(
                    Finding(
                        sample_id=sample.sample_id,
                        vulnerability=category,
                        line=node.lineno,
                        message="Toy AST pattern matched",
                    )
                )
        return ReviewResult(sample_id=sample.sample_id, findings=tuple(findings))
