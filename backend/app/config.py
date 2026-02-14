from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ping_parking"

    # Auth
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours
    jwt_remember_me_expire_minutes: int = 10080  # 7 days

    # Encryption (Fernet key for license plates)
    encryption_key: str = "1tGkwxGdZgqzWY8sF0C--shdR3n8_PqAJkreObb--tU="  # dev default

    # App
    debug: bool = False
    app_name: str = "Ping Parking API"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
