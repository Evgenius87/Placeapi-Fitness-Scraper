from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    google_maps_api_key: str
    overpass_url: str
    nominatim_url: str

   

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()