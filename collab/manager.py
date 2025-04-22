# collab/manager.py
from typing import Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import time

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.connected_users: Dict[str, Dict[str, dict]] = {}

    async def connect(self, websocket: WebSocket, project_id: str, user_id: str):
        await websocket.accept()
        self.active_connections.setdefault(project_id, {})[user_id] = websocket
        self.connected_users.setdefault(project_id, {})

        await self.send_connected_users(project_id, user_id)
        print(f"[+] Conexión establecida: {user_id} en {project_id}")

    def disconnect(self, project_id: str, user_id: str):
        if user_id in self.active_connections.get(project_id, {}):
            self.active_connections[project_id].pop(user_id, None)
        if user_id in self.connected_users.get(project_id, {}):
            self.connected_users[project_id].pop(user_id, None)
        print(f"[-] Desconexión: {user_id} de {project_id}")

    async def broadcast(self, message: dict, project_id: str, exclude_user_id: Optional[str] = None):
        for user_id, ws in list(self.active_connections.get(project_id, {}).items()):
            if exclude_user_id and user_id == exclude_user_id:
                continue
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                print(f"[!] Error enviando a {user_id}: {e}")
                self.disconnect(project_id, user_id)

    async def send_connected_users(self, project_id: str, user_id: str):
        ws = self.active_connections[project_id].get(user_id)
        if not ws:
            return
        try:
            await ws.send_text(json.dumps({
                "type": "CONNECTED_USERS",
                "payload": list(self.connected_users[project_id].values())
            }))
        except Exception as e:
            print(f"[!] Error enviando lista a {user_id}: {e}")

    def update_user_info(self, project_id: str, user_id: str, info: dict):
        user = self.connected_users.setdefault(project_id, {}).setdefault(user_id, {})
        user.update(info)
        user["userId"] = user_id
        user["lastActive"] = info.get("lastActive", int(time.time() * 1000))
