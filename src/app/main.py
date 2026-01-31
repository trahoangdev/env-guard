from fastapi import FastAPI

from app.api.v1.router import api_router
from app.web.router import router as web_router

app = FastAPI(
    title="Env Guard",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(web_router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
