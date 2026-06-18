from pydantic_settings import BaseSettings, SettingsConfigDict

class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    BOT_TOKEN: str
    API_BASE_URL: str = "http://api:8000/api/v1"
    MEDIA_BASE_URL: str = "http://api:8000"  # для построения URL медиафайлов
    BOT_API_EMAIL: str    # email технического бота для авторизации на API
    BOT_API_PASSWORD: str

bot_settings = BotSettings()