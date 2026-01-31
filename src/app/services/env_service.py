from __future__ import annotations

from dataclasses import dataclass
import io
import re
from typing import Dict, Iterable, List, Optional

from dotenv import dotenv_values


@dataclass(frozen=True)
class EnvSpec:
    key: str
    default: str | None
    required: bool
    description: str | None
    value_type: str | None
    allowed: List[str] | None
    allowed_ci: bool | None
    pattern: str | None
    min_value: float | None
    max_value: float | None
    min_len: int | None
    max_len: int | None


@dataclass(frozen=True)
class ValidationIssue:
    key: str
    reason: str


@dataclass(frozen=True)
class ValidationReport:
    required_missing: List[ValidationIssue]
    empty_values: List[ValidationIssue]
    invalid_values: List[ValidationIssue]
    extra_keys: List[ValidationIssue]
    ok: bool


_LAST_REPORT: Optional[ValidationReport] = None
_LAST_DIFF: Optional["DiffReport"] = None


def _parse_comment(
    comment: str,
) -> tuple[
    str | None,
    str | None,
    List[str] | None,
    bool | None,
    str | None,
    float | None,
    float | None,
    int | None,
    int | None,
]:
    description_parts: List[str] = []
    value_type: str | None = None
    allowed: List[str] | None = None
    allowed_ci: bool | None = None
    pattern: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    min_len: int | None = None
    max_len: int | None = None

    for part in (p.strip() for p in comment.split("|")):
        if not part:
            continue
        if "=" in part:
            key, value = (piece.strip() for piece in part.split("=", 1))
            if key == "type":
                value_type = value
                continue
            if key == "allowed":
                allowed = [item.strip() for item in value.split(",") if item.strip()]
                continue
            if key == "allowed_ci":
                allowed_ci = value.lower() in {"true", "1", "yes"}
                continue
            if key == "pattern":
                pattern = value
                continue
            if key == "min":
                try:
                    min_value = float(value)
                except ValueError:
                    min_value = None
                continue
            if key == "max":
                try:
                    max_value = float(value)
                except ValueError:
                    max_value = None
                continue
            if key == "min_len":
                try:
                    min_len = int(value)
                except ValueError:
                    min_len = None
                continue
            if key == "max_len":
                try:
                    max_len = int(value)
                except ValueError:
                    max_len = None
                continue
        description_parts.append(part)

    description = " ".join(description_parts).strip() or None
    return (
        description,
        value_type,
        allowed,
        allowed_ci,
        pattern,
        min_value,
        max_value,
        min_len,
        max_len,
    )


def _parse_env_example_lines(lines: Iterable[str]) -> List[EnvSpec]:
    specs: List[EnvSpec] = []
    pending_desc: Optional[str] = None
    pending_type: Optional[str] = None
    pending_allowed: List[str] | None = None
    pending_allowed_ci: bool | None = None
    pending_pattern: Optional[str] = None
    pending_min: float | None = None
    pending_max: float | None = None
    pending_min_len: int | None = None
    pending_max_len: int | None = None

    for raw in lines:
        line = raw.strip()
        if not line:
            pending_desc = None
            continue
        if line.startswith("#"):
            comment = line.lstrip("#").strip()
            if comment:
                (
                    pending_desc,
                    pending_type,
                    pending_allowed,
                    pending_allowed_ci,
                    pending_pattern,
                    pending_min,
                    pending_max,
                    pending_min_len,
                    pending_max_len,
                ) = _parse_comment(comment)
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
                value_type=pending_type,
                allowed=pending_allowed,
                allowed_ci=pending_allowed_ci,
                pattern=pending_pattern,
                min_value=pending_min,
                max_value=pending_max,
                min_len=pending_min_len,
                max_len=pending_max_len,
            )
        )
        pending_desc = None
        pending_type = None
        pending_allowed = None
        pending_allowed_ci = None
        pending_pattern = None
        pending_min = None
        pending_max = None
        pending_min_len = None
        pending_max_len = None

    return specs


def parse_env_example(content: str) -> List[EnvSpec]:
    return _parse_env_example_lines(content.splitlines())


def parse_env(content: str) -> Dict[str, str]:
    stream = io.StringIO(content)
    return {k: v for k, v in dotenv_values(stream=stream).items() if k}


