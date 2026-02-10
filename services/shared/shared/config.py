"""Task: T006 — Shared base configuration using Pydantic Settings.

Provides base settings for DAPR_HTTP_PORT, DATABASE_URL, SERVICE_NAME
that all microservices inherit from.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class BaseServiceConfig(BaseSettings):
    """Base configuration shared by all microservices.

    Environment variables are loaded automatically by Pydantic Settings.
    Each service subclasses this to add service-specific settings.
    """

    SERVICE_NAME: str = "unknown-service"
    DAPR_HTTP_PORT: int = 3500
    DAPR_GRPC_PORT: int = 50001
    DATABASE_URL: str = ""
    LOG_LEVEL: str = "INFO"

    model_config = {"env_prefix": "", "case_sensitive": True}
