"""Task: T021 — WebSocket Service configuration.

Service-specific settings: PORT=8003, SERVICE_NAME=websocket-service.
No DB — stateless service that uses Dapr State Store.
"""

from __future__ import annotations

from shared.config import BaseServiceConfig


class WebSocketServiceConfig(BaseServiceConfig):
    """WebSocket Service specific configuration."""

    SERVICE_NAME: str = "websocket-service"
    PORT: int = 8003


settings = WebSocketServiceConfig()
