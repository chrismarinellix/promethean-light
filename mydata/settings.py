from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    watch_directories: list[str] = [str(Path.home() / "Documents"), str(Path.home() / "Downloads")]
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    ml_loop_interval_seconds: int = 300
    mac_outlook_poll_interval: int = 60
    mac_outlook_days_back: int = 30
    win_outlook_history_hours: int = 1440
    win_outlook_watch_sent: bool = True


settings = Settings()
