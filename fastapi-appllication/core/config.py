from pydantic_settings import BaseSettings
from pydantic import BaseModel

class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: str = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()


settings = Settings()