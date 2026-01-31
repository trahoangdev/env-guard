from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EnvGuard"
    env: str = "local"
    log_level: str = "info"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
