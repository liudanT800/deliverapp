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

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:4174",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:9000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
        "http://127.0.0.1:4174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:9000"
    ]
    
    # 高德地图Web服务API密钥
    amap_web_service_key: str = "CHANGE_ME"

    @computed_field(return_type=str)
    def frontend_url(self) -> str:
        return self.cors_origins[0]


settings = Settings()