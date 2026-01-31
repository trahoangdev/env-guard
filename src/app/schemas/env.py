from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class EnvVariableSpec(BaseModel):
    key: str
    default: Optional[str] = None
    required: bool
    description: Optional[str] = None


class ValidationIssue(BaseModel):
    key: str
    reason: str


class ValidationReport(BaseModel):
    required_missing: List[ValidationIssue]
    empty_values: List[ValidationIssue]
    extra_keys: List[ValidationIssue]
    ok: bool


class DocsResponse(BaseModel):
    markdown: str
    variables: List[EnvVariableSpec]
