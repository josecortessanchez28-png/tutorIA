from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn
import base64
import json
import logging
from agent.llm_client import chat, chat_stream_async, transcribe_audio
from agent.prompts import SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if path.endswith(".js"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

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
    history = []
    try:
        while True:
            raw = await websocket.receive()
            if "bytes" in raw:
                continue
            elif "text" in raw:
                data = json.loads(raw["text"])
                msg_type = data.get("type", "text")

                if msg_type == "audio_data":
                    audio_bytes = base64.b64decode(data["data"])
                    fmt = data.get("format", "audio/webm")
                    logger.info(f"Audio base64: {len(data['data'])} chars -> {len(audio_bytes)} bytes, mime={fmt}")
                    if len(audio_bytes) < 5000:
                        await websocket.send_text(json.dumps({
                            "type": "transcribed",
                            "text": "[audio demasiado corto, habla un poco más]"
                        }))
                        continue
                    transcribed = transcribe_audio(audio_bytes, mime_type=fmt)
                    await websocket.send_text(json.dumps({"type": "transcribed", "text": transcribed}))
                    message = transcribed
                elif msg_type == "text":
                    message = data.get("message", "")
                else:
                    continue

                full_response = ""
                async for chunk in chat_stream_async(message, context=SYSTEM_PROMPT, history=history):
                    full_response += chunk
                    await websocket.send_text(json.dumps({"chunk": chunk}))
                await websocket.send_text(json.dumps({"done": True}))
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": full_response})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text(json.dumps({"error": str(e), "done": True}))
        except:
            pass

app.mount("/", NoCacheStaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
