from pydantic_settings import BaseSettings, SettingsConfigDict

class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    BOT_TOKEN: str
    API_BASE_URL: str = "http://api:8000/api/v1"

bot_settings = BotSettings()