def validate_env(example_content: str, env_content: str) -> ValidationReport:
    specs = parse_env_example(example_content)
    env = parse_env(env_content)
    specs_by_key = {spec.key: spec for spec in specs}

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

    invalid_values: List[ValidationIssue] = []
    for key, value in env.items():
        if key not in specs_by_key:
            continue
        if value is None or str(value).strip() == "":
            continue
        spec = specs_by_key[key]
        if spec.value_type:
            raw_value = str(value)
            if spec.value_type == "int":
                if not re.fullmatch(r"[-+]?\d+", raw_value):
                    invalid_values.append(ValidationIssue(key=key, reason="invalid_type"))
                    continue
            elif spec.value_type == "float":
                try:
                    float(raw_value)
                except ValueError:
                    invalid_values.append(ValidationIssue(key=key, reason="invalid_type"))
                    continue
            elif spec.value_type == "bool":
                if raw_value.lower() not in {"true", "false", "1", "0"}:
                    invalid_values.append(ValidationIssue(key=key, reason="invalid_type"))
                    continue
        if spec.allowed:
            if spec.allowed_ci:
                if str(value).lower() not in {item.lower() for item in spec.allowed}:
                    invalid_values.append(
                        ValidationIssue(key=key, reason="invalid_allowed")
                    )
                    continue
            elif str(value) not in spec.allowed:
                invalid_values.append(ValidationIssue(key=key, reason="invalid_allowed"))
                continue
        if spec.pattern:
            if re.fullmatch(spec.pattern, str(value)) is None:
                invalid_values.append(ValidationIssue(key=key, reason="invalid_pattern"))
                continue
        if spec.min_len is not None or spec.max_len is not None:
            length = len(str(value))
            if spec.min_len is not None and length < spec.min_len:
                invalid_values.append(ValidationIssue(key=key, reason="min_len"))
                continue
            if spec.max_len is not None and length > spec.max_len:
                invalid_values.append(ValidationIssue(key=key, reason="max_len"))
                continue
        if spec.value_type in {"int", "float"} and (spec.min_value is not None or spec.max_value is not None):
            try:
                numeric = float(str(value))
            except ValueError:
                invalid_values.append(ValidationIssue(key=key, reason="invalid_type"))
                continue
            if spec.min_value is not None and numeric < spec.min_value:
                invalid_values.append(ValidationIssue(key=key, reason="min_value"))
                continue
            if spec.max_value is not None and numeric > spec.max_value:
                invalid_values.append(ValidationIssue(key=key, reason="max_value"))
                continue

    extra_keys = [
        ValidationIssue(key=key, reason="extra")
        for key in sorted(env.keys() - spec_keys)
    ]

    ok = not (required_missing or empty_values or invalid_values or extra_keys)
    report = ValidationReport(
        required_missing=required_missing,
        empty_values=empty_values,
        invalid_values=invalid_values,
        extra_keys=extra_keys,
        ok=ok,
    )

    global _LAST_REPORT
    _LAST_REPORT = report

    return report


def get_last_report() -> Optional[ValidationReport]:
    return _LAST_REPORT


@dataclass(frozen=True)
class DiffItem:
    key: str
    base_value: str | None
    compare_value: str | None


@dataclass(frozen=True)
class DiffReport:
    missing_in_compare: List[DiffItem]
    extra_in_compare: List[DiffItem]
    different_values: List[DiffItem]
    ok: bool


def diff_envs(base_content: str, compare_content: str) -> DiffReport:
    base_env = parse_env(base_content)
    compare_env = parse_env(compare_content)

    base_keys = set(base_env.keys())
    compare_keys = set(compare_env.keys())

    missing_in_compare = [
        DiffItem(key=key, base_value=base_env.get(key), compare_value=None)
        for key in sorted(base_keys - compare_keys)
    ]

    extra_in_compare = [
        DiffItem(key=key, base_value=None, compare_value=compare_env.get(key))
        for key in sorted(compare_keys - base_keys)
    ]

    different_values = []
    for key in sorted(base_keys & compare_keys):
        base_value = base_env.get(key)
        compare_value = compare_env.get(key)
        if str(base_value) != str(compare_value):
            different_values.append(
                DiffItem(
                    key=key,
                    base_value=base_value,
                    compare_value=compare_value,
                )
            )

    ok = not (missing_in_compare or extra_in_compare or different_values)
    report = DiffReport(
        missing_in_compare=missing_in_compare,
        extra_in_compare=extra_in_compare,
        different_values=different_values,
        ok=ok,
    )

    global _LAST_DIFF
    _LAST_DIFF = report
    return report


def get_last_diff() -> Optional[DiffReport]:
    return _LAST_DIFF


def generate_docs_markdown(specs: List[EnvSpec]) -> str:
    lines = [
        "# Configuration",
        "",
        "| Name | Required | Default | Description | Constraints |",
        "|------|----------|---------|-------------|-------------|",
    ]
    for spec in specs:
        required = "Yes" if spec.required else "No"
        default = spec.default or ""
        description = spec.description or ""
        constraints_parts: List[str] = []
        if spec.value_type:
            constraints_parts.append(f"type={spec.value_type}")
        if spec.allowed:
            constraints_parts.append(f"allowed={','.join(spec.allowed)}")
        if spec.allowed_ci:
            constraints_parts.append("allowed_ci=true")
        if spec.pattern:
            constraints_parts.append(f"pattern={spec.pattern}")
        if spec.min_value is not None:
            constraints_parts.append(f"min={spec.min_value:g}")
        if spec.max_value is not None:
            constraints_parts.append(f"max={spec.max_value:g}")
        if spec.min_len is not None:
            constraints_parts.append(f"min_len={spec.min_len}")
        if spec.max_len is not None:
            constraints_parts.append(f"max_len={spec.max_len}")
        constraints = "; ".join(constraints_parts)
        lines.append(
            f"| {spec.key} | {required} | {default} | {description} | {constraints} |"
        )
    lines.append("")
    return "\n".join(lines)
