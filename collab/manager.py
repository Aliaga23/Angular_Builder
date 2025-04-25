import json
import time
from typing import Dict, Optional
from fastapi import WebSocket
from .redis_sync import redis_sync

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.connected_users: Dict[str, Dict[str, dict]] = {}
        self.last_event_time: Dict[str, Dict[str, int]] = {}

    async def connect(self, websocket: WebSocket, project_id: str, user_id: str):
        await websocket.accept()
        self.active_connections.setdefault(project_id, {})[user_id] = websocket
        self.connected_users.setdefault(project_id, {})[user_id] = {"userId": user_id}

        await redis_sync.start_listener(project_id, self.send_to_user)
        await self.send_connected_users(project_id, user_id)
        await self.send_initial_state(project_id, user_id)

    async def disconnect(self, project_id: str, user_id: str):
        self.active_connections[project_id].pop(user_id, None)
        self.connected_users[project_id].pop(user_id, None)

        if not self.active_connections[project_id]:
            await redis_sync.clear_state(project_id)

        await redis_sync.broadcast({
            "type": "USER_DISCONNECTED",
            "userId": user_id,
            "timestamp": int(time.time() * 1000)
        }, project_id)

    async def handle_message(self, raw: str, project_id: str, user_id: str):
        try:
            message = json.loads(raw)
            message.setdefault("timestamp", int(time.time() * 1000))
            msg_type = message.get("type")

            if msg_type == "USER_CONNECTED":
                self.update_user_info(project_id, user_id, message["payload"], message["timestamp"])
                await redis_sync.broadcast({
                    "type": "USER_CONNECTED",
                    "userId": user_id,
                    "timestamp": message["timestamp"],
                    "payload": self.connected_users[project_id][user_id]
                }, project_id, exclude_user_id=user_id)

            elif msg_type == "CURSOR_POSITION":
                if self.should_throttle(project_id, user_id, msg_type, 3):
                    return
                self.update_user_info(project_id, user_id, {"cursorPosition": message["payload"]}, message["timestamp"])
                await redis_sync.broadcast(message, project_id, exclude_user_id=user_id)

            elif msg_type == "ACTIVE_COMPONENT":
                self.update_user_info(project_id, user_id, {"currentComponent": message["payload"].get("componentId")}, message["timestamp"])
                await redis_sync.broadcast(message, project_id, exclude_user_id=user_id)
            elif msg_type == "SAVE_PROJECT":
    # Guardar el estado completo si está presente en el mensaje
                if message.get("fullState"):
                    await redis_sync.set_state(project_id, message["fullState"])
                    print(f"[💾] Estado guardado para proyecto {project_id} por {user_id}")
            elif msg_type == "CANVAS_RESIZE":
                self.update_user_info(project_id, user_id, {"canvasSize": message["payload"]}, message["timestamp"])
                await redis_sync.broadcast(message, project_id, exclude_user_id=user_id)

    # Notificar a todos (excepto quien lo envió)
                await redis_sync.broadcast({
                    "type": "PROJECT_SAVED",
                    "userId": user_id,
                    "timestamp": message["timestamp"]
                }, project_id, exclude_user_id=user_id)

            else:
                await redis_sync.broadcast(message, project_id, exclude_user_id=user_id)

        except Exception as e:
            print(f"[!] Error procesando mensaje: {e}")

    def update_user_info(self, project_id: str, user_id: str, info: dict, ts: int):
        user = self.connected_users[project_id].setdefault(user_id, {"userId": user_id})
        user.update(info)
        user["lastActive"] = ts

    def should_throttle(self, project_id: str, user_id: str, event_type: str, interval_ms: int) -> bool:
        now = int(time.time() * 1000)
        key = f"{event_type}:{user_id}"
        proj = self.last_event_time.setdefault(project_id, {})
        if now - proj.get(key, 0) < interval_ms:
            return True
        proj[key] = now
        return False

    async def send_connected_users(self, project_id: str, user_id: str):
        ws = self.active_connections[project_id].get(user_id)
        if ws:
            await ws.send_text(json.dumps({
                "type": "CONNECTED_USERS",
                "payload": list(self.connected_users[project_id].values())
            }))

    async def send_initial_state(self, project_id: str, user_id: str):
        ws = self.active_connections[project_id].get(user_id)
        state = await redis_sync.get_state(project_id)
        if ws and state:
            await ws.send_text(json.dumps({
                "type": "INITIAL_STATE",
                "payload": state
            }))

    async def send_to_user(self, project_id: str, user_id: str, message: dict):
        ws = self.active_connections.get(project_id, {}).get(user_id)
        if ws:
            await ws.send_text(json.dumps(message))

connection_manager = ConnectionManager()
