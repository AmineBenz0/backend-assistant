from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Literal
import os


available_webhooks = {
    "local": [
        {
            "url": os.environ.get("WEBHOOK_INTEGRATION", ""),
            "username": os.environ.get("WEBHOOK_USERNAME", ""),
            "password": os.environ.get("WEBHOOK_PASSWORD", ""),
        },
        {
            "url": os.environ.get("WEBHOOK_STAGE", ""),
            "username": os.environ.get("WEBHOOK_USERNAME", ""),
            "password": os.environ.get("WEBHOOK_PASSWORD", ""),
        },
        {
            "url": os.environ.get("WEBHOOK_TEST", ""),
            "username": os.environ.get("WEBHOOK_USERNAME", ""),
            "password": os.environ.get("WEBHOOK_PASSWORD", ""),
        },
    ],
    "develop": [
        {
            "url": os.environ.get("WEBHOOK_INTEGRATION", ""),
            "username": os.environ.get("WEBHOOK_USERNAME", ""),
            "password": os.environ.get("WEBHOOK_PASSWORD", ""),
        },
        {
            "url": os.environ.get("WEBHOOK_STAGE", ""),
            "username": os.environ.get("WEBHOOK_USERNAME", ""),
            "password": os.environ.get("WEBHOOK_PASSWORD", ""),
        },
        {
            "url": os.environ.get("WEBHOOK_TEST", ""),
            "username": os.environ.get("WEBHOOK_USERNAME", ""),
            "password": os.environ.get("WEBHOOK_PASSWORD", ""),
        },
    ],
    "production": [
        {
            "url": os.environ.get("WEBHOOK_PROD", ""),
            "username": os.environ.get("WEBHOOK_USERNAME", ""),
            "password": os.environ.get("WEBHOOK_PASSWORD", ""),
        }
    ],
}


class EnvironmentConfig(BaseModel):
    environment: Literal["local", "develop", "production"]


class Settings(BaseSettings):
    celery_broker_url: str = os.environ.get("CELERY_BROKER_URL", "redis://:smucks@redis:6379/0")
    _current_environment = EnvironmentConfig(environment=os.environ.get("ENVIRONMENT", "local"))
    webhooks: list = available_webhooks[_current_environment.environment]


settings = Settings()



