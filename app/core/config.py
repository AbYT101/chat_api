from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class Settings(BaseSettings):
    app_name: str = "Chat API"
    admin_email: str = "aberhamyirsaw@gmail.com"
    environment: str = "development"

    # DB
    db_user: str
    db_password: str
    db_host: str
    db_port: int = 5432
    db_name: str

    db_echo: bool = True

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def database_url(self) -> str:
        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        host = self.db_host
        return f"postgresql+asyncpg://{user}:{password}@{host}:{self.db_port}/{self.db_name}"
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
