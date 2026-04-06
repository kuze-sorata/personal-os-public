from functools import lru_cache

from pydantic import Field
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    notion_api_key: str = Field(default="")
    notion_task_db_id: str = Field(default="")
    notion_idea_db_id: str = Field(default="")
    notion_daily_log_db_id: str = Field(default="")

    google_client_id: str = Field(default="")
    google_client_secret: str = Field(default="")
    google_refresh_token: str = Field(default="")
    google_calendar_id: str = Field(default="primary")

    telegram_bot_token: str = Field(default="")
    telegram_chat_id: str = Field(default="")
    use_mock_data: bool = Field(default=True)
    mock_today_date: str = Field(default="2026-04-05")
    mock_data_dir: str = Field(default="mock_data")

    day_start: str = Field(default="08:00")
    day_end: str = Field(default="22:00")
    min_block_minutes: int = Field(default=20)
    buffer_minutes: int = Field(default=15)
    timezone: str = Field(default="Asia/Tokyo")

    @model_validator(mode="after")
    def validate_public_demo_safety(self) -> "Settings":
        if not self.use_mock_data:
            raise ValueError("public-demo requires USE_MOCK_DATA=true")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
