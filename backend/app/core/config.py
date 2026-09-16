from pathlib import Path
from tempfile import gettempdir

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore", env_ignore_empty=True)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    data_dir: Path = Field(default=ROOT / "data", validation_alias="FINQUANT_DATA_DIR")
    vercel: bool = False
    persistence_enabled: bool = Field(default=True, validation_alias="FINQUANT_PERSISTENCE_ENABLED")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="FINQUANT_CORS_ORIGINS",
    )

    @model_validator(mode="after")
    def serverless_storage(self):
        if self.vercel:
            # Vercel's deployment filesystem is read-only; /tmp is ephemeral.
            self.data_dir = Path(gettempdir()) / "finquant-ai"
            self.persistence_enabled = False
        return self


settings = Settings()
