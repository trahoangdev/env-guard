from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.services import env_service


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Failed to read {path}: {exc}") from exc


def _cmd_validate(args: argparse.Namespace) -> int:
    example_content = _read_file(Path(args.example))
    env_content = _read_file(Path(args.env))
    report = env_service.validate_env(example_content, env_content)
    payload = {
        "ok": report.ok,
        "required_missing": [item.__dict__ for item in report.required_missing],
        "empty_values": [item.__dict__ for item in report.empty_values],
        "invalid_values": [item.__dict__ for item in report.invalid_values],
        "extra_keys": [item.__dict__ for item in report.extra_keys],
    }
    print(json.dumps(payload, indent=2))
    return 0 if report.ok else 2


def _cmd_docs(args: argparse.Namespace) -> int:
    example_content = _read_file(Path(args.example))
    specs = env_service.parse_env_example(example_content)
    markdown = env_service.generate_docs_markdown(specs)
    output = Path(args.out)
    output.write_text(markdown, encoding="utf-8")
    print(f"Wrote {output}")
    return 0


def _cmd_diff(args: argparse.Namespace) -> int:
    base_content = _read_file(Path(args.base))
    compare_content = _read_file(Path(args.compare))
    report = env_service.diff_envs(base_content, compare_content)
    payload = {
        "ok": report.ok,
        "missing_in_compare": [item.__dict__ for item in report.missing_in_compare],
        "extra_in_compare": [item.__dict__ for item in report.extra_in_compare],
        "different_values": [item.__dict__ for item in report.different_values],
    }
    print(json.dumps(payload, indent=2))
    return 0 if report.ok else 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envguard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate .env vs .env.example"
    )
    validate_parser.add_argument("--example", required=True, help="Path to .env.example")
    validate_parser.add_argument("--env", required=True, help="Path to .env")
    validate_parser.set_defaults(func=_cmd_validate)

    docs_parser = subparsers.add_parser(
        "docs", help="Generate docs/config.md from .env.example"
    )
    docs_parser.add_argument("--example", required=True, help="Path to .env.example")
    docs_parser.add_argument("--out", required=True, help="Output markdown file")
    docs_parser.set_defaults(func=_cmd_docs)

    diff_parser = subparsers.add_parser("diff", help="Diff two .env files")
    diff_parser.add_argument("--base", required=True, help="Base .env file")
    diff_parser.add_argument("--compare", required=True, help="Compare .env file")
    diff_parser.set_defaults(func=_cmd_diff)

    return parser


def run() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    return args.func(args)


def main() -> None:
    raise SystemExit(run())
