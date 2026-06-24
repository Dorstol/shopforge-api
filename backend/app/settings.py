from functools import lru_cache

from pydantic_settings import BaseSettings


class JWTSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_LIFETIME_MINUTES: int = 5
    REFRESH_TOKEN_LIFETIME_MINUTES: int = 60


class BetterStackSettings(BaseSettings):
    BETTER_STACK_TOKEN: str
    BETTER_STACK_HOST: str


class SentrySettings(BaseSettings):
    SENTRY_DSN: str


class CoreSettings(BaseSettings):
    APP_NAME: str = "Title"
    DEBUG: bool = False


class PostgreSQLSettings(BaseSettings):
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    PGPORT: int = 5432

    @property
    def database_async_url(self) -> str:
        return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str = "default"
    REDIS_PASSWORD: str
    REDIS_DATABASE: int = 0


class S3Storage(BaseSettings):
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_PUBLIC_URL: str
    S3_REGION: str
    S3_BUCKET: str


class PaymentSettings(BaseSettings):
    STRIPE_SECRET_KEY: str


class Settings(
    CoreSettings,
    PostgreSQLSettings,
    SentrySettings,
    BetterStackSettings,
    JWTSettings,
    RedisSettings,
    S3Storage,
    PaymentSettings,
):
    pass


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
