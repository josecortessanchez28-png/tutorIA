from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn
import json
import logging
from agent.llm_client import chat, chat_stream_async
from agent.prompts import SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TutorIA", version="0.1.0")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    response = chat(req.message, context=SYSTEM_PROMPT)
    return {"response": response}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            message = msg.get("message", "")
            async for chunk in chat_stream_async(message, context=SYSTEM_PROMPT):
                await websocket.send_text(json.dumps({"chunk": chunk}))
            await websocket.send_text(json.dumps({"done": True}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text(json.dumps({"error": str(e), "done": True}))
        except:
            pass

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
