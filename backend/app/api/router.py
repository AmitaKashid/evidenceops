from fastapi import APIRouter

from app.api.routes import dashboard, evaluations, health, tasks

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(tasks.router)
api_router.include_router(evaluations.router)
api_router.include_router(dashboard.router)
