from typing import Dict, Optional
from fastapi import WebSocket
import json
import asyncio
import time
from db.redis import redis_client

CHANNEL_PREFIX = "project:"


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.connected_users: Dict[str, Dict[str, dict]] = {}

    async def connect(self, websocket: WebSocket, project_id: str, user_id: str):
        await websocket.accept()
        self.active_connections.setdefault(project_id, {})[user_id] = websocket
        self.connected_users.setdefault(project_id, {})

        # Escuchar cambios desde Redis
        asyncio.create_task(self.redis_listener(project_id, user_id))

        # Enviar estado inicial y usuarios conectados
        await self.send_connected_users(project_id, user_id)
        await self.send_initial_state(project_id, user_id)

        print(f"[+] Conexión establecida: {user_id} en {project_id}")

    def disconnect(self, project_id: str, user_id: str):
        self.active_connections.get(project_id, {}).pop(user_id, None)
        self.connected_users.get(project_id, {}).pop(user_id, None)

        print(f"[-] Desconexión: {user_id} de {project_id}")

        # Si ya no hay nadie conectado, limpiar estado del proyecto
        if not self.active_connections.get(project_id):
            asyncio.create_task(redis_client.delete(f"{CHANNEL_PREFIX}{project_id}:state"))

    async def broadcast(self, message: dict, project_id: str, exclude_user_id: Optional[str] = None):
        await redis_client.publish(f"{CHANNEL_PREFIX}{project_id}", json.dumps(message))

        # Actualizar estado si corresponde
        if message["type"] in {
            "ADD_COMPONENT", "UPDATE_COMPONENT", "REMOVE_COMPONENT", "MOVE_COMPONENT",
            "ADD_PAGE", "REMOVE_PAGE", "UPDATE_PAGE"
        } and message.get("fullState"):
            await self.update_project_state(project_id, message["fullState"])

    async def update_project_state(self, project_id: str, new_state: dict):
        key = f"{CHANNEL_PREFIX}{project_id}:state"
        await redis_client.set(key, json.dumps(new_state), ex=3600)  # 1h TTL

    async def redis_listener(self, project_id: str, user_id: str):
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"{CHANNEL_PREFIX}{project_id}")

        async for msg in pubsub.listen():
            if msg["type"] == "message":
                try:
                    data = json.loads(msg["data"])
                    if data.get("userId") == user_id:
                        continue
                    ws = self.active_connections[project_id].get(user_id)
                    if ws:
                        await ws.send_text(json.dumps(data))
                except Exception as e:
                    print(f"[!] Error reenviando desde Redis a {user_id}: {e}")
                    break

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

    async def send_initial_state(self, project_id: str, user_id: str):
        ws = self.active_connections[project_id].get(user_id)
        if not ws:
            return
        try:
            raw_state = await redis_client.get(f"{CHANNEL_PREFIX}{project_id}:state")
            if raw_state:
                await ws.send_text(json.dumps({
                    "type": "INITIAL_STATE",
                    "payload": json.loads(raw_state)
                }))
        except Exception as e:
            print(f"[!] Error enviando INITIAL_STATE a {user_id}: {e}")

    def update_user_info(self, project_id: str, user_id: str, info: dict):
        user = self.connected_users.setdefault(project_id, {}).setdefault(user_id, {})
        user.update(info)
        user["userId"] = user_id
        user["lastActive"] = info.get("lastActive", int(time.time() * 1000))
