from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    departments: str = "/departments"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class SqlalchemyConfig(BaseModel):
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class DatabaseConfig(BaseModel):
    username: str = "postgres"
    password: str = "postgres"
    database: str = "hitalent"
    host: str = "localhost"
    port: int = 5432
    driver_name: str = "postgresql+asyncpg"
    sqla: SqlalchemyConfig = SqlalchemyConfig()

    @property
    def async_url(self) -> URL:
        return URL.create(
            username=self.username,
            password=self.password,
            database=self.database,
            port=self.port,
            host=self.host,
            drivername=self.driver_name,
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig = DatabaseConfig()


settings = Settings()
