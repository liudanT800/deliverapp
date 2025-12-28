from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    project_name: str = "顺路带 API"
    api_prefix: str = "/api"
    
    # 根据环境变量决定使用哪种数据库
    database_url: str = (
        os.getenv("DATABASE_URL") or
        ("sqlite+aiosqlite:///./test.db" if os.getenv("ENV") == "development" 
         else "mysql+aiomysql://deliverapp:deliverapp@localhost:3306/deliverapp")
    )
    echo_sql: bool = False

    secret_key: str = "CHANGE_ME"
    access_token_expire_minutes: int = 60 * 24
    jwt_algorithm: str = "HS256"

    cors_origins: list[str] = ["*"]

    @computed_field(return_type=str)
    def frontend_url(self) -> str:
        return self.cors_origins[0]


settings = Settings()