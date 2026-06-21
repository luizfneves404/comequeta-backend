"""In-process WebSocket connection manager.

Maps ``user_id`` to the set of currently open WebSocket connections for that
user, enabling delivery of chat messages to every device a user has online.

This is a single-process, in-memory registry: it is intentionally simple and
suits the MVP. Scaling to multiple workers would require an external pub/sub
(e.g. Redis), which is out of scope here.
"""

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        sockets = self._connections.get(user_id)
        if sockets is None:
            return
        sockets.discard(websocket)
        if not sockets:
            del self._connections[user_id]

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        """Deliver a JSON payload to every open socket of ``user_id``."""
        for websocket in list(self._connections.get(user_id, set())):
            try:
                await websocket.send_json(payload)
            except Exception:  # noqa: BLE001 - drop dead sockets silently
                self.disconnect(user_id, websocket)


# Module-level singleton shared by REST routes and the WebSocket endpoint.
manager = ConnectionManager()
