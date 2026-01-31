from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class EnvVariableSpec(BaseModel):
    key: str
    default: Optional[str] = None
    required: bool
    description: Optional[str] = None
    value_type: Optional[str] = None
    allowed: Optional[List[str]] = None
    allowed_ci: Optional[bool] = None
    pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_len: Optional[int] = None
    max_len: Optional[int] = None


class ValidationIssue(BaseModel):
    key: str
    reason: str


class ValidationReport(BaseModel):
    required_missing: List[ValidationIssue]
    empty_values: List[ValidationIssue]
    invalid_values: List[ValidationIssue]
    extra_keys: List[ValidationIssue]
    ok: bool


class DocsResponse(BaseModel):
    markdown: str
    variables: List[EnvVariableSpec]


class DiffItem(BaseModel):
    key: str
    base_value: Optional[str] = None
    compare_value: Optional[str] = None


class DiffReport(BaseModel):
    missing_in_compare: List[DiffItem]
    extra_in_compare: List[DiffItem]
    different_values: List[DiffItem]
    ok: bool
