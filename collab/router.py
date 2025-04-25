from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import connection_manager

router = APIRouter()

@router.websocket("/ws/{project_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str, user_id: str):
    await connection_manager.connect(websocket, project_id, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.handle_message(data, project_id, user_id)
    except WebSocketDisconnect:
        await connection_manager.disconnect(project_id, user_id)
