"""Конфигурация приложения через переменные окружения."""
import sys
import logging

from pydantic import AmqpDsn, PostgresDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """Настройки базы данных."""
    
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    
    @property
    def database_url(self) -> str:
        """URL для подключения к базе данных."""
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        ).unicode_string()
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class RabbitMQSettings(BaseSettings):
    """Настройки RabbitMQ."""
    
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_queue: str
    
    @property
    def rabbitmq_url(self) -> str:
        """URL для подключения к RabbitMQ."""
        return AmqpDsn.build(
            scheme="amqp",
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            username=self.rabbitmq_user,
            password=self.rabbitmq_password,
        ).unicode_string()
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ApplicationSettings(BaseSettings):
    """Настройки приложения."""
    
    app_name: str = "Task Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class LoggingSettings(BaseSettings):
    """Настройки логирования."""
    
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(
    DatabaseSettings,
    RabbitMQSettings,
    ApplicationSettings,
    LoggingSettings,
):
    """Объединенные настройки приложения."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


try:
    settings = Settings()
    logger.info("Settings loaded successfully")
except ValidationError as e:
    logger.error(f"Error loading settings, check .env file: {e}")
    sys.exit(1)
