from typing import List, Dict, Any
from fastapi import WebSocket

class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 活跃连接列表
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """处理新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """处理断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """广播消息给所有连接"""
        # 复制列表以避免在迭代时修改
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except Exception:
                # 如果发送失败，假设连接已断开
                self.disconnect(connection)

# 全局单例
manager = ConnectionManager()
