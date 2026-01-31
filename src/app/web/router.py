from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.db import report_store
from app.schemas.env import DocsResponse, ValidationReport
from app.services import env_service

router = APIRouter()

_TEMPLATES = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent / "templates")
)


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


async def _read_optional_upload(file: UploadFile | None) -> Optional[str]:
    if file is None:
        return None
    return (await file.read()).decode("utf-8-sig", errors="ignore")


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return _TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "validation": None,
            "diff": None,
            "history": report_store.list_validation_reports(limit=5),
            "diff_history": report_store.list_diff_reports(limit=5),
        },
    )


@router.get("/docs", response_class=HTMLResponse)
def docs_page(request: Request) -> HTMLResponse:
    return _TEMPLATES.TemplateResponse(
        request,
        "docs.html",
        {"docs": None},
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
        "docs.html",
        {"docs": payload.model_dump()},
    )


@router.get("/history/{report_id}", response_class=HTMLResponse)
def validation_detail(request: Request, report_id: int) -> HTMLResponse:
    report = report_store.get_validation_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Validation report not found")
    return _TEMPLATES.TemplateResponse(
        request,
        "detail.html",
        {
            "title": f"Validation Report #{report_id}",
            "report": report,
            "back_href": "/",
            "download_href": f"/history/{report_id}/download",
        },
    )


@router.get("/history/{report_id}/download")
def validation_download(report_id: int) -> JSONResponse:
    report = report_store.get_validation_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Validation report not found")
    return JSONResponse(report)


@router.get("/diff-history/{report_id}", response_class=HTMLResponse)
def diff_detail(request: Request, report_id: int) -> HTMLResponse:
    report = report_store.get_diff_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Diff report not found")
    return _TEMPLATES.TemplateResponse(
        request,
        "detail.html",
        {
            "title": f"Diff Report #{report_id}",
            "report": report,
            "back_href": "/",
            "download_href": f"/diff-history/{report_id}/download",
        },
    )


@router.get("/diff-history/{report_id}/download")
def diff_download(report_id: int) -> JSONResponse:
    report = report_store.get_diff_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Diff report not found")
    return JSONResponse(report)
