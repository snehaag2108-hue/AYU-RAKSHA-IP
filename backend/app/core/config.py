from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AYU-RAKSHA IP"
    database_url: str = "sqlite:///./ayu_raksha.db"
    jwt_secret: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 1440
    upload_dir: str = "uploads"
    report_dir: str = "reports"
    knowledge_dir: str = "data/knowledge"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
