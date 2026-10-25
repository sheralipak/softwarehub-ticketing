from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List

app = FastAPI(title="SoftwareHub Live Ticketing")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

class Task(BaseModel):
    title: str
    assigned_to: str
    status: str = "Pending"

@app.get("/")
def home():
    return {"status": "online", "system": "SoftwareHub Core Ticketing"}

@app.post("/tasks/")
async def create_task(task: Task):
    await manager.broadcast(f"Task Created: {task.title} -> {task.assigned_to}")
    return {"status": "created", "task": task}

@app.websocket("/ws/live-updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Report Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
