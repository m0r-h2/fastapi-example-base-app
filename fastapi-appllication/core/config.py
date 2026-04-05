from pydantic_settings import BaseSettings
from pydantic import BaseModel
from sqlalchemy import URL

class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: str = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class SqlalchemyConfig(BaseModel):
    echo: bool = True
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10

class DatabaseConfig(BaseModel):
    username: str = "user"
    password: str = "password"
    database: str ="shop"
    port: int = 5432
    host: str = "db"
    driver_name: str = "postgresql+asyncpg"
    @property
    def async_url(self) -> URL:
        return URL.create(
            username=self.username,
            password=self.password,
            database=self.database,
            port=self.port,
            host=self.host,
            drivername=self.driver_name
        )

    sqla: SqlalchemyConfig = SqlalchemyConfig()





class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig = DatabaseConfig()


settings = Settings()