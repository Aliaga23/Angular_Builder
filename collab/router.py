# collab/router.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import ConnectionManager
import json
import asyncio
import time

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/{project_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str, user_id: str):
    await manager.connect(websocket, project_id, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message.setdefault("timestamp", int(time.time() * 1000))

            msg_type = message.get("type")

            if msg_type == "USER_CONNECTED":
                info = {
                    "username": message["payload"].get("username", f"User {user_id[:4]}"),
                    "color": message["payload"].get("color", "#3b82f6"),
                    "lastActive": message["timestamp"]
                }
                manager.update_user_info(project_id, user_id, info)
                await manager.broadcast({
                    "type": "USER_CONNECTED",
                    "userId": user_id,
                    "timestamp": message["timestamp"],
                    "payload": info
                }, project_id, exclude_user_id=user_id)

            elif msg_type == "CURSOR_POSITION":
                manager.update_user_info(project_id, user_id, {
                    "cursorPosition": message["payload"],
                    "lastActive": message["timestamp"]
                })
                await manager.broadcast(message, project_id, exclude_user_id=user_id)

            elif msg_type == "ACTIVE_COMPONENT":
                manager.update_user_info(project_id, user_id, {
                    "currentComponent": message["payload"].get("componentId"),
                    "lastActive": message["timestamp"]
                })
                await manager.broadcast(message, project_id, exclude_user_id=user_id)

            else:
                await manager.broadcast(message, project_id, exclude_user_id=user_id)

    except WebSocketDisconnect:
        manager.disconnect(project_id, user_id)
        await manager.broadcast({
            "type": "USER_DISCONNECTED",
            "userId": user_id,
            "timestamp": int(time.time() * 1000)
        }, project_id)
