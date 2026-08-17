from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://learnflow:learnflow@localhost:5432/learnflow"

    # JWT
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "learnflow"
    jwt_audience: str = "learnflow-api"
    access_token_ttl_min: int = 15
    refresh_token_ttl_days: int = 7
    clock_skew_leeway_sec: int = 60

    # Verification / reset tokens
    verify_token_ttl_hours: int = 24
    reset_token_ttl_min: int = 30

    # Lockout / rate limiting
    lockout_threshold: int = 5
    lockout_minutes: int = 15
    login_rate_limit: str = "20/minute"
    register_rate_limit: str = "10/minute"
    forgot_password_rate_limit: str = "10/minute"
    resend_verification_max_per_hour: int = 3

    # Password policy
    password_min_length: int = 10
    password_max_length: int = 128

    # SMTP
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "LearnFlow <no-reply@learnflow.local>"
    smtp_use_tls: bool = True
    smtp_timeout_sec: int = 10

    # App
    frontend_base_url: str = "http://localhost:5173"
    cors_origins: list[str] = ["http://localhost:5173"]
    environment: str = "development"

    # LMS
    default_passing_score: int = 70
    certificates_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
