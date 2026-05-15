from fastapi import APIRouter

from app.core.config import settings
from .departments import router as departments_router

router_v1 = APIRouter(prefix=settings.api.v1.prefix)

router_v1.include_router(router=departments_router)
