import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def check_connection() -> bool:
    engine = create_async_engine(
        str(settings.db.async_url.render_as_string(hide_password=False)),
        pool_pre_ping=True,
    )
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(check_connection()) else 1)
