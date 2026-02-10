"""Task: T046 — WebSocket connection manager.

ConnectionManager class: connect, disconnect, broadcast methods.
Tracks active connections. Handles graceful disconnection.
"""

from __future__ import annotations

import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts messages."""

    def __init__(self) -> None:
        self._active_connections: list[WebSocket] = []

    @property
    def active_count(self) -> int:
        """Return number of active connections."""
        return len(self._active_connections)

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self._active_connections.append(websocket)
        logger.info(
            "WebSocket connected. Active connections: %d", self.active_count
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from the active list."""
        if websocket in self._active_connections:
            self._active_connections.remove(websocket)
        logger.info(
            "WebSocket disconnected. Active connections: %d", self.active_count
        )

    async def broadcast(self, message: dict) -> None:
        """Broadcast a JSON message to all active connections.

        Disconnects clients that fail to receive the message.
        """
        stale: list[WebSocket] = []
        for connection in self._active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                logger.warning("Failed to send to client, marking as stale")
                stale.append(connection)

        for connection in stale:
            self.disconnect(connection)

        if self._active_connections:
            logger.info(
                "Broadcast sent to %d clients",
                len(self._active_connections),
            )


manager = ConnectionManager()
