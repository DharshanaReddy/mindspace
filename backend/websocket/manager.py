"""
WebSocket connection manager for real-time community feed updates.
Broadcasts new posts and replies to all connected clients instantly.
Tracks per-connection metadata and prunes stale connections on broadcast.
"""

from fastapi import WebSocket
import json
import time
import logging

logger = logging.getLogger(__name__)


class _Connection:
    """Wraps a WebSocket with connection metadata."""
    __slots__ = ("ws", "connected_at", "last_ping")

    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.connected_at: float = time.time()
        self.last_ping: float = time.time()


class ConnectionManager:
    def __init__(self):
        self._connections: list[_Connection] = []

    @property
    def active_connections(self) -> list[WebSocket]:
        return [c.ws for c in self._connections]

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._connections.append(_Connection(websocket))
        logger.info(f"WebSocket connected. Total: {len(self._connections)}")

    def disconnect(self, websocket: WebSocket):
        self._connections = [c for c in self._connections if c.ws is not websocket]
        logger.info(f"WebSocket disconnected. Total: {len(self._connections)}")

    def record_ping(self, websocket: WebSocket):
        for conn in self._connections:
            if conn.ws is websocket:
                conn.last_ping = time.time()
                break

    async def broadcast(self, event_type: str, data: dict):
        """Broadcast an event to all live connections; prune dead ones."""
        payload = json.dumps({"event": event_type, "data": data})
        dead: list[WebSocket] = []
        for conn in self._connections:
            try:
                await conn.ws.send_text(payload)
            except Exception:
                dead.append(conn.ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_to(self, websocket: WebSocket, event_type: str, data: dict):
        """Send an event to a specific client."""
        try:
            await websocket.send_text(json.dumps({"event": event_type, "data": data}))
        except Exception as e:
            logger.warning(f"Failed to send to client: {e}")
            self.disconnect(websocket)

    def connection_stats(self) -> dict:
        now = time.time()
        return {
            "total": len(self._connections),
            "avg_age_seconds": (
                round(sum(now - c.connected_at for c in self._connections) / len(self._connections))
                if self._connections else 0
            ),
        }

    @property
    def connection_count(self) -> int:
        return len(self._connections)


manager = ConnectionManager()
