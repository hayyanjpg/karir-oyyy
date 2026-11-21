from fastapi import APIRouter

from app.api.v1 import analytics, applications, auth, reports

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(applications.router)
api_router.include_router(analytics.router)
api_router.include_router(reports.router)
