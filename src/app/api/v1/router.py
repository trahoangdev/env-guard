from fastapi import APIRouter

from app.api.v1.routes.env import router as env_router

api_router = APIRouter()
api_router.include_router(env_router, prefix="/env", tags=["env"])
