from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.models import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()


def create_app() -> FastAPI:
    return FastAPI(
        title="HiTalent Org Structure API",
        description=(
            "REST API for managing a hierarchical department structure "
            "and employees."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )
