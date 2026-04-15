from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str  # used in token create
    JWT_ALGORITHM: str  # also used in there

    REDIS_HOST : str = "localhost"
    REDIS_PORT : int = 6379
    REDIS_URL: str = "redis://localhost:6379/0" #db=0 we did

    #smtp settings(konse email server se mail aya)
    MAIL_USERNAME : str
    MAIL_PASSWORD : str
    MAIL_SERVER : str
    MAIL_PORT : int
    MAIL_FROM : str
    MAIL_FROM_NAME : str
    MAIL_STARTTLS : bool = True
    MAIL_SSL_TLS : bool = False
    USE_CREDENTIALS : bool = True
    VALIDATE_CERTS: bool = True

    DOMAIN: str


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

Config = Settings()

# Celery configuration
broker_url = Config.REDIS_URL # just as told in the flow(broker=redis)
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True # Celery will retry connecting to the broker if it's initially unavailable.

