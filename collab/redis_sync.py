import json
from typing import Callable, Optional
from db.redis import redis_client

CHANNEL_PREFIX = "project"

class RedisSync:
    def __init__(self):
        self.listeners = {}

    async def start_listener(self, project_id: str, callback: Callable):
        if project_id in self.listeners:
            return  # ya está escuchando

        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"{CHANNEL_PREFIX}:{project_id}")

        async def listener():
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    data = json.loads(msg["data"])
                    for user_id in callback.__self__.active_connections[project_id]:
                        if data.get("userId") != user_id:
                            await callback(project_id, user_id, data)

        self.listeners[project_id] = listener
        import asyncio
        asyncio.create_task(listener())

    async def broadcast(self, message: dict, project_id: str, exclude_user_id: Optional[str] = None):
        await redis_client.publish(f"{CHANNEL_PREFIX}:{project_id}", json.dumps(message))

        if message["type"] in {
            "ADD_COMPONENT", "UPDATE_COMPONENT", "REMOVE_COMPONENT", "MOVE_COMPONENT",
            "ADD_PAGE", "REMOVE_PAGE", "UPDATE_PAGE"
        } and message.get("fullState"):
            await self.set_state(project_id, message["fullState"])

    async def set_state(self, project_id: str, state: dict):
        key = f"{CHANNEL_PREFIX}:{project_id}:state"
        await redis_client.set(key, json.dumps(state), ex=3600)
        print(f"[✅ Redis] Guardado con éxito: {key}")
    async def get_state(self, project_id: str) -> Optional[dict]:
        key = f"{CHANNEL_PREFIX}:{project_id}:state"
        raw = await redis_client.get(key)
        if raw:
            print(f"[🔍 Redis] Se encontró estado guardado en {key}")
            return json.loads(raw)
        print(f"[❌ Redis] No se encontró estado guardado en {key}")
        return None

    async def clear_state(self, project_id: str):
        await redis_client.delete(f"{CHANNEL_PREFIX}:{project_id}:state")

redis_sync = RedisSync()
