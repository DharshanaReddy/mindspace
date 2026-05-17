"""
WebSocket connection manager for real-time community feed updates.
Broadcasts new posts and replies to all connected clients instantly.
"""

from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: dict):
        """Broadcast an event to all connected clients."""
        payload = json.dumps({"event": event_type, "data": data})
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead.append(connection)
        for c in dead:
            self.disconnect(c)

    async def send_to(self, websocket: WebSocket, event_type: str, data: dict):
        """Send an event to a specific client."""
        try:
            await websocket.send_text(json.dumps({"event": event_type, "data": data}))
        except Exception as e:
            logger.warning(f"Failed to send to client: {e}")
            self.disconnect(websocket)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()
