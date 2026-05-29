from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    BOT_TOKEN: str | None = None
    ADMIN_ID: int | None = None
    REDIS_HOST: str | None = None
    REDIS_PORT: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_USERNAME: str | None = None
    DB_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env",
    )


print(f"Загрузка конфигурации из: {BASE_DIR}/.env")


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
