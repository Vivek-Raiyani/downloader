from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # General
    DOWNLOAD_DIR: str = "downloads"
    S3_ENABLED: bool = False

    # S3 Configuration
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET_NAME: str | None = None
    S3_REGION: str = "us-east-1"

    # API Configuration
    DEBUG: bool = True
    PORT: int = 8000

    # Cleanup Configuration
    CLEANUP_INTERVAL_SECONDS: int = 60  # How often to run the cleanup job
    FILE_RETENTION_SECONDS: int = 60    # How long to keep files before deleting

    # FFmpeg Configuration
    FFMPEG_PATH: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure download directory exists
Path(settings.DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
