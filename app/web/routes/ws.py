from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket import manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃，并可以接收客户端消息（如果有的话）
            # 目前主要用于服务器向客户端推送消息
            data = await websocket.receive_text()
            # 可以在这里处理客户端发送的消息，如果需要
    except WebSocketDisconnect:
        manager.disconnect(websocket)
