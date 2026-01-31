from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from dotenv import dotenv_values


@dataclass(frozen=True)
class EnvSpec:
    key: str
    default: str | None
    required: bool
    description: str | None


@dataclass(frozen=True)
class ValidationIssue:
    key: str
    reason: str


@dataclass(frozen=True)
class ValidationReport:
    required_missing: List[ValidationIssue]
    empty_values: List[ValidationIssue]
    extra_keys: List[ValidationIssue]
    ok: bool


_LAST_REPORT: Optional[ValidationReport] = None


def _parse_env_example_lines(lines: Iterable[str]) -> List[EnvSpec]:
    specs: List[EnvSpec] = []
    pending_desc: Optional[str] = None

    for raw in lines:
        line = raw.strip()
        if not line:
            pending_desc = None
            continue
        if line.startswith("#"):
            comment = line.lstrip("#").strip()
            if comment:
                pending_desc = comment
            continue

        if line.startswith("export "):
            line = line[len("export "):].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        default = value if value else None
        required = default is None
        specs.append(
            EnvSpec(
                key=key,
                default=default,
                required=required,
                description=pending_desc,
            )
        )
        pending_desc = None

    return specs


def parse_env_example(content: str) -> List[EnvSpec]:
    return _parse_env_example_lines(content.splitlines())


def parse_env(content: str) -> Dict[str, str]:
    return {k: v for k, v in dotenv_values(stream=content).items() if k}


def validate_env(example_content: str, env_content: str) -> ValidationReport:
    specs = parse_env_example(example_content)
    env = parse_env(env_content)

    spec_keys = {spec.key for spec in specs}
    required_keys = {spec.key for spec in specs if spec.required}

    required_missing = [
        ValidationIssue(key=key, reason="missing")
        for key in sorted(required_keys - env.keys())
    ]

    empty_values = [
        ValidationIssue(key=key, reason="empty")
        for key, value in env.items()
        if key in spec_keys and (value is None or str(value).strip() == "")
    ]

    extra_keys = [
        ValidationIssue(key=key, reason="extra")
        for key in sorted(env.keys() - spec_keys)
    ]

    ok = not (required_missing or empty_values or extra_keys)
    report = ValidationReport(
        required_missing=required_missing,
        empty_values=empty_values,
        extra_keys=extra_keys,
        ok=ok,
    )

    global _LAST_REPORT
    _LAST_REPORT = report

    return report


def get_last_report() -> Optional[ValidationReport]:
    return _LAST_REPORT


def generate_docs_markdown(specs: List[EnvSpec]) -> str:
    lines = [
        "# Configuration",
        "",
        "| Name | Required | Default | Description |",
        "|------|----------|---------|-------------|",
    ]
    for spec in specs:
        required = "Yes" if spec.required else "No"
        default = spec.default or ""
        description = spec.description or ""
        lines.append(
            f"| {spec.key} | {required} | {default} | {description} |"
        )
    lines.append("")
    return "\n".join(lines)
