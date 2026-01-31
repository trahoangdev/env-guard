from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.env import (
    DiffReport,
    DocsResponse,
    EnvVariableSpec,
    ValidationReport,
)
from app.db import report_store
from app.services import env_service

router = APIRouter()


@router.get("/status")
def status() -> dict:
    return {"service": "env-guard", "status": "ready"}


@router.post("/validate", response_model=ValidationReport)
async def validate_env(
    env_file: UploadFile = File(...),
    example_file: UploadFile | None = File(default=None),
) -> ValidationReport:
    env_bytes = await env_file.read()
    env_content = env_bytes.decode("utf-8-sig", errors="ignore")

    if example_file is None:
        try:
            with open(".env.example", "r", encoding="utf-8") as handle:
                example_content = handle.read()
        except OSError as exc:
            raise HTTPException(
                status_code=400,
                detail="example_file missing and .env.example not found",
            ) from exc
    else:
        example_bytes = await example_file.read()
        example_content = example_bytes.decode("utf-8-sig", errors="ignore")

    report = env_service.validate_env(example_content, env_content)
    report_store.save_validation_report(report)
    return ValidationReport(
        required_missing=[item.__dict__ for item in report.required_missing],
        empty_values=[item.__dict__ for item in report.empty_values],
        invalid_values=[item.__dict__ for item in report.invalid_values],
        extra_keys=[item.__dict__ for item in report.extra_keys],
        ok=report.ok,
    )


@router.get("/report", response_model=ValidationReport)
def get_report() -> ValidationReport:
    report = env_service.get_last_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No report available")
    return ValidationReport(
        required_missing=[item.__dict__ for item in report.required_missing],
        empty_values=[item.__dict__ for item in report.empty_values],
        invalid_values=[item.__dict__ for item in report.invalid_values],
        extra_keys=[item.__dict__ for item in report.extra_keys],
        ok=report.ok,
    )


@router.post("/diff", response_model=DiffReport)
async def diff_envs(
    base_env_file: UploadFile = File(...),
    compare_env_file: UploadFile = File(...),
) -> DiffReport:
    base_bytes = await base_env_file.read()
    compare_bytes = await compare_env_file.read()
    base_content = base_bytes.decode("utf-8-sig", errors="ignore")
    compare_content = compare_bytes.decode("utf-8-sig", errors="ignore")

    report = env_service.diff_envs(base_content, compare_content)
    report_store.save_diff_report(report)
    return DiffReport(
        missing_in_compare=[item.__dict__ for item in report.missing_in_compare],
        extra_in_compare=[item.__dict__ for item in report.extra_in_compare],
        different_values=[item.__dict__ for item in report.different_values],
        ok=report.ok,
    )


@router.get("/diff/report", response_model=DiffReport)
def get_diff_report() -> DiffReport:
    report = env_service.get_last_diff()
    if report is None:
        raise HTTPException(status_code=404, detail="No diff report available")
    return DiffReport(
        missing_in_compare=[item.__dict__ for item in report.missing_in_compare],
        extra_in_compare=[item.__dict__ for item in report.extra_in_compare],
        different_values=[item.__dict__ for item in report.different_values],
        ok=report.ok,
    )


@router.get("/history", response_model=list[dict])
def list_validation_history(limit: int = 20) -> list[dict]:
    return report_store.list_validation_reports(limit=limit)


@router.get("/history/{report_id}", response_model=dict)
def get_validation_history(report_id: int) -> dict:
    report = report_store.get_validation_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Validation report not found")
    return report


@router.get("/diff/history", response_model=list[dict])
def list_diff_history(limit: int = 20) -> list[dict]:
    return report_store.list_diff_reports(limit=limit)


@router.get("/diff/history/{report_id}", response_model=dict)
def get_diff_history(report_id: int) -> dict:
    report = report_store.get_diff_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Diff report not found")
    return report


@router.post("/docs", response_model=DocsResponse)
async def generate_docs(
    example_file: UploadFile | None = File(default=None),
) -> DocsResponse:
    if example_file is None:
        try:
            with open(".env.example", "r", encoding="utf-8") as handle:
                example_content = handle.read()
        except OSError as exc:
            raise HTTPException(
                status_code=400,
                detail="example_file missing and .env.example not found",
            ) from exc
    else:
        example_bytes = await example_file.read()
        example_content = example_bytes.decode("utf-8-sig", errors="ignore")

    specs = env_service.parse_env_example(example_content)
    markdown = env_service.generate_docs_markdown(specs)
    return DocsResponse(
        markdown=markdown,
        variables=[EnvVariableSpec(**spec.__dict__) for spec in specs],
    )
