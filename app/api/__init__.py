from fastapi import APIRouter
from .api_v1 import router_v1
from app.core.config import settings

router = APIRouter(
    prefix=settings.api.prefix
)

router.include_router(router_v1)