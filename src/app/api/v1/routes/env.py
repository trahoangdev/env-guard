from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.env import DocsResponse, EnvVariableSpec, ValidationReport
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
    return ValidationReport(
        required_missing=report.required_missing,
        empty_values=report.empty_values,
        extra_keys=report.extra_keys,
        ok=report.ok,
    )


@router.get("/report", response_model=ValidationReport)
def get_report() -> ValidationReport:
    report = env_service.get_last_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No report available")
    return ValidationReport(
        required_missing=report.required_missing,
        empty_values=report.empty_values,
        extra_keys=report.extra_keys,
        ok=report.ok,
    )


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
