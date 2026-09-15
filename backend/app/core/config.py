from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore", env_ignore_empty=True)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    data_dir: Path = Field(default=ROOT / "data", validation_alias="FINQUANT_DATA_DIR")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="FINQUANT_CORS_ORIGINS",
    )


settings = Settings()
