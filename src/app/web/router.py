from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import report_store
from app.schemas.env import DocsResponse, ValidationReport
from app.services import env_service

router = APIRouter()

_TEMPLATES = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent / "templates")
)


async def _read_optional_upload(file: UploadFile | None) -> Optional[str]:
    if file is None:
        return None
    return (await file.read()).decode("utf-8-sig", errors="ignore")


def _read_example_fallback(content: Optional[str]) -> str:
    if content is not None:
        return content
    try:
        return Path(".env.example").read_text(encoding="utf-8")
    except OSError as exc:
        raise HTTPException(
            status_code=400,
            detail="example_file missing and .env.example not found",
        ) from exc


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return _TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "validation": None,
            "diff": None,
            "docs": None,
            "history": report_store.list_validation_reports(limit=5),
            "diff_history": report_store.list_diff_reports(limit=5),
        },
    )


@router.post("/validate-ui", response_class=HTMLResponse)
async def validate_ui(
    request: Request,
    env_file: UploadFile = File(...),
    example_file: UploadFile | None = File(default=None),
) -> HTMLResponse:
    env_content = (await env_file.read()).decode("utf-8-sig", errors="ignore")
    example_content = _read_example_fallback(await _read_optional_upload(example_file))
    report = env_service.validate_env(example_content, env_content)
    report_store.save_validation_report(report)
    payload = ValidationReport(
        required_missing=[item.__dict__ for item in report.required_missing],
        empty_values=[item.__dict__ for item in report.empty_values],
        invalid_values=[item.__dict__ for item in report.invalid_values],
        extra_keys=[item.__dict__ for item in report.extra_keys],
        ok=report.ok,
    )
    return _TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "validation": payload.model_dump(),
            "diff": None,
            "docs": None,
            "history": report_store.list_validation_reports(limit=5),
            "diff_history": report_store.list_diff_reports(limit=5),
        },
    )


@router.post("/diff-ui", response_class=HTMLResponse)
async def diff_ui(
    request: Request,
    base_env_file: UploadFile = File(...),
    compare_env_file: UploadFile = File(...),
) -> HTMLResponse:
    base_content = (await base_env_file.read()).decode("utf-8-sig", errors="ignore")
    compare_content = (await compare_env_file.read()).decode(
        "utf-8-sig", errors="ignore"
    )
    report = env_service.diff_envs(base_content, compare_content)
    report_store.save_diff_report(report)
    payload = {
        "missing_in_compare": [item.__dict__ for item in report.missing_in_compare],
        "extra_in_compare": [item.__dict__ for item in report.extra_in_compare],
        "different_values": [item.__dict__ for item in report.different_values],
        "ok": report.ok,
    }
    return _TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "validation": None,
            "diff": payload,
            "docs": None,
            "history": report_store.list_validation_reports(limit=5),
            "diff_history": report_store.list_diff_reports(limit=5),
        },
    )


@router.post("/docs-ui", response_class=HTMLResponse)
async def docs_ui(
    request: Request,
    example_file: UploadFile | None = File(default=None),
) -> HTMLResponse:
    example_content = _read_example_fallback(await _read_optional_upload(example_file))
    specs = env_service.parse_env_example(example_content)
    markdown = env_service.generate_docs_markdown(specs)
    payload = DocsResponse(
        markdown=markdown,
        variables=[spec.__dict__ for spec in specs],
    )
    return _TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "validation": None,
            "diff": None,
            "docs": payload.model_dump(),
            "history": report_store.list_validation_reports(limit=5),
            "diff_history": report_store.list_diff_reports(limit=5),
        },
    )